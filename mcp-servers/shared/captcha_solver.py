"""Resolución de CAPTCHA opt-in vía servicio externo (2captcha, API createTask).

Apagado por defecto: sin `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`,
`solver_activo()` es False y los MCPs devuelven handoff humano como antes.

Soporta:
- Imagen (ImageToTextTask) con LLM de visión de respaldo opcional (ANTHROPIC_API_KEY).
- reCAPTCHA v2 / v2 Enterprise / v3, hCaptcha y Turnstile por token.

Doc 2captcha: https://2captcha.com/api-docs (createTask / getTaskResult).
Excluidos a propósito: apartado de citas (mp_citas_monitor) y portales con anti-bot
deliberado (REPEP): ver `PORTALES_EXCLUIDOS`.
"""

from __future__ import annotations

import base64
import os
import re
import time
from typing import Any, Callable, TypeVar

import httpx

from shared.errors import ConfigError, UpstreamError

API = "https://api.2captcha.com"
POLL_S = 5.0
TIMEOUT_S = 180.0
# Errores de cuenta: no tiene caso reintentar.
ERRORES_FATALES = {
    "ERROR_KEY_DOES_NOT_EXIST", "ERROR_ZERO_BALANCE", "ERROR_IP_NOT_ALLOWED",
    "ERROR_ACCOUNT_SUSPENDED", "ERROR_WRONG_USER_KEY",
}
PORTALES_EXCLUIDOS = {"citas_monitor", "repep_profeco"}


def solver_activo(portal: str | None = None) -> bool:
    if portal in PORTALES_EXCLUIDOS:
        return False
    return (
        os.environ.get("PLUGINS_MX_CAPTCHA_SOLVER", "").strip().lower() == "2captcha"
        and bool(os.environ.get("TWOCAPTCHA_API_KEY", "").strip())
    )


class CaptchaSolver:
    def __init__(self, http: httpx.Client | None = None, poll_s: float = POLL_S, timeout_s: float = TIMEOUT_S) -> None:
        self.key = os.environ.get("TWOCAPTCHA_API_KEY", "").strip()
        if not self.key:
            raise ConfigError("Falta TWOCAPTCHA_API_KEY para resolver CAPTCHA.")
        self._http = http or httpx.Client(timeout=30)
        self.poll_s, self.timeout_s = poll_s, timeout_s

    def _post(self, ruta: str, body: dict[str, Any]) -> dict[str, Any]:
        try:
            r = self._http.post(f"{API}/{ruta}", json={"clientKey": self.key, **body})
            r.raise_for_status()
        except httpx.HTTPError as exc:
            raise UpstreamError(f"2captcha no respondió: {type(exc).__name__}") from exc
        data = r.json()
        if data.get("errorId"):
            codigo = data.get("errorCode", "ERROR_DESCONOCIDO")
            cls = ConfigError if codigo in ERRORES_FATALES else UpstreamError
            raise cls(f"2captcha: {codigo}", {"error_code": codigo})
        return data

    def resolver(self, task: dict[str, Any]) -> dict[str, Any]:
        """Crea la tarea y espera la solución. Devuelve el dict `solution` de 2captcha."""
        task_id = self._post("createTask", {"task": task})["taskId"]
        limite = time.monotonic() + self.timeout_s
        while time.monotonic() < limite:
            time.sleep(self.poll_s)
            r = self._post("getTaskResult", {"taskId": task_id})
            if r.get("status") == "ready":
                return r["solution"]
        raise UpstreamError("2captcha no resolvió a tiempo", {"task_id": task_id})

    # ---------- atajos por tipo ----------

    def imagen(self, png: bytes, min_len: int = 4, max_len: int = 0) -> str:
        """Texto de un captcha de imagen. Si 2captcha falla y hay ANTHROPIC_API_KEY, usa visión de respaldo."""
        try:
            texto = self.resolver({
                "type": "ImageToTextTask",
                "body": base64.b64encode(png).decode(),
                "minLength": min_len,
                "maxLength": max_len,
            })["text"]
        except UpstreamError:
            texto = _vision_respaldo(png)
        texto = re.sub(r"[^A-Za-z0-9]", "", texto or "")
        if len(texto) < min_len:
            raise UpstreamError("Respuesta de captcha de imagen inválida", {"largo": len(texto)})
        return texto

    def recaptcha(
        self, sitekey: str, url: str, version: str = "v2", accion: str | None = None,
        min_score: float = 0.7, enterprise: bool = False,
    ) -> str:
        """Token para `g-recaptcha-response`."""
        if version == "v3":
            task = {"type": "RecaptchaV3TaskProxyless", "websiteURL": url, "websiteKey": sitekey,
                    "minScore": min_score, "pageAction": accion or "verify", "isEnterprise": enterprise}
        else:
            tipo = "RecaptchaV2EnterpriseTaskProxyless" if enterprise else "RecaptchaV2TaskProxyless"
            task = {"type": tipo, "websiteURL": url, "websiteKey": sitekey}
        return self.resolver(task)["gRecaptchaResponse"]

    def hcaptcha(self, sitekey: str, url: str) -> str:
        return self.resolver({"type": "HCaptchaTaskProxyless", "websiteURL": url, "websiteKey": sitekey})["gRecaptchaResponse"]

    def turnstile(self, sitekey: str, url: str, accion: str | None = None) -> str:
        task = {"type": "TurnstileTaskProxyless", "websiteURL": url, "websiteKey": sitekey}
        if accion:
            task["action"] = accion
        return self.resolver(task)["token"]


T = TypeVar("T")
REINTENTOS_TOKEN = 2


class TokenRechazado(Exception):
    """El portal rechazó el token de captcha (expirado, score bajo, etc.)."""


def con_token(
    obtener_token: Callable[[], str], enviar: Callable[[str], T],
    portal: str, reintentos: int = REINTENTOS_TOKEN,
) -> T:
    """Pide token y lo envía; si `enviar` levanta TokenRechazado, reintenta hasta `reintentos` veces."""
    for _ in range(reintentos + 1):
        try:
            return enviar(obtener_token())
        except TokenRechazado:
            continue
    raise UpstreamError(
        f"{portal} rechazó el token de captcha {reintentos + 1} veces.",
        {"portal": portal, "intentos": reintentos + 1},
    )


_SITEKEY_RES = (
    r'data-sitekey=["\']([\w-]{20,})["\']',
    r'[?&]render=([\w-]{20,})',
    r'sitekey["\']?\s*[:=]\s*["\']([\w-]{20,})["\']',
)


def extraer_sitekey(html: str, respaldo: str) -> str:
    """Sitekey del HTML/JS en vivo; si no aparece, la constante documentada."""
    for patron in _SITEKEY_RES:
        if m := re.search(patron, html or "", re.IGNORECASE):
            return m.group(1)
    return respaldo


def _vision_respaldo(png: bytes) -> str:
    """OCR de respaldo con Claude (visión). Solo si hay ANTHROPIC_API_KEY."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise UpstreamError("2captcha falló y no hay ANTHROPIC_API_KEY para el respaldo de visión.")
    try:
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            json={
                "model": os.environ.get("PLUGINS_MX_CAPTCHA_MODELO", "claude-haiku-5-5"),
                "max_tokens": 20,
                "temperature": 0,
                "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(png).decode()}},
                    {"type": "text", "text": "Transcribe solo los caracteres del captcha, sin espacios ni explicación."},
                ]}],
            },
            timeout=30,
        )
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise UpstreamError(f"Respaldo de visión falló: {type(exc).__name__}") from exc
    return "".join(b.get("text", "") for b in r.json().get("content", []))
