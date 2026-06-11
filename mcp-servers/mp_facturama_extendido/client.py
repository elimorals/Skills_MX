"""Async client for Facturama PAC API.

API docs: https://apisandbox.facturama.mx/guias/api-multi
Production base: https://api.facturama.mx
Sandbox base:    https://apisandbox.facturama.mx

Auth: HTTP Basic with username:password (or API key as username).

This client wraps Facturama's REST surface with:
- Mock mode (no creds → synthetic UUIDs + sello)
- Cache for read ops (consulta status, etc.)
- Bitácora of every timbrado + cancelación
- Typed errors via shared.errors

Tools implemented at this layer (server.py exposes them as MCP tools):
- timbrar_cfdi
- cancelar_cfdi
- consultar_estatus
- get_cfdi_xml / get_cfdi_pdf
- buscar_cfdis
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# Make shared/ importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    ConfigError,
    McpError,
    NotFoundError,
    UpstreamError,
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "facturama_mcp"

FACTURAMA_PROD_URL = "https://api.facturama.mx"
FACTURAMA_SANDBOX_URL = "https://apisandbox.facturama.mx"
REQUEST_TIMEOUT_S = 30.0


class FacturamaClient:
    """Async client over Facturama API with mock fallback + cache + bitácora."""

    def __init__(
        self,
        user: str | None = None,
        password: str | None = None,
        environment: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit_creds = user is not None or password is not None
        if user is None:
            user = os.environ.get("FACTURAMA_USER") or os.environ.get("FACTURAMA_API_KEY") or None
        if password is None:
            password = os.environ.get("FACTURAMA_PASSWORD") or None
        if environment is None:
            environment = os.environ.get("FACTURAMA_ENV", "sandbox")

        self._user = user
        self._password = password
        self._environment = environment.lower() if environment else "sandbox"
        self._base_url = (
            FACTURAMA_PROD_URL if self._environment == "production" else FACTURAMA_SANDBOX_URL
        )

        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        # Mock decision: PLUGINS_MX_MOCK=1 always wins; explicit creds → real;
        # otherwise check env vars
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicit_creds or (self._user and self._password):
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["FACTURAMA_USER", "FACTURAMA_API_KEY"])

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    @property
    def environment(self) -> str:
        return self._environment

    @property
    def base_url(self) -> str:
        return self._base_url

    # ---------- timbrado ----------

    async def timbrar_cfdi(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Timbra un CFDI 4.0 contra Facturama.

        En modo real, hace POST a /api/3/cfdis con auth Basic.
        En modo mock, devuelve un UUID + sello plausibles.

        Returns:
            dict con uuid, fecha_timbrado, sello_sat, sello_emisor,
            cadena_original_complemento, xml_base64 (en real), simulated.
        """
        # Mock mode
        if self._mock_mode:
            response = self._mock_timbrar(payload)
            self._bitacora.log(
                "timbrar_cfdi",
                success=True,
                params_summary={
                    "emisor_rfc_hash": Bitacora.hash_sensitive(payload.get("emisor", {}).get("rfc")),
                    "receptor_rfc_hash": Bitacora.hash_sensitive(payload.get("receptor", {}).get("rfc")),
                    "tipo": payload.get("comprobante", {}).get("tipo_comprobante"),
                    "mode": "mock",
                },
                result_summary={"uuid": response["uuid"]},
            )
            return response

        # Real mode
        if not self._user or not self._password:
            raise ConfigError(
                "Facturama: configura FACTURAMA_USER y FACTURAMA_PASSWORD para modo real. "
                "Sandbox gratis en https://www.facturama.mx",
            )

        url = f"{self._base_url}/api/3/cfdis"
        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(
                    url,
                    auth=(self._user, self._password),
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "timbrar_cfdi",
                success=False,
                duration_ms=_now_ms() - start,
                params_summary={
                    "emisor_rfc_hash": Bitacora.hash_sensitive(payload.get("emisor", {}).get("rfc")),
                    "mode": "real",
                    "env": self._environment,
                },
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        response = self._parse_timbrado_response(body)
        self._bitacora.log(
            "timbrar_cfdi",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "emisor_rfc_hash": Bitacora.hash_sensitive(payload.get("emisor", {}).get("rfc")),
                "receptor_rfc_hash": Bitacora.hash_sensitive(payload.get("receptor", {}).get("rfc")),
                "mode": "real",
                "env": self._environment,
            },
            result_summary={"uuid": response.get("uuid")},
        )
        return response

    # ---------- cancelación ----------

    async def cancelar_cfdi(
        self,
        uuid: str,
        motivo: str,
        folio_sustituto: str | None = None,
    ) -> dict[str, Any]:
        """Cancela un CFDI por UUID.

        En modo mock devuelve respuesta plausible. En real hace DELETE a
        /api/cfdi/{uuid} con query params motivo + folio_sustituto.
        """
        if self._mock_mode:
            response = self._mock_cancelar(uuid, motivo, folio_sustituto)
            self._bitacora.log(
                "cancelar_cfdi",
                success=True,
                params_summary={
                    "uuid_hash": Bitacora.hash_sensitive(uuid),
                    "motivo": motivo,
                    "mode": "mock",
                },
                result_summary={"estatus": response.get("estatus")},
            )
            return response

        if not self._user or not self._password:
            raise ConfigError("Facturama: configura FACTURAMA_USER y FACTURAMA_PASSWORD.")

        url = f"{self._base_url}/api/cfdi/{uuid}"
        params: dict[str, str] = {"motive": motivo}
        if folio_sustituto:
            params["uuidReplacement"] = folio_sustituto

        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.delete(
                    url,
                    auth=(self._user, self._password),
                    params=params,
                )
                resp.raise_for_status()
                body = resp.json() if resp.text else {}
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "cancelar_cfdi",
                success=False,
                duration_ms=_now_ms() - start,
                params_summary={
                    "uuid_hash": Bitacora.hash_sensitive(uuid),
                    "motivo": motivo,
                    "mode": "real",
                },
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        result = {
            "uuid": uuid,
            "motivo": motivo,
            "folio_sustituto": folio_sustituto,
            "estatus": body.get("Status") or "Solicitud de cancelación enviada",
            "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
            "raw_response": body,
            "simulated": False,
        }
        self._bitacora.log(
            "cancelar_cfdi",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "uuid_hash": Bitacora.hash_sensitive(uuid),
                "motivo": motivo,
                "mode": "real",
            },
            result_summary={"estatus": result["estatus"]},
        )
        return result

    # ---------- consultas ----------

    async def consultar_estatus(self, uuid: str) -> dict[str, Any]:
        """Consulta el estatus actual de un CFDI."""
        cache_key = f"estatus_{uuid}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = {
                "uuid": uuid,
                "estatus": "Vigente",
                "consultado_en": datetime.now(timezone.utc).isoformat(),
                "simulated": True,
                "advertencias": ["Estatus simulado — en producción consultar contra SAT directamente."],
            }
            self._cache.set(cache_key, response, ttl_minutes=15)
            return response

        if not self._user or not self._password:
            raise ConfigError("Facturama: configura FACTURAMA_USER y FACTURAMA_PASSWORD.")

        url = f"{self._base_url}/api/cfdi/status/{uuid}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, auth=(self._user, self._password))
                if resp.status_code == 404:
                    raise NotFoundError(f"CFDI con UUID {uuid} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {
            "uuid": uuid,
            "estatus": body.get("Status", "Desconocido"),
            "consultado_en": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
            "raw_response": body,
        }
        self._cache.set(cache_key, response, ttl_minutes=15)
        return response

    async def buscar_cfdis(
        self,
        rfc_receptor: str | None = None,
        rfc_emisor: str | None = None,
        folio: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        tipo: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Busca CFDIs por filtros (RFC, fechas, tipo).

        Real: GET /api/cfdi con query params.
        Mock: devuelve lista vacía con flag simulated.
        """
        if self._mock_mode:
            return mark_simulated(
                {"cfdis": [], "total": 0, "filtros_aplicados": {"limit": limit}},
                note="Búsqueda simulada — no devuelve resultados reales.",
            )

        if not self._user or not self._password:
            raise ConfigError("Facturama: configura FACTURAMA_USER y FACTURAMA_PASSWORD.")

        url = f"{self._base_url}/api/cfdi"
        params: dict[str, str] = {}
        if rfc_receptor:
            params["rfc"] = rfc_receptor
        if folio:
            params["folio"] = folio
        if fecha_desde:
            params["dateFrom"] = fecha_desde
        if fecha_hasta:
            params["dateTo"] = fecha_hasta
        if tipo:
            params["type"] = tipo
        params["limit"] = str(limit)

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, auth=(self._user, self._password), params=params)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        items = body if isinstance(body, list) else body.get("Items", [])
        return {
            "cfdis": items,
            "total": len(items),
            "filtros_aplicados": params,
            "simulated": False,
        }

    # ---------- descargas ----------

    async def descargar_xml(self, uuid: str) -> dict[str, Any]:
        """Descarga el XML de un CFDI por UUID.

        Real: GET /api/cfdi/xml/{uuid}.
        Mock: XML sintético plausible.
        """
        if self._mock_mode:
            xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<cfdi:Comprobante UUID="{uuid}">(mock CFDI XML)</cfdi:Comprobante>'
            return mark_simulated({"uuid": uuid, "xml": xml, "size_bytes": len(xml)})

        if not self._user or not self._password:
            raise ConfigError("Facturama: configura FACTURAMA_USER y FACTURAMA_PASSWORD.")

        url = f"{self._base_url}/api/cfdi/xml/issued/{uuid}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, auth=(self._user, self._password))
                if resp.status_code == 404:
                    raise NotFoundError(f"XML no encontrado para UUID {uuid}.")
                resp.raise_for_status()
                # Facturama puede devolver el XML como base64 dentro de JSON o como texto
                if resp.headers.get("content-type", "").startswith("application/json"):
                    body = resp.json()
                    xml = body.get("Content", "")
                else:
                    xml = resp.text
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {"uuid": uuid, "xml": xml, "size_bytes": len(xml), "simulated": False}

    async def descargar_pdf(self, uuid: str) -> dict[str, Any]:
        """Descarga el PDF de representación impresa.

        Real: GET /api/cfdi/pdf/{uuid}. Devuelve base64 del PDF.
        Mock: devuelve placeholder.
        """
        if self._mock_mode:
            return mark_simulated(
                {
                    "uuid": uuid,
                    "pdf_base64": "JVBERi0xLjMKJcfsj6IK",  # tiny valid PDF header
                    "note": "PDF mock — no es un PDF real válido.",
                }
            )

        if not self._user or not self._password:
            raise ConfigError("Facturama: configura FACTURAMA_USER y FACTURAMA_PASSWORD.")

        url = f"{self._base_url}/api/cfdi/pdf/issued/{uuid}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, auth=(self._user, self._password))
                if resp.status_code == 404:
                    raise NotFoundError(f"PDF no encontrado para UUID {uuid}.")
                resp.raise_for_status()
                body = resp.json()
                pdf_b64 = body.get("Content", "") if isinstance(body, dict) else ""
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {"uuid": uuid, "pdf_base64": pdf_b64, "simulated": False}

    # ---------- mock helpers ----------

    @staticmethod
    def _mock_timbrar(payload: dict) -> dict[str, Any]:
        """Genera respuesta mock plausible para timbrado.

        UUID con formato 8-4-4-4-12 hex válido; sello sha256 sobre payload
        para que llamadas con mismo payload den el mismo sello (deterministic
        en tests).
        """
        uuid = _generate_uuid_v4_like()
        sello = _hash_payload(payload)
        ahora = datetime.now(timezone.utc).replace(microsecond=0)

        emisor_rfc = payload.get("emisor", {}).get("rfc", "AAAA010101AAA")

        return mark_simulated(
            {
                "uuid": uuid,
                "fecha_timbrado": ahora.isoformat(),
                "sello_sat": sello,
                "sello_emisor": sello[:128],
                "cadena_original_complemento": (
                    f"||1.1|{uuid}|{ahora.isoformat()}|"
                    f"AAA010101AAA|{sello[:8]}|0001||"
                ),
                "xml_base64": "PHhtbCBtb2NrPjwveG1sPg==",  # "<xml mock></xml>"
                "no_certificado_sat": "30001000000400002495",
                "rfc_proveedor_certificacion": "FAKE_PAC_RFC",
            },
            note="Timbrado SIMULADO — UUID no es válido ante SAT.",
        )

    @staticmethod
    def _mock_cancelar(uuid: str, motivo: str, folio_sustituto: str | None) -> dict[str, Any]:
        """Mock de respuesta de cancelación."""
        return mark_simulated(
            {
                "uuid": uuid,
                "motivo": motivo,
                "folio_sustituto": folio_sustituto,
                "estatus": "Solicitud de cancelación enviada (simulado)",
                "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
                "requiere_aceptacion_receptor": True,
                "plazo_respuesta_receptor": "3 días hábiles",
                "default_si_no_responde": "se considera aceptada",
            }
        )

    @staticmethod
    def _parse_timbrado_response(body: dict[str, Any]) -> dict[str, Any]:
        """Convierte respuesta Facturama a estructura estándar.

        Facturama devuelve un JSON con muchos campos. Extraemos los críticos.
        """
        # Estructura típica Facturama: Id (UUID), Date, Status, Complement.TimbreFiscalDigital
        complement = body.get("Complement", {}) or {}
        tfd = complement.get("TimbreFiscalDigital", {}) or {}

        return {
            "uuid": body.get("Id") or tfd.get("UUID"),
            "fecha_timbrado": tfd.get("Date") or body.get("Date"),
            "sello_sat": tfd.get("SatSeal"),
            "sello_emisor": tfd.get("CfdiSeal"),
            "cadena_original_complemento": tfd.get("OriginalString"),
            "no_certificado_sat": tfd.get("SatCertNumber"),
            "rfc_proveedor_certificacion": tfd.get("RfcProvCertif"),
            "xml_base64": body.get("ContentEncoding"),
            "simulated": False,
            "raw_response": body,
        }


# ---------- module-level helpers ----------


def _generate_uuid_v4_like() -> str:
    """Genera string con formato UUID v4 (válido sintácticamente)."""
    h = secrets.token_hex(16)
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _hash_payload(payload: dict) -> str:
    """SHA256 del payload serializado canónicamente. Deterministic."""
    import json

    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _now_ms() -> float:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.time() * 1000
    except RuntimeError:
        pass
    return 0.0
