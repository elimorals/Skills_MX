"""Utilidades para REPUVE — Registro Público Vehicular.

Portal:   https://www2.repuve.gob.mx:8443/ciudadania/
Stack:    Angular SPA + reCAPTCHA v3 invisible (acción "login").
Endpoint: POST https://www2.repuve.gob.mx:8443/consulta/consulta/repuve
          body JSON {criterio, llave, token}. Verificado 2026-10-14: un navegador
          automatizado recibe 401 "El reCaptcha no fue superado correctamente".

Cifrado del lado cliente (leído de main.*.js público, 2026-10-14): `criterio`
("1" placa, "2" NIV) y `llave` (el valor) van cifrados con RSA-1024
PKCS#1 v1.5 (node-forge `publicKey.encrypt` por defecto) y en base64, con
llaves públicas FIJAS embebidas en el bundle (`publicKeyRep` para /repuve,
`publicKeyPgj` para /pgj, que da el estatus de robo). No hay llave por sesión
ni otro anti-bot: es reproducible sin evadir nada más que el captcha, que se
resuelve con el solver opt-in (shared/captcha_solver.py). Sin solver: handoff.
"""
from __future__ import annotations

import base64
import re
import ssl
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from shared.captcha_solver import TokenRechazado, extraer_sitekey
from shared.errors import ConfigError, UpstreamError


PORTAL_URL = "https://www2.repuve.gob.mx:8443/ciudadania/"
RECAPTCHA_SITE_KEY = "6Lfy8AEoAAAAANclz0Doczn6y826fM0BjOPXEn9B"
RECAPTCHA_ACCION = "login"  # recaptchaV3Service.execute("login") antes de /repuve
API_BASE = "https://www2.repuve.gob.mx:8443/consulta/consulta"
API_URL = f"{API_BASE}/repuve"
API_PGJ = f"{API_BASE}/pgj"
CRITERIO = {"placa": "1", "niv": "2"}

# Respaldo si el bundle en vivo no se puede leer (valores del 2026-10-14).
CLAVE_REP = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDVrrj9NHtVBAHCWhqGIiaNoaTBLqF0AAnB07PUnRJQ0YKTHvRyoLfllDkYrkmunGEFvyMoKUtPz8LBsyjZrW0pNQnaMBGp7TEFaYt/O436vIa1TSIvgULpKqE5PBgue/BZPnfD6x7qHkJTxjnSrUyG6YIWDIa30XLqYjl0/+NSzwIDAQAB\n"
    "-----END PUBLIC KEY-----"
)
CLAVE_PGJ = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDVj7xC0/A+Sp5ZGoZ5nlxt46RTJ1owTBPXogRNX1Vyo6M8ZeJFTPne+uD1pu/0Yt5svw5cHZIKICBMTT8efMKada+84mjmJHQduGsNN9IKgVV4V858YmgVQLxoTMY9ILc+qHwVmm0YBD5hzaH8YBxdLOfxD41kSQ+4Wze4O3BwwIDAQAB\n"
    "-----END PUBLIC KEY-----"
)
_CONFIG: dict[str, str] = {}  # se lee el bundle una vez por proceso


def ssl_legacy() -> ssl.SSLContext:
    """El servidor REPUVE solo negocia cifrados TLS legacy."""
    import certifi

    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    return ctx


def cifrar(texto: str, pem: str) -> str:
    """RSA PKCS#1 v1.5 + base64, igual que node-forge en el portal."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError as exc:  # extra opcional
        raise ConfigError("REPUVE con solver requiere `cryptography` (extra sat-ws o dev).") from exc
    llave = serialization.load_pem_public_key(pem.encode())
    return base64.b64encode(llave.encrypt(texto.encode("utf-8"), padding.PKCS1v15())).decode()


def _clave(js: str, nombre: str, respaldo: str) -> str:
    m = re.search(nombre + r'="(-----BEGIN PUBLIC KEY-----.*?-----END PUBLIC KEY-----)"', js, re.S)
    return m.group(1).replace("\\n", "\n") if m else respaldo


def config_portal(http: httpx.Client) -> dict[str, str]:
    """Sitekey y llaves RSA del bundle en vivo; constantes documentadas si no aparecen."""
    if _CONFIG:
        return _CONFIG
    js = ""
    try:
        html = http.get(PORTAL_URL).text
        if m := re.search(r'src="\.?/?(main\.[\w]+\.js)"', html):
            js = http.get(PORTAL_URL + m.group(1)).text
    except httpx.HTTPError:
        pass  # respaldo con constantes
    _CONFIG.update(
        sitekey=extraer_sitekey(js, RECAPTCHA_SITE_KEY),
        rep=_clave(js, "publicKeyRep", CLAVE_REP),
        pgj=_clave(js, "publicKeyPgj", CLAVE_PGJ),
    )
    return _CONFIG


def enviar(http: httpx.Client, url: str, pem: str, tipo: str, valor: str, token: str) -> list[dict[str, Any]]:
    """POST cifrado; devuelve las filas. TokenRechazado si el portal no acepta el reCAPTCHA."""
    body = {"criterio": cifrar(CRITERIO[tipo], pem), "llave": cifrar(valor, pem), "token": token}
    try:
        r = http.post(url, json=body)
    except httpx.HTTPError as exc:
        raise UpstreamError(f"REPUVE no respondió: {type(exc).__name__}", {"url": url}) from exc
    if r.status_code == 401 and "recaptcha" in r.text.lower():
        raise TokenRechazado()
    if r.status_code != 200:
        raise UpstreamError(f"REPUVE respondió HTTP {r.status_code}.", {"url": url, "status_code": r.status_code})
    data = r.json() if r.content else {}
    # El portal recorre Object.entries(respuesta) y toma j[0]: dict de listas de filas.
    filas: list[dict[str, Any]] = []
    for v in (data.values() if isinstance(data, dict) else []):
        if isinstance(v, list):
            filas += [f for f in v if isinstance(f, dict)]
    return filas


def estatus_robo(filas_pgj: list[dict[str, Any]]) -> tuple[str, bool]:
    """Sin filas en PGJ el portal muestra "NO ROBADO"."""
    # ponytail: valores de ESTATUS_VHI_ROBO no validados en vivo; todo lo que no empiece con NO/SIN cuenta como robo.
    estatus = next((str(f.get("ESTATUS_VHI_ROBO") or "").strip() for f in filas_pgj if f.get("ESTATUS_VHI_ROBO")), "")
    if not estatus:
        return "NO ROBADO", False
    return estatus, not re.match(r"^(NO|SIN)\b", estatus.upper())


# Regex NIV/VIN: 17 caracteres alfanuméricos (sin I, O, Q por estándar ISO 3779)
_NIV_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

# Regex placa mexicana: 2-3 letras + 2-3 dígitos + 1-2 letras (variantes por estado)
_PLACA_PATTERN = re.compile(r"^[A-Z]{2,3}[-\s]?[0-9]{2,4}[-\s]?[A-Z0-9]{1,3}$")


@dataclass
class VehiculoREPUVE:
    """Resultado normalizado de consulta REPUVE."""
    niv: str = ""
    placa: str = ""
    marca: str = ""
    submarca: str = ""
    modelo: str = ""  # año del modelo
    color: str = ""
    tipo: str = ""
    estado: str = ""  # entidad federativa de registro
    estatus_robo: str = ""  # "SIN REPORTE DE ROBO" / "REPORTE DE ROBO ACTIVO"
    tiene_reporte_robo: bool = False
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "niv": self.niv,
            "placa": self.placa,
            "marca": self.marca,
            "submarca": self.submarca,
            "modelo": self.modelo,
            "color": self.color,
            "tipo": self.tipo,
            "estado": self.estado,
            "estatus_robo": self.estatus_robo,
            "tiene_reporte_robo": self.tiene_reporte_robo,
        }


def validar_niv(niv: str) -> str:
    """Valida y normaliza NIV/VIN.

    Estándar ISO 3779: 17 caracteres alfanuméricos sin I, O, Q.
    Es responsabilidad del caller verificar el dígito verificador (posición 9)
    si necesita validación estricta — REPUVE acepta NIVs aunque tengan typos.
    """
    niv = (niv or "").strip().upper().replace(" ", "").replace("-", "")
    if len(niv) != 17:
        raise ValueError(f"NIV debe tener 17 caracteres, recibido {len(niv)}.")
    if not _NIV_PATTERN.match(niv):
        raise ValueError(
            "NIV inválido. Solo letras A-Z (sin I/O/Q) y dígitos 0-9."
        )
    return niv


def validar_placa(placa: str) -> str:
    """Valida y normaliza placa mexicana."""
    placa = (placa or "").strip().upper()
    if not placa:
        raise ValueError("Placa requerida.")
    if not _PLACA_PATTERN.match(placa):
        raise ValueError(
            "Placa con formato inválido. Esperado: 2-3 letras + 2-4 dígitos + 1-3 caracteres."
        )
    return placa


__all__ = [
    "PORTAL_URL",
    "RECAPTCHA_SITE_KEY",
    "VehiculoREPUVE",
    "validar_niv",
    "validar_placa",
]
