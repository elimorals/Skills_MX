"""Cliente IMPI — búsqueda de marcas.

Path real: API JSON de MARCia (https://marcia.impi.gob.mx/, ver `marcia.py`),
sin CAPTCHA. ViDoc (vidoc.impi.gob.mx) exige token reCAPTCHA v3 y ya no se usa.
Mock solo con PLUGINS_MX_MOCK=1. Errores → UpstreamError.

Cache 30 días por query.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from mp_impi_marcanet import marcia  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.impi_vidoc import MarcaIMPI, validar_query  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402

PORTAL_URL = marcia.PORTAL_URL


NAMESPACE = "impi_marcanet"
CACHE_TTL_HOURS = 24 * 30  # 30 días
MAX_LIMITE = 100
DEFAULT_LIMITE = 20


class ImpiMarcanetClient:
    """Cliente búsqueda de marcas IMPI (MARCia)."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ============================================================
    # Tool principal
    # ============================================================

    def buscar(
        self,
        query: str,
        limite: int = DEFAULT_LIMITE,
        incluir_raw: bool = False,
    ) -> dict[str, Any]:
        """Búsqueda en el padrón IMPI (marcas, patentes, diseños, asuntos).

        Args:
            query: término a buscar (ej. "TELMEX", "BIMBO", "RELLAMADO").
            limite: máx resultados a devolver. Default 20, máx 100.
            incluir_raw: si True, incluye `raw_ficha_normalizada` por cada
                resultado (campos completos no mapeados al schema tipado).

        Returns:
            {
              "query": str,
              "total_encontrados": int,        # total real del padrón
              "devueltos": int,                # cuántos devolvemos
              "resultados": [MarcaIMPI.to_dict(), ...],
              "fecha_consulta": ISO-8601 UTC,
              "fuente": URL portal,
              "modo": "mock" | "playwright" | "cache",
              "simulated": bool,
            }
        """
        query_norm = validar_query(query)
        if not 1 <= limite <= MAX_LIMITE:
            raise ValidationError(
                f"limite={limite} fuera de rango [1, {MAX_LIMITE}].",
                {"limite": limite},
            )

        cache_key = f"buscar:{query_norm}:{limite}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._bitacora.log(
                "buscar",
                success=True,
                params_summary={"query": query_norm, "limite": limite, "cache": "hit"},
            )
            return {**cached, "modo": "cache"}

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            result = self._mock_buscar(query_norm, limite)
        else:
            result = self._buscar_real(query_norm, limite)

        if not incluir_raw:
            for r in result.get("resultados", []):
                r.pop("raw_ficha_normalizada", None)

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "buscar",
            success=True,
            params_summary={
                "query": query_norm,
                "limite": limite,
                "devueltos": result.get("devueltos", 0),
                "cache": "miss",
                "modo": result.get("modo"),
            },
        )
        return result

    # ============================================================
    # Verificación de denominación disponible
    # ============================================================

    def verificar_denominacion(self, denominacion: str) -> dict[str, Any]:
        """Tool de alto nivel: ¿esta denominación parece estar registrada?

        Args:
            denominacion: nombre comercial que un usuario quiere registrar.

        Returns:
            {
              "denominacion": str (normalizada),
              "tiene_coincidencias": bool,
              "coincidencias_exactas": int,
              "coincidencias_similares": int,
              "ejemplos": [MarcaIMPI.to_dict(), ... top 5],
              "advertencias": [str]
            }

        Util para legaltech / startups que evalúan si una marca es
        registrable antes de pagar el trámite IMPI.
        """
        denom_norm = validar_query(denominacion)
        resultado = self.buscar(query=denom_norm, limite=20)
        coincidencias = resultado["resultados"]

        exactas = sum(
            1 for r in coincidencias
            if (r.get("denominacion") or "").upper().strip() == denom_norm
        )
        similares = len(coincidencias) - exactas

        advertencias: list[str] = []
        if exactas > 0:
            advertencias.append(
                f"⚠️ Existen {exactas} marca(s) con denominación EXACTA "
                f"a '{denom_norm}'. Registro probablemente bloqueado."
            )
        if similares > 0:
            advertencias.append(
                f"Existen {similares} marca(s) con denominación similar. "
                "Considera análisis legal de posible confusión fonética."
            )
        if not coincidencias:
            advertencias.append(
                "Sin coincidencias directas. Sin embargo, IMPI evalúa similitud "
                "fonética/gráfica/conceptual — no es garantía de registrabilidad."
            )

        return {
            "denominacion": denom_norm,
            "tiene_coincidencias": exactas + similares > 0,
            "coincidencias_exactas": exactas,
            "coincidencias_similares": similares,
            "ejemplos": coincidencias[:5],
            "advertencias": advertencias,
            "fuente": PORTAL_URL,
            "fecha_consulta": resultado.get("fecha_consulta"),
            "modo": resultado.get("modo"),
        }

    # ============================================================
    # Path real: MARCia
    # ============================================================

    @staticmethod
    def _buscar_real(query: str, limite: int) -> dict[str, Any]:
        r = marcia.buscar(query, limite)
        resultados = [marcia.mapear(i) for i in r["items"][:limite]]
        return {
            "query": query,
            "total_encontrados": r["total"],
            "devueltos": len(resultados),
            "resultados": resultados,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": PORTAL_URL,
            "modo": "marcia",
            "simulated": False,
        }

    # ============================================================
    # Mock path (default)
    # ============================================================

    def _mock_buscar(self, query: str, limite: int) -> dict[str, Any]:
        """Respuestas simuladas para CI/dev.

        Devuelve 0, 1 o 3 resultados según la longitud del query, para que
        los tests puedan ejercitar todos los caminos (vacío, una marca, varias).
        """
        if len(query) <= 2:
            marcas: list[MarcaIMPI] = []
        elif len(query) <= 5:
            marcas = [self._mock_marca(query, idx=0)]
        else:
            marcas = [self._mock_marca(query, idx=i) for i in range(3)]

        devueltos = marcas[:limite]
        out = {
            "query": query,
            "total_encontrados": len(marcas),
            "devueltos": len(devueltos),
            "resultados": [m.to_dict() for m in devueltos],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": PORTAL_URL,
            "modo": "mock",
        }
        return mark_simulated(out)

    @staticmethod
    def _mock_marca(query: str, idx: int) -> MarcaIMPI:
        """Construye un MarcaIMPI ejemplo determinístico."""
        nombres_titular = [
            "TELEFONOS DE MEXICO, S.A.B. DE C.V.",
            "GRUPO BIMBO, S.A.B. DE C.V.",
            "CEMEX, S.A.B. DE C.V.",
        ]
        denominaciones = [
            f"{query}",
            f"{query} PREMIUM",
            f"RELLAMADO {query}",
        ]
        clases = ["38", "30", "19"]
        return MarcaIMPI(
            expediente=f"MA/M/1985/{3500000 + idx}",
            numero_expediente=str(3500000 + idx),
            area="MARCAS",
            anio=2025,
            tipo_expediente="MARCA",
            denominacion=denominaciones[idx % 3],
            titular=nombres_titular[idx % 3],
            titular_nacionalidad="MEXICO",
            titular_estado="CUAUHTEMOC, CIUDAD DE MEXICO",
            clase_niza=clases[idx % 3],
            tipo_descripcion="DENOMINACION",
            fecha="2025-11-11T14:21:29",
            raw_ficha_normalizada={"denominacion": denominaciones[idx % 3]},
        )
