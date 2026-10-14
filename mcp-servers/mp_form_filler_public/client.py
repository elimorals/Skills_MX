"""Cliente mp_form_filler_public — autollenado de formularios públicos gob.mx.

Solo formularios PÚBLICOS sin login (cualquier ciudadano puede llenarlos). NO
cubre operaciones autenticadas — para eso ver mp_sat_portal / mp_imss_patronal.

Características:
- Catálogo de formularios públicos con URL, campos y tipo de CAPTCHA
- Validación pre-flight: tipos de datos, longitudes, regex MX (RFC, CURP, NSS, placa)
- `llenar` en modo real devuelve un **handoff humano**: URL, pasos y los campos
  ya validados para pegarlos en el portal. Si existe un MCP que consulta ese
  portal de verdad (p. ej. REPSE), se indica en `mcp_real`.

⚠ NO resuelve CAPTCHAs ni envía formularios por su cuenta. Mock solo con
PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "form_filler_public"

RFC_RE = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")
CURP_RE = re.compile(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$")
NSS_RE = re.compile(r"^\d{11}$")
PLACA_RE = re.compile(r"^[A-Z0-9]{3,7}$")
TEL_RE = re.compile(r"^\d{10}$")

# Catálogo de formularios públicos soportados (selectores validados 2026-06-15)
FORMULARIOS_PUBLICOS: dict[str, dict[str, Any]] = {
    "sat_rfc_consulta": {
        "nombre": "SAT — Consulta RFC en padrón",
        "url": "https://siat.sat.gob.mx/PTSC/IdentificacionContribuyentes/secuencia.html",
        "campos_requeridos": ["rfc"],
        "validaciones": {"rfc": "RFC_RE"},
        "selectores": {
            "rfc": "input[name='ctl00$MainContent$txtRFC']",
            "submit": "input[type='submit'][value='Consultar']",
        },
        "tipo_resultado": "html_text",
        "tiene_captcha": True,
        "captcha_tipo": "imagen",
    },
    "sat_verifica_cfdi": {
        "nombre": "SAT — Verifica CFDI",
        "url": "https://verificacfdi.facturaelectronica.sat.gob.mx/",
        "campos_requeridos": ["uuid", "rfc_emisor", "rfc_receptor", "total"],
        "validaciones": {
            "uuid": r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$",
            "rfc_emisor": "RFC_RE",
            "rfc_receptor": "RFC_RE",
        },
        "selectores": {
            "uuid": "input[name='ctl00$MainContent$TxtUUID']",
            "rfc_emisor": "input[name='ctl00$MainContent$TxtRfcEmisor']",
            "rfc_receptor": "input[name='ctl00$MainContent$TxtRfcReceptor']",
            "total": "input[name='ctl00$MainContent$TxtImporte']",
            "submit": "input[type='submit']",
        },
        "tipo_resultado": "estado_cfdi",
        "tiene_captcha": True,
        "captcha_tipo": "imagen",
    },
    "repse_consulta": {
        "nombre": "STPS — Consulta REPSE",
        "url": "https://repse.stps.gob.mx/",
        "campos_requeridos": ["rfc"],
        "validaciones": {"rfc": "RFC_RE"},
        "selectores": {
            "rfc": "input[name='rfc']",
            "submit": "button[type='submit']",
        },
        "tipo_resultado": "tabla_padron",
        "tiene_captcha": False,
        "mcp_real": "mp_repse_stps",
    },
    "repuve_consulta": {
        "nombre": "REPUVE — Consulta vehículo",
        "url": "https://www2.repuve.gob.mx:8443/ciudadania/",
        "campos_requeridos": ["niv_o_placa"],
        "validaciones": {"niv_o_placa": "PLACA_RE"},
        "selectores": {
            "niv_o_placa": "input[name='niv']",
            "submit": "input[type='submit']",
        },
        "tipo_resultado": "ficha_vehiculo",
        "tiene_captcha": True,
        "captcha_tipo": "recaptcha_v3",  # verificado 2026-10-14
        "mcp_real": "mp_repuve",
    },
    "repep_consulta": {
        "nombre": "PROFECO — Consulta REPEP",
        "url": "https://repep.profeco.gob.mx/",
        "campos_requeridos": ["telefono"],
        "validaciones": {"telefono": "TEL_RE"},
        "selectores": {
            "telefono": "input[name='telefono']",
            "submit": "button[type='submit']",
        },
        "tipo_resultado": "estado_inscripcion",
        "tiene_captcha": False,
    },
    "curp_consulta": {
        "nombre": "RENAPO — Consulta CURP",
        "url": "https://www.gob.mx/curp/",
        "campos_requeridos": ["curp"],
        "validaciones": {"curp": "CURP_RE"},
        "selectores": {
            "curp": "input[name='curp']",
            "submit": "button[type='submit']",
        },
        "tipo_resultado": "datos_persona",
        "tiene_captcha": True,
        "captcha_tipo": "recaptcha_enterprise",  # + challenge Akamai, verificado 2026-10-14
        "mcp_real": "mp_curp_renapo",
    },
    "buro_comercial": {
        "nombre": "PROFECO — Buró Comercial",
        "url": "https://burocomercial.profeco.gob.mx/",
        "campos_requeridos": ["razon_social"],
        "validaciones": {},
        "selectores": {
            "razon_social": "input[name='proveedor']",
            "submit": "button[type='submit']",
        },
        "tipo_resultado": "tabla_quejas",
        "tiene_captcha": False,
    },
    "sat_opinion_32d": {
        "nombre": "SAT — Opinión cumplimiento 32-D",
        "url": "https://www.sat.gob.mx/aplicacion/operacion/35715/registra-tu-clave-de-r-f-c-de-tu-contraparte",
        "campos_requeridos": ["rfc_contraparte"],
        "validaciones": {"rfc_contraparte": "RFC_RE"},
        "selectores": {
            "rfc_contraparte": "input[name='rfcContraparte']",
            "submit": "button[type='submit']",
        },
        "tipo_resultado": "opinion_pdf",
        "tiene_captcha": False,
    },
}


def _validar_campo(valor: str, regla: str) -> tuple[bool, str | None]:
    """Valida un campo contra una regla (nombre o regex)."""
    if not valor:
        return False, "Campo vacío"
    regex_map = {
        "RFC_RE": RFC_RE,
        "CURP_RE": CURP_RE,
        "NSS_RE": NSS_RE,
        "PLACA_RE": PLACA_RE,
        "TEL_RE": TEL_RE,
    }
    rx = regex_map.get(regla)
    if rx is None:
        # Asumir que regla es un patrón regex directo
        try:
            rx = re.compile(regla)
        except re.error:
            return False, f"Regla regex inválida: {regla}"
    if not rx.match(valor.strip().upper()):
        return False, f"No cumple patrón {regla}"
    return True, None


class FormFillerPublicClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = {}
        for k, v in params.items():
            # Hashear identificadores sensibles
            if k in {"rfc", "curp", "nss", "telefono", "placa", "niv_o_placa"}:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(v))
            else:
                safe[k] = v
        self._bitacora.log(op, success=True, params_summary=safe)

    def listar_formularios(self, sin_captcha: bool = False) -> dict[str, Any]:
        """Lista formularios soportados, opcionalmente solo sin captcha."""
        self._log("listar_formularios", {"sin_captcha": sin_captcha})
        items = []
        for clave, f in FORMULARIOS_PUBLICOS.items():
            if sin_captcha and f.get("tiene_captcha"):
                continue
            items.append({
                "clave": clave,
                "nombre": f["nombre"],
                "url": f["url"],
                "campos_requeridos": f["campos_requeridos"],
                "tiene_captcha": f.get("tiene_captcha", False),
                "captcha_tipo": f.get("captcha_tipo"),
                "tipo_resultado": f["tipo_resultado"],
            })
        return {
            "total": len(items),
            "filtro_sin_captcha": sin_captcha,
            "formularios": items,
        }

    def validar_inputs(self, clave: str, datos: dict[str, str]) -> dict[str, Any]:
        """Pre-flight: valida datos antes de enviar al portal (sin tocar red)."""
        self._log("validar_inputs", {"clave": clave, **datos})
        if clave not in FORMULARIOS_PUBLICOS:
            raise ValidationError(f"clave no reconocida: {clave!r}")
        f = FORMULARIOS_PUBLICOS[clave]
        errores: list[dict[str, str]] = []
        for campo in f["campos_requeridos"]:
            valor = datos.get(campo, "").strip()
            if not valor:
                errores.append({"campo": campo, "error": "Faltante"})
                continue
            regla = f["validaciones"].get(campo)
            if regla:
                ok, msg = _validar_campo(valor, regla)
                if not ok:
                    errores.append({"campo": campo, "error": msg or "Inválido"})
        return {
            "clave": clave,
            "valido": len(errores) == 0,
            "total_errores": len(errores),
            "errores": errores,
            "campos_recibidos": list(datos.keys()),
        }

    def llenar(
        self,
        clave: str,
        datos: dict[str, str],
        screenshot: bool = False,
    ) -> dict[str, Any]:
        """Prepara el llenado: valida datos y devuelve handoff humano (URL, pasos,
        campos prellenados). `screenshot` se ignora en modo real (no se abre navegador).
        Mock solo con PLUGINS_MX_MOCK=1.
        """
        self._log("llenar", {"clave": clave, **datos, "screenshot": screenshot})
        if clave not in FORMULARIOS_PUBLICOS:
            raise ValidationError(f"clave no reconocida: {clave!r}")

        # Pre-flight validación
        prevalid = self.validar_inputs(clave, datos)
        if not prevalid["valido"]:
            raise ValidationError(
                f"Pre-flight falló: {prevalid['errores']}"
            )

        f = FORMULARIOS_PUBLICOS[clave]
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            return mark_simulated(
                {
                    "clave": clave,
                    "url": f["url"],
                    "datos_enviados": list(datos.keys()),
                    "exito": True,
                    "requiere_intervencion_humana": f.get("tiene_captcha", False),
                    "captcha_tipo_detectado": f.get("captcha_tipo"),
                    "respuesta_parcial": (
                        f"[MOCK] Resultado tipo {f['tipo_resultado']} esperado."
                    ),
                    "screenshot_b64": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        pasos = [
            f"Abrir {f['url']} en un navegador.",
            "Pegar los campos prellenados (ya validados) en el formulario.",
        ]
        if f.get("tiene_captcha"):
            pasos.append(f"Resolver la verificación de seguridad ({f.get('captcha_tipo')}).")
        pasos.append("Enviar y guardar el comprobante/resultado.")
        return {
            "clave": clave,
            "requiere_humano": True,
            "requiere_intervencion_humana": True,
            "motivo": "captcha_requerido" if f.get("tiene_captcha") else "envio_manual",
            "url": f["url"],
            "pasos": pasos,
            "campos_prellenados": {k: str(v).strip() for k, v in datos.items()},
            "captcha_tipo": f.get("captcha_tipo"),
            "mcp_real": f.get("mcp_real"),
            "exito": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
