"""Cliente mp_ine_verificacion — KYC INE con QR.

Servicio de verificación de credencial INE: devuelve true/false + porcentaje
similitud de huellas SIN exponer datos personales (LFPDPPP compliant).

Modelos credencial vigentes:
- Modelo C → 2008-2012 (anverso vertical)
- Modelo D → 2013
- Modelo D1 → 2014
- Modelo E → 2018
- Modelo F → 2024 (incluye QR alta densidad)
"""
from __future__ import annotations

import json
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


NAMESPACE = "ine_verificacion"
URL_INE_VERIFICACION = "https://portal.ine.mx/servicio-verificacion-datos-credencial-votar/"


# Formato CIC (Código de Identificación de la Credencial): 13 dígitos en modelos D/E/F
CIC_RE = re.compile(r"^\d{13}$")
# Clave de elector: 18 caracteres (letras+dígitos) en credenciales históricas
CLAVE_ELECTOR_RE = re.compile(r"^[A-Z]{6}\d{8}[HM]\d{3}$")
# OCR: número en reverso credencial (modelos D+ 13 dígitos)
OCR_RE = re.compile(r"^\d{12,13}$")

MODELOS_CREDENCIAL = {
    "C": "Modelo C (2008-2012)",
    "D": "Modelo D (2013)",
    "D1": "Modelo D1 (2014)",
    "E": "Modelo E (2018-2024)",
    "F": "Modelo F (2024-presente, QR alta densidad)",
}


class INEVerificacionClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def verificar_datos(
        self,
        cic: str,
        clave_elector: str,
        anio_emision: int,
        autorizacion_token: str,
    ) -> dict[str, Any]:
        """Verifica autenticidad credencial vs padrón INE.

        Devuelve solo true/false + porcentaje similitud, SIN exponer datos personales.
        REQUIERE autorización del titular (LFPDPPP).
        """
        if not autorizacion_token or len(autorizacion_token) < 16:
            raise ValidationError(
                "autorizacion_token requerido (LFPDPPP). "
                "Obtener autorización firmada del titular antes de invocar."
            )
        cic = (cic or "").strip()
        if not CIC_RE.match(cic):
            raise ValidationError(f"CIC inválido (13 dígitos esperados): {cic!r}")
        clave_elector = (clave_elector or "").strip().upper()
        if not CLAVE_ELECTOR_RE.match(clave_elector):
            raise ValidationError(f"clave_elector inválida: {clave_elector!r}")
        if anio_emision < 2008 or anio_emision > datetime.now(timezone.utc).year:
            raise ValidationError(f"anio_emision fuera de rango: {anio_emision}")

        # Mock determinístico por suffix del CIC
        last = int(cic[-1])
        autentica = last != 0  # 90% auténticas
        similitud = 95.0 - (last % 5) if autentica else 0.0

        self._bitacora.log("verificar_datos", success=True,
                           params_summary={"cic_hash": self._bitacora.hash_sensitive(cic),
                                           "anio_emision": anio_emision})
        return mark_simulated({
            "autentica": autentica,
            "similitud_huellas_pct": similitud,
            "modelo_credencial": _detectar_modelo(anio_emision),
            "anio_emision": anio_emision,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": URL_INE_VERIFICACION,
            "ley_aplicable": "Art. 142 LGIPE — Servicio de Verificación de Datos",
        })

    def verificar_qr(self, qr_payload: str) -> dict[str, Any]:
        """Verifica QR alta densidad de credencial modelo F (2024+).

        El QR INE contiene datos firmados criptográficamente — su existencia
        garantiza que la credencial fue emitida por el INE.
        """
        if not qr_payload or len(qr_payload) < 32:
            raise ValidationError("qr_payload muy corto (≥32 chars esperados)")

        # Mock: simular parsing. Real path requiere validación firma criptográfica INE.
        prefix_valid = qr_payload.startswith("INE.MX.QR.") or qr_payload.startswith("INE:")
        autentica = prefix_valid

        return mark_simulated({
            "autentica": autentica,
            "metodo": "QR alta densidad INE (modelo F 2024+)",
            "validacion_firma_criptografica": "mock — path real requiere INE pubkey",
            "datos_extraidos": {
                "cic_parcial": "******1234",
                "anio_emision": 2024,
                "vigente": True,
            } if autentica else None,
            "nota": "El QR INE NO expone datos personales en claro; sólo firma + token verificable.",
        })

    def consultar_vigencia(self, cic: str, autorizacion_token: str) -> dict[str, Any]:
        if not autorizacion_token or len(autorizacion_token) < 16:
            raise ValidationError("autorizacion_token requerido (LFPDPPP)")
        cic = (cic or "").strip()
        if not CIC_RE.match(cic):
            raise ValidationError(f"CIC inválido: {cic!r}")

        last = int(cic[-1])
        vigente = last % 3 != 0  # ~66% vigentes
        return mark_simulated({
            "cic_hash": self._bitacora.hash_sensitive(cic),
            "vigente": vigente,
            "fecha_vencimiento": "2034-12-31" if vigente else "2024-06-30",
            "ano_emision_estimado": 2018 + (last % 6),
        })

    def generar_autorizacion(
        self, curp: str, proposito: str, vigencia_dias: int = 90,
    ) -> dict[str, Any]:
        """Template de autorización LFPDPPP para que el titular firme."""
        if vigencia_dias < 1 or vigencia_dias > 365:
            raise ValidationError("vigencia_dias entre 1 y 365")
        if not proposito or len(proposito) < 10:
            raise ValidationError("proposito requerido (mínimo 10 chars)")
        if not curp or len(curp) != 18:
            raise ValidationError(f"CURP inválida (18 chars): {curp!r}")

        ahora = datetime.now(timezone.utc)
        token_referencia = self._bitacora.hash_sensitive(f"{curp}|{proposito}|{ahora.isoformat()}")[:32]
        return mark_simulated({
            "token_referencia": token_referencia,
            "fecha_emision": ahora.isoformat(),
            "vigencia_dias": vigencia_dias,
            "texto_autorizacion": (
                f"Por medio del presente, AUTORIZO la verificación de los datos de mi "
                f"Credencial para Votar ante el Servicio de Verificación de Datos del INE, "
                f"con el siguiente propósito: {proposito}.\n\n"
                f"Mi autorización tiene vigencia de {vigencia_dias} días naturales a partir "
                f"de hoy. Conozco mis derechos ARCO (LFPDPPP) y puedo revocar esta "
                f"autorización en cualquier momento."
            ),
            "campos_firma": ["nombre_completo", "fecha", "firma_olografa_o_digital"],
            "ley_aplicable": "LFPDPPP + Art. 142 LGIPE",
        })

    def listar_modelos_credencial(self) -> dict[str, Any]:
        return {
            "modelos": [
                {"clave": k, "descripcion": v} for k, v in MODELOS_CREDENCIAL.items()
            ],
            "modelo_actual_vigente": "F (2024+)",
            "soporta_qr": ["F"],
            "fuente": "INE — Conoce tu Credencial",
        }


def _detectar_modelo(anio: int) -> str:
    if anio >= 2024:
        return "F (QR alta densidad)"
    if anio >= 2018:
        return "E"
    if anio >= 2014:
        return "D1"
    if anio >= 2013:
        return "D"
    return "C"
