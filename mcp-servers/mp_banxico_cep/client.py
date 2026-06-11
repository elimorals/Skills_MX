"""Cliente CEP (Constancia de Pago Electrónico) — Banxico.

⚠ Banxico NO expone API REST oficial. La consulta CEP está en
https://www.banxico.org.mx/cep/ y requiere POST de form-data + parseo HTML.
Eventualmente también CAPTCHA en algunos endpoints.

Este cliente implementa:
1. **Modo mock determinístico** (default): genera CEPs plausibles cuya respuesta
   se deriva del hash SHA-256 de la clave de rastreo. La misma clave siempre
   produce el mismo CEP en mock — ideal para tests y desarrollo.

2. **Modo real**: TODO — requiere Playwright + parseo HTML. Por ahora devuelve
   `not_implemented_error` con guía de qué hace falta.

Cache: CEP por clave_rastreo se cachea 90 días (los datos del padrón histórico
SPEI no cambian). Consultas por clave (sin generar PDF) se cachean 30 días.
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_banxico_cep.catalogos import BANCOS_CLABE, ESTADO_CEP, lookup_banco  # noqa: E402
from mp_banxico_cep.clabe import parsear_clave_rastreo  # noqa: E402
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402

NAMESPACE = "banxico_cep_mcp"
CACHE_CEP_DIAS = 90
CACHE_CONSULTA_DIAS = 30


class _NotImplementedError(McpError):
    """Integración Playwright al portal CEP de Banxico está pendiente."""

    code = "not_implemented_error"


class BanxicoCepClient:
    """Cliente para generar y validar CEP de pagos SPEI."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif os.environ.get("BANXICO_CEP_PLAYWRIGHT") == "1":
            self._mock_mode = False
        else:
            # Default: mock (Banxico no tiene API y Playwright todavía no integrado)
            self._mock_mode = True

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    # ---------- generar_cep ----------

    async def generar_cep(
        self,
        clave_rastreo: str,
        fecha_operacion: date,
        banco_emisor: str,
        banco_receptor: str,
        monto: float,
    ) -> dict[str, Any]:
        """Solicita CEP a Banxico con los datos del SPEI.

        Args:
            clave_rastreo: cadena alfanumérica del banco emisor.
            fecha_operacion: fecha en que se ejecutó el SPEI.
            banco_emisor: código 3 dígitos.
            banco_receptor: código 3 dígitos.
            monto: monto exacto del pago.

        Returns:
            Dict con datos del CEP + URL del PDF + estado.
        """
        self._validar_datos_basicos(banco_emisor, banco_receptor, monto, clave_rastreo)

        cache_key = self._cache_key_cep(
            clave_rastreo, fecha_operacion, banco_emisor, banco_receptor, monto
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_cep(
                clave_rastreo, fecha_operacion, banco_emisor, banco_receptor, monto
            )
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_CEP_DIAS)
            self._bitacora.log(
                "generar_cep",
                success=True,
                params_summary={
                    "clave_hash": Bitacora.hash_sensitive(clave_rastreo),
                    "fecha": fecha_operacion.isoformat(),
                    "banco_emisor": banco_emisor,
                    "banco_receptor": banco_receptor,
                    "monto": monto,
                    "mode": "mock",
                },
            )
            return response

        raise _NotImplementedError(
            "Generación CEP real (POST a banxico.org.mx/cep/) requiere "
            "integración Playwright + parseo HTML. Pendiente. Mientras tanto, "
            "usar modo mock (sin BANXICO_CEP_PLAYWRIGHT=1)."
        )

    # ---------- validar_cep ----------

    async def validar_cep(self, clave_rastreo: str) -> dict[str, Any]:
        """Verifica si un CEP existe (sin volver a generarlo).

        Más liviano que generar_cep — solo confirma existencia.
        """
        cache_key = f"validar_{clave_rastreo.upper()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        parseo = parsear_clave_rastreo(clave_rastreo)
        if not parseo["formato_valido"]:
            raise ValidationError(
                f"Clave de rastreo con formato inválido. Alertas: {parseo['alertas']}"
            )

        if self._mock_mode:
            # Heurística determinística: claves cuyo hash[0] es par → existe, impar → no
            seed = int(hashlib.sha256(clave_rastreo.encode()).hexdigest()[0], 16)
            existe = seed % 2 == 0
            response = mark_simulated(
                {
                    "clave_rastreo": clave_rastreo,
                    "existe_en_banxico": existe,
                    "estado": "disponible" if existe else "no_encontrado",
                    "estado_descripcion": ESTADO_CEP[
                        "disponible" if existe else "no_encontrado"
                    ],
                    "consultado_en": datetime.now(timezone.utc).isoformat(),
                    "emisor_probable": parseo["emisor_probable"],
                }
            )
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_CONSULTA_DIAS)
            return response

        raise _NotImplementedError(
            "Validación CEP real requiere Playwright. Pendiente."
        )

    # ---------- descargar_pdf ----------

    async def descargar_pdf_cep(
        self,
        clave_rastreo: str,
        fecha_operacion: date,
        banco_emisor: str,
        banco_receptor: str,
        monto: float,
    ) -> dict[str, Any]:
        """Descarga el PDF oficial del CEP. En mock devuelve metadata simulada."""
        self._validar_datos_basicos(banco_emisor, banco_receptor, monto, clave_rastreo)

        if self._mock_mode:
            cep = await self.generar_cep(
                clave_rastreo, fecha_operacion, banco_emisor, banco_receptor, monto
            )
            return mark_simulated(
                {
                    "clave_rastreo": clave_rastreo,
                    "pdf_path": f"/mock/cep/{clave_rastreo.upper()}.pdf",
                    "pdf_bytes": 0,
                    "cep_disponible": cep["cep_disponible"],
                    "nota": (
                        "Modo mock — no se generó PDF real. En modo Playwright "
                        "habría descargado el PDF y lo habría persistido en cache."
                    ),
                }
            )

        raise _NotImplementedError(
            "Descarga PDF CEP real requiere Playwright. Pendiente."
        )

    # ---------- consultar_pago_por_clave ----------

    async def consultar_pago_por_clave(self, clave_rastreo: str) -> dict[str, Any]:
        """Variante simplificada: dado solo una clave de rastreo, intenta consultar.

        Útil cuando el cliente solo manda la clave por WhatsApp y el agente
        todavía no sabe banco/fecha/monto exactos. En mock infiere lo que puede.
        En real (Playwright), Banxico exige todos los campos — esta función
        devolverá `validation_error` indicando qué falta.
        """
        parseo = parsear_clave_rastreo(clave_rastreo)
        if not parseo["formato_valido"]:
            raise ValidationError(
                f"Clave de rastreo con formato inválido. Alertas: {parseo['alertas']}"
            )

        if self._mock_mode:
            # En mock infiere todo desde el hash de la clave para tener algo plausible
            seed_hex = hashlib.sha256(clave_rastreo.encode()).hexdigest()
            monto_mock = round(100.0 + int(seed_hex[:6], 16) % 50000 / 100.0, 2)
            return mark_simulated(
                {
                    "clave_rastreo": clave_rastreo,
                    "emisor_probable": parseo["emisor_probable"],
                    "monto_estimado_mock": monto_mock,
                    "nota": (
                        "Modo mock — datos derivados algorítmicamente de la clave. "
                        "Para CEP real necesitas fecha + bancos + monto. Llama a "
                        "generar_cep con esos datos."
                    ),
                }
            )

        raise ValidationError(
            "Banxico CEP exige fecha_operacion, banco_emisor, banco_receptor y monto "
            "para emitir un CEP. La clave de rastreo sola no es suficiente. "
            "Recopila esos datos del cliente y llama a generar_cep."
        )

    # ---------- helpers ----------

    @staticmethod
    def _validar_datos_basicos(
        banco_emisor: str,
        banco_receptor: str,
        monto: float,
        clave_rastreo: str,
    ) -> None:
        if not lookup_banco(banco_emisor):
            raise ValidationError(
                f"Banco emisor '{banco_emisor}' no está en el catálogo conocido. "
                "Verificar código de 3 dígitos contra catalogos.BANCOS_CLABE."
            )
        if not lookup_banco(banco_receptor):
            raise ValidationError(
                f"Banco receptor '{banco_receptor}' no está en el catálogo conocido."
            )
        if monto <= 0:
            raise ValidationError("Monto debe ser positivo.")
        if not parsear_clave_rastreo(clave_rastreo)["formato_valido"]:
            raise ValidationError(
                f"Clave de rastreo con formato inválido: '{clave_rastreo}'."
            )

    @staticmethod
    def _cache_key_cep(
        clave: str, fecha: date, emisor: str, receptor: str, monto: float
    ) -> str:
        # Hash compacto de los identificadores — la combinación es única por SPEI
        raw = f"{clave}|{fecha.isoformat()}|{emisor}|{receptor}|{monto:.2f}".upper()
        h = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return f"cep_{h}"

    @staticmethod
    def _mock_cep(
        clave: str, fecha: date, emisor: str, receptor: str, monto: float
    ) -> dict[str, Any]:
        """Construye una respuesta CEP determinística para tests/mock."""
        seed = hashlib.sha256(clave.encode()).hexdigest()
        hora_seed = int(seed[6:8], 16) % 24
        min_seed = int(seed[8:10], 16) % 60
        seg_seed = int(seed[10:12], 16) % 60
        cuenta_ord = "**** " + seed[12:16]
        cuenta_ben = "**** " + seed[16:20]

        return mark_simulated(
            {
                "clave_rastreo": clave,
                "fecha_operacion": fecha.isoformat(),
                "hora_operacion": f"{hora_seed:02d}:{min_seed:02d}:{seg_seed:02d}",
                "banco_emisor": {
                    "clave": emisor,
                    "nombre": lookup_banco(emisor),
                },
                "banco_receptor": {
                    "clave": receptor,
                    "nombre": lookup_banco(receptor),
                },
                "monto": round(monto, 2),
                "moneda": "MXN",
                "ordenante": {
                    "nombre": "ORDENANTE MOCK",
                    "cuenta_enmascarada": cuenta_ord,
                },
                "beneficiario": {
                    "nombre": "BENEFICIARIO MOCK",
                    "cuenta_enmascarada": cuenta_ben,
                },
                "concepto": "Pago referencia mock",
                "referencia": seed[:8],
                "cep_disponible": True,
                "estado": "disponible",
                "estado_descripcion": ESTADO_CEP["disponible"],
                "pdf_url": f"https://www.banxico.org.mx/cep/?mock={seed[:12]}",
                "generado_en": datetime.now(timezone.utc).isoformat(),
            }
        )
