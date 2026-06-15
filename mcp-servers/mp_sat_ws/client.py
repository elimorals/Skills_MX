"""Cliente SAT Web Service Descarga Masiva CFDI.

3 modos:
  - mock (default): respuestas determinísticas, no requiere e.firma.
  - real (PLUGINS_MX_SAT_WS_LIVE=1 + SAT_EFIRMA_CERT/KEY/PASSWORD): full SOAP.

Flujo end-to-end:
    cliente = SatWsClient()
    sol = cliente.solicitar_descarga(SolicitudDescarga(
        rfc_emisor="ABC120101AB1",
        fecha_inicial="2026-01-01T00:00:00",
        fecha_final="2026-01-31T23:59:59",
        tipo_solicitud="CFDI",
    ))
    # sol = {"id_solicitud": "abc-def-...", "cod_estatus": 5000}
    estado = cliente.verificar_solicitud(sol["id_solicitud"], rfc_emisor="ABC...")
    # Polling cada 10-30s hasta estado["cod_estatus_solicitud"] == 3
    paquetes = cliente.descargar_paquetes(estado["paquetes"], rfc_emisor="ABC...")
    # paquetes = [{"id": ..., "zip_base64": ...}]

NOTA: El modo real requiere SOAP signing con XMLSignature (firma del request
con la e.firma). En v1 implementamos la estructura completa con mock; el
signing real queda como extension point via `_firmar_soap_request` que debe
implementarse cuando el user provee credenciales.
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ConfigError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.sat_ws import (  # noqa: E402
    ESTADO_ACEPTADA,
    ESTADO_EN_PROCESO,
    ESTADO_TERMINADA,
    SolicitudDescarga,
    estado_es_terminal,
    parsear_estado_solicitud,
)


NAMESPACE = "sat_ws"
TIMEOUT_SECONDS = 60.0


class SatWsClient:
    """Cliente del Web Service SAT Descarga Masiva CFDI."""

    CRED_ENV_VARS = ["SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]
    LIVE_ENV_FLAG = "PLUGINS_MX_SAT_WS_LIVE"

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ============================================================
    # Tools del MCP
    # ============================================================

    def solicitar_descarga(self, solicitud: SolicitudDescarga | dict) -> dict[str, Any]:
        """Inicia una solicitud de descarga masiva.

        Args:
            solicitud: SolicitudDescarga dataclass o dict equivalente.

        Returns:
            {
              "id_solicitud": str (UUID),
              "cod_estatus": int (5000 = aceptada),
              "mensaje": str,
              "rfc_emisor": str,
              "fecha_solicitud": ISO-8601,
              "simulated": bool,
            }
        """
        if isinstance(solicitud, dict):
            solicitud = SolicitudDescarga(**solicitud)
        solicitud.validar()

        self._bitacora.log(
            "solicitar_descarga",
            success=True,
            params_summary={
                "rfc_emisor_hash": self._bitacora.hash_sensitive(solicitud.rfc_emisor),
                "rango": f"{solicitud.fecha_inicial} → {solicitud.fecha_final}",
                "tipo": solicitud.tipo_solicitud,
            },
        )

        if is_mock_mode(self.CRED_ENV_VARS):
            return self._mock_solicitud(solicitud)
        return self._real_solicitud(solicitud)

    def verificar_solicitud(self, id_solicitud: str, rfc_emisor: str) -> dict[str, Any]:
        """Polling del estado de una solicitud.

        Returns:
            {
              "id_solicitud": str,
              "cod_estatus_solicitud": int (1=aceptada, 2=en proceso, 3=terminada, 4=error),
              "estado_legible": "ACEPTADA" | "EN_PROCESO" | "TERMINADA" | ...,
              "es_terminal": bool,
              "numero_cfdis": int,
              "paquetes": [str] (IDs de paquetes ZIP a descargar),
              "fecha_consulta": ISO-8601,
              "simulated": bool,
            }
        """
        if not id_solicitud or not rfc_emisor:
            raise ValidationError("id_solicitud y rfc_emisor requeridos.")

        self._bitacora.log(
            "verificar_solicitud",
            success=True,
            params_summary={
                "id_hash": self._bitacora.hash_sensitive(id_solicitud),
                "rfc_hash": self._bitacora.hash_sensitive(rfc_emisor),
            },
        )

        if is_mock_mode(self.CRED_ENV_VARS):
            return self._mock_verificar(id_solicitud)
        return self._real_verificar(id_solicitud, rfc_emisor)

    def descargar_paquete(self, id_paquete: str, rfc_emisor: str) -> dict[str, Any]:
        """Descarga un paquete ZIP con CFDIs.

        Returns:
            {
              "id_paquete": str,
              "zip_base64": str (contenido binario ZIP en base64),
              "cfdis_estimados": int,
              "fecha_descarga": ISO-8601,
              "simulated": bool,
            }
        """
        if not id_paquete or not rfc_emisor:
            raise ValidationError("id_paquete y rfc_emisor requeridos.")

        self._bitacora.log(
            "descargar_paquete",
            success=True,
            params_summary={"id_hash": self._bitacora.hash_sensitive(id_paquete)},
        )

        if is_mock_mode(self.CRED_ENV_VARS):
            return self._mock_descargar(id_paquete)
        return self._real_descargar(id_paquete, rfc_emisor)

    # ============================================================
    # Real path (placeholder — requiere XMLSignature con e.firma)
    # ============================================================

    def _real_solicitud(self, sol: SolicitudDescarga) -> dict[str, Any]:
        raise ConfigError(
            "Modo real SAT WS requiere implementación de XMLSignature con e.firma "
            "(certificado .cer + llave .key + password). Setea PLUGINS_MX_MOCK=1 "
            "para usar mock determinístico, o implementa _firmar_soap_request() en "
            "el cliente para activar producción.",
            {
                "env_vars_requeridas": self.CRED_ENV_VARS,
                "dependencia_requerida": "signxml o lxml + cryptography",
            },
        )

    def _real_verificar(self, id_solicitud: str, rfc: str) -> dict[str, Any]:
        raise ConfigError("Idem _real_solicitud — implementar XMLSignature.")

    def _real_descargar(self, id_paquete: str, rfc: str) -> dict[str, Any]:
        raise ConfigError("Idem _real_solicitud — implementar XMLSignature.")

    # ============================================================
    # Mock path
    # ============================================================

    def _mock_solicitud(self, sol: SolicitudDescarga) -> dict[str, Any]:
        return mark_simulated({
            "id_solicitud": str(uuid.uuid4()),
            "cod_estatus": 5000,
            "mensaje": "Solicitud Aceptada (mock).",
            "rfc_emisor": sol.rfc_emisor,
            "rango": f"{sol.fecha_inicial} → {sol.fecha_final}",
            "tipo_solicitud": sol.tipo_solicitud,
            "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_verificar(self, id_solicitud: str) -> dict[str, Any]:
        # Determinístico: id que termine en par → TERMINADA, impar → EN_PROCESO
        last = id_solicitud[-1].lower()
        if last in "02468ace":
            estado = ESTADO_TERMINADA
            paquetes = [f"{id_solicitud}_01", f"{id_solicitud}_02"]
            numero_cfdis = 1247
        elif last in "13579":
            estado = ESTADO_EN_PROCESO
            paquetes = []
            numero_cfdis = 0
        else:
            estado = ESTADO_ACEPTADA
            paquetes = []
            numero_cfdis = 0

        return mark_simulated({
            "id_solicitud": id_solicitud,
            "cod_estatus_solicitud": estado,
            "estado_legible": parsear_estado_solicitud(estado),
            "es_terminal": estado_es_terminal(estado),
            "numero_cfdis": numero_cfdis,
            "paquetes": paquetes,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_descargar(self, id_paquete: str) -> dict[str, Any]:
        # Base64 trivial de un "ZIP" simulado
        zip_b64_mock = "UEsDBBQAAAAIAA=="  # header de ZIP truncado
        return mark_simulated({
            "id_paquete": id_paquete,
            "zip_base64": zip_b64_mock,
            "cfdis_estimados": 1000,
            "fecha_descarga": datetime.now(timezone.utc).isoformat(),
        })
