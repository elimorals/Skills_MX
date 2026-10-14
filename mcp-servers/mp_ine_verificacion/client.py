"""Cliente mp_ine_verificacion — Credencial para Votar: formatos, vigencia y handoff.

Verificado en vivo 2026-10-14 en https://listanominal.ine.mx/scpln/ (navegador real):
- La consulta pública "¿Está vigente tu credencial?" exige **reCAPTCHA** (sitekey
  6LdAe1sUAAAAACrdhVFHK5KmZ5TA8ZJ0iWQ6i64b) y está detrás de Cloudflare (httpx → 403
  "Just a moment"). No se evade: la verificación contra el padrón es handoff humano.
- Campos por modelo: E-J → CIC (9 dígitos) + Identificador del ciudadano (9);
  D → CIC (9) + OCR (13); A, B, C → clave de elector (18) + número de emisión (2) + OCR (13).
- Modelos que el INE presenta como vigentes: E (desde julio 2014), F (extranjero, desde
  febrero 2016), G y H (desde diciembre 2019), I y J (desde junio 2026). D y A-C: "No vigente".
- "La vigencia de cada credencial es de diez años a partir de su emisión."

Formulario (navegador real, 2026-10-14): cuatro <form> que hacen POST a
`/scpln/resultado.html` (x-www-form-urlencoded) con `modelo` oculto ("e" para E-J, "d", "c";
"r" es reporte de robo/extravío), campos `cic`, `idCiudadano`, `ocr`, `claveElector`,
`numeroEmision` y `g-recaptcha-response`. reCAPTCHA **v2 checkbox** (api.js, no Enterprise,
sin action), misma sitekey en los cuatro widgets.

Solver opt-in (`solver_activo("ine_verificacion")`): GET al formulario; si Cloudflare
responde challenge (`cf-mitigated: challenge` / "Just a moment") → handoff `bot_manager`
(no se evade). Si el formulario carga: token v2 → POST → parseo. El parseo de
`resultado.html` no se ha visto con datos reales (no se enviaron consultas de personas):
reconoce frases y, si no reconoce ninguna, falla con UpstreamError en lugar de adivinar.
Sin caché de resultados; en bitácora solo hashes.

La versión mock anterior inventaba resultados (autenticidad y "similitud de huellas" por el
último dígito, CIC de 13 dígitos, modelos C/D/D1/E/F con fechas erróneas).
Mock solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import httpx  # noqa: E402

from shared.bitacora import Bitacora  # noqa: E402
from shared.captcha_solver import (  # noqa: E402
    CaptchaSolver, TokenRechazado, con_token, extraer_sitekey, solver_activo, texto_html,
)
from shared.errors import UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.portal_handoff import USER_AGENT, armar_handoff  # noqa: E402


NAMESPACE = "ine_verificacion"
URL_LISTA_NOMINAL = "https://listanominal.ine.mx/scpln/"
URL_RESULTADO = f"{URL_LISTA_NOMINAL}resultado.html"
RECAPTCHA_SITEKEY = "6LdAe1sUAAAAACrdhVFHK5KmZ5TA8ZJ0iWQ6i64b"  # respaldo; se lee del HTML en vivo
_CAMPO_FORM = {"cic": "cic", "id_ciudadano": "idCiudadano", "ocr": "ocr",
               "clave_elector": "claveElector", "numero_emision": "numeroEmision"}
AVISO_PRIVACIDAD = (
    "Datos personales tratados conforme a la LFPDPPP: CIC, identificador, OCR o clave de elector "
    "se usan solo para verificar la vigencia de la credencial ante el INE, con consentimiento "
    "previo del titular (autorizacion_token). No se almacenan; la bitácora guarda únicamente "
    "hashes. El titular puede ejercer sus derechos ARCO ante el responsable que hace la consulta."
)
# ponytail: frases inferidas, no vistas en un resultado real; ajustar con la primera consulta en vivo.
_NO_ENCONTRADA_RE = re.compile(
    r"no (?:se )?(?:encontr|localiz|fue (?:encontrad|localizad))|no existe|no se encuentra"
    r"|datos (?:proporcionados )?no corresponden", re.I)
_NO_VIGENTE_RE = re.compile(r"no (?:es |est[aá] )?vigente", re.I)
_VIGENTE_RE = re.compile(r"\b(?:es |est[aá] )?vigente\b", re.I)
_FECHA_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2} de [a-záéíóú]+ de \d{4}\b", re.I)

CIC_RE = re.compile(r"^\d{9}$")
ID_CIUDADANO_RE = re.compile(r"^\d{9}$")
OCR_RE = re.compile(r"^\d{13}$")
CLAVE_ELECTOR_RE = re.compile(r"^[A-Z]{6}\d{8}[HM]\d{3}$")
NUM_EMISION_RE = re.compile(r"^\d{2}$")

VIGENCIA_ANIOS = 10

MODELOS_CREDENCIAL: dict[str, dict[str, Any]] = {
    "A": {"vigente_segun_ine": False, "campos": ["clave_elector", "numero_emision", "ocr"]},
    "B": {"vigente_segun_ine": False, "campos": ["clave_elector", "numero_emision", "ocr"]},
    "C": {"vigente_segun_ine": False, "campos": ["clave_elector", "numero_emision", "ocr"]},
    "D": {"vigente_segun_ine": False, "campos": ["cic", "ocr"]},
    "E": {"vigente_segun_ine": True, "desde": "julio 2014", "campos": ["cic", "id_ciudadano"]},
    "F": {"vigente_segun_ine": True, "desde": "febrero 2016 (emitida en el extranjero)",
          "campos": ["cic", "id_ciudadano"]},
    "G": {"vigente_segun_ine": True, "desde": "diciembre 2019", "campos": ["cic", "id_ciudadano"]},
    "H": {"vigente_segun_ine": True, "desde": "diciembre 2019", "campos": ["cic", "id_ciudadano"]},
    "I": {"vigente_segun_ine": True, "desde": "junio 2026", "campos": ["cic", "id_ciudadano"]},
    "J": {"vigente_segun_ine": True, "desde": "junio 2026", "campos": ["cic", "id_ciudadano"]},
}

_VALIDADORES = {
    "cic": (CIC_RE, "CIC: 9 dígitos con ceros a la izquierda"),
    "id_ciudadano": (ID_CIUDADANO_RE, "Identificador del ciudadano: 9 dígitos"),
    "ocr": (OCR_RE, "OCR: 13 dígitos"),
    "clave_elector": (CLAVE_ELECTOR_RE, "Clave de elector: 18 caracteres"),
    "numero_emision": (NUM_EMISION_RE, "Número de emisión: 2 dígitos"),
}


def _modelo(modelo: str) -> str:
    m = (modelo or "").strip().upper()
    if m not in MODELOS_CREDENCIAL:
        raise ValidationError(f"modelo inválido {modelo!r}; válidos: {sorted(MODELOS_CREDENCIAL)}")
    return m


def _exigir_autorizacion(token: str) -> None:
    if not token or len(token) < 16:
        raise ValidationError(
            "autorizacion_token requerido: obtener la autorización del titular antes de "
            "consultar datos de su credencial (datos personales)."
        )


def _es_challenge(r: httpx.Response) -> bool:
    return r.headers.get("cf-mitigated") == "challenge" or (
        r.status_code in (403, 503) and "just a moment" in r.text.lower())


def _parsear_resultado(html_txt: str) -> dict[str, Any]:
    """Estado, mensaje oficial y fecha de `resultado.html`. TokenRechazado si volvió al formulario."""
    cuerpo = re.sub(r"(?is)<(header|footer|nav)\b.*?</\1>", " ", html_txt)
    texto = texto_html(cuerpo)
    if re.search(r"captcha (?:necesario|inv[aá]lido|incorrecto|no v[aá]lido)", texto, re.I):
        raise TokenRechazado()
    for estado, patron in (("no_encontrada", _NO_ENCONTRADA_RE), ("no_vigente", _NO_VIGENTE_RE),
                           ("vigente", _VIGENTE_RE)):
        if patron.search(texto):
            frases = re.split(r"(?<=[.!])\s+", texto)
            mensaje = next(f for f in frases if patron.search(f))
            fecha = _FECHA_RE.search(texto)
            return {"estado": estado, "vigente": estado == "vigente",
                    "mensaje_oficial": mensaje[:500], "fecha_portal": fecha.group(0) if fecha else None}
    if 'id="formEFGH"' in html_txt:  # el portal regresó al formulario: token no aceptado
        raise TokenRechazado()
    raise UpstreamError("Respuesta del INE no reconocida; revisar el parseo de resultado.html.")


class INEVerificacionClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def verificar_datos(self, modelo: str, autorizacion_token: str, **campos: str | None) -> dict[str, Any]:
        """Valida formatos del modelo y devuelve handoff a la consulta oficial (reCAPTCHA)."""
        _exigir_autorizacion(autorizacion_token)
        m = _modelo(modelo)
        requeridos = MODELOS_CREDENCIAL[m]["campos"]
        limpios: dict[str, str] = {}
        for campo in requeridos:
            valor = (campos.get(campo) or "").strip().upper()
            regex, msg = _VALIDADORES[campo]
            if not regex.match(valor):
                raise ValidationError(f"{msg} (modelo {m})")
            limpios[campo] = valor
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"modelo": m, "en_lista_nominal": True})
        if solver_activo(NAMESPACE):
            return self._consulta_con_solver(m, limpios)
        self._bitacora.log("verificar_datos_handoff", success=True,
                           params_summary={"modelo": m,
                                           "cic_hash": self._bitacora.hash_sensitive(limpios.get("cic", ""))})
        return armar_handoff(
            motivo="captcha",
            detalle="La consulta del INE exige reCAPTCHA; no se automatiza.",
            url=URL_LISTA_NOMINAL,
            pasos=[
                f"Abrir la URL y elegir el bloque del modelo {m}.",
                "Capturar " + ", ".join(requeridos) + " tal como aparecen en la credencial (con ceros a la izquierda).",
                "Resolver el reCAPTCHA y pulsar CONSULTAR; registrar el resultado y la fecha.",
            ],
            modelo=m,
            formato_valido=True,
            en_lista_nominal=None,
            campos_a_capturar=requeridos,
        )

    def _consulta_con_solver(self, m: str, limpios: dict[str, str]) -> dict[str, Any]:
        """Token reCAPTCHA v2 → POST resultado.html → vigente / no_vigente / no_encontrada."""
        hashes = {f"{k}_hash": self._bitacora.hash_sensitive(v) for k, v in limpios.items()}
        with httpx.Client(timeout=30, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as http:
            try:
                pagina = http.get(URL_LISTA_NOMINAL)
            except httpx.HTTPError as exc:
                raise UpstreamError(f"INE no respondió: {type(exc).__name__}") from exc
            if _es_challenge(pagina):
                self._bitacora.log("verificar_datos_bloqueo_cloudflare", success=False,
                                   params_summary={"modelo": m, **hashes})
                return armar_handoff(
                    motivo="bot_manager",
                    detalle=("Cloudflare responde con challenge JS antes del formulario "
                             "(reCAPTCHA v2); no se evade. Consulta manual."),
                    url=URL_LISTA_NOMINAL,
                    pasos=[
                        f"Abrir la URL y elegir el bloque del modelo {m}.",
                        "Capturar " + ", ".join(limpios) + " tal como aparecen en la credencial.",
                        "Resolver el reCAPTCHA y pulsar CONSULTAR; registrar el resultado y la fecha.",
                    ],
                    captcha_tipo="recaptcha_v2",
                    modelo=m, formato_valido=True, en_lista_nominal=None,
                    campos_a_capturar=list(limpios), aviso_privacidad=AVISO_PRIVACIDAD,
                )
            if pagina.status_code != 200:
                raise UpstreamError(f"INE respondió HTTP {pagina.status_code}.",
                                    {"status_code": pagina.status_code})
            sitekey = extraer_sitekey(pagina.text, RECAPTCHA_SITEKEY)
            solver = CaptchaSolver()
            form = {"modelo": "d" if m == "D" else "c" if m in "ABC" else "e",
                    **{_CAMPO_FORM[k]: v for k, v in limpios.items()}}

            def enviar(token: str) -> dict[str, Any]:
                try:
                    r = http.post(URL_RESULTADO, data={**form, "g-recaptcha-response": token},
                                  headers={"Referer": URL_LISTA_NOMINAL})
                except httpx.HTTPError as exc:
                    raise UpstreamError(f"INE no respondió: {type(exc).__name__}") from exc
                if _es_challenge(r):
                    raise UpstreamError("Cloudflare bloqueó el envío de la consulta del INE.")
                if r.status_code != 200:
                    raise UpstreamError(f"INE respondió HTTP {r.status_code}.", {"status_code": r.status_code})
                return _parsear_resultado(r.text)

            res = con_token(lambda: solver.recaptcha(sitekey, URL_LISTA_NOMINAL), enviar, "INE lista nominal")
        self._bitacora.log("verificar_datos_consulta", success=True,
                           params_summary={"modelo": m, **hashes}, result_summary={"estado": res["estado"]})
        return {
            "consultado": True, "simulated": False, "requiere_humano": False,
            "modelo": m, **res,
            "en_lista_nominal": res["estado"] == "vigente",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": URL_RESULTADO,
            "aviso_privacidad": AVISO_PRIVACIDAD,
        }

    def verificar_qr(self, qr_payload: str) -> dict[str, Any]:
        """Sin la llave pública del INE no se puede validar la firma del QR: no se afirma nada."""
        if not qr_payload or len(qr_payload) < 32:
            raise ValidationError("qr_payload muy corto (≥32 chars esperados)")
        return armar_handoff(
            motivo="sin_verificador_publico",
            detalle=("El INE no publica un mecanismo/llave para validar el QR fuera de sus servicios; "
                     "la versión anterior 'validaba' por el prefijo del texto."),
            url=URL_LISTA_NOMINAL,
            pasos=[],
            autentica=None,
            verificable_localmente=False,
        )

    def consultar_vigencia(self, modelo: str, anio_emision: int) -> dict[str, Any]:
        """Regla publicada por el INE: modelo en lista de vigentes y < 10 años desde la emisión."""
        m = _modelo(modelo)
        hoy = datetime.now(timezone.utc).year
        if anio_emision < 1990 or anio_emision > hoy:
            raise ValidationError(f"anio_emision fuera de rango: {anio_emision}")
        modelo_vigente = MODELOS_CREDENCIAL[m]["vigente_segun_ine"]
        dentro_de_plazo = hoy < anio_emision + VIGENCIA_ANIOS
        return {
            "modelo": m,
            "anio_emision": anio_emision,
            "modelo_vigente_segun_ine": modelo_vigente,
            "vence_fin_de_anio": anio_emision + VIGENCIA_ANIOS,
            "vigente_por_regla": modelo_vigente and dentro_de_plazo,
            "nota": ("Estimación por regla pública (10 años desde la emisión; la credencial trae su "
                     "año de vigencia impreso). Bajas por robo/extravío o reposición solo se ven en "
                     "la consulta oficial."),
            "fuente": URL_LISTA_NOMINAL,
        }

    def generar_autorizacion(self, curp: str, proposito: str, vigencia_dias: int = 90) -> dict[str, Any]:
        """Plantilla de autorización del titular. Texto local, no es un documento del INE."""
        if vigencia_dias < 1 or vigencia_dias > 365:
            raise ValidationError("vigencia_dias entre 1 y 365")
        if not proposito or len(proposito) < 10:
            raise ValidationError("proposito requerido (mínimo 10 chars)")
        if not curp or len(curp) != 18:
            raise ValidationError(f"CURP inválida (18 chars): {curp!r}")
        ahora = datetime.now(timezone.utc)
        return {
            "token_referencia": self._bitacora.hash_sensitive(f"{curp}|{proposito}|{ahora.isoformat()}")[:32],
            "fecha_emision": ahora.isoformat(),
            "vigencia_dias": vigencia_dias,
            "texto_autorizacion": (
                f"Por medio del presente, AUTORIZO el tratamiento de los datos de mi Credencial para "
                f"Votar para verificar su vigencia ante el INE, con el siguiente propósito: {proposito}.\n\n"
                f"Mi autorización tiene vigencia de {vigencia_dias} días naturales a partir de hoy. "
                f"Conozco mis derechos ARCO y puedo revocar esta autorización en cualquier momento."
            ),
            "campos_firma": ["nombre_completo", "fecha", "firma_olografa_o_digital"],
            "nota": "Plantilla orientativa; revisar con el aviso de privacidad del responsable.",
        }

    def listar_modelos_credencial(self) -> dict[str, Any]:
        return {
            "modelos": [{"clave": k, **v} for k, v in MODELOS_CREDENCIAL.items()],
            "vigencia_anios": VIGENCIA_ANIOS,
            "fuente": URL_LISTA_NOMINAL,
            "verificado": "2026-10-14",
        }
