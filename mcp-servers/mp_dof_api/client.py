"""Cliente mp_dof_api — Diario Oficial de la Federación.

3 endpoints validados Playwright MCP 2026-06-14:

1. **sumario_dia(fecha)** — Notas publicadas un día concreto
2. **buscar_texto(texto, [desde, hasta])** — Búsqueda full-text histórica
3. **detalle_nota(codigo, fecha)** — Texto completo + metadatos de una nota

Cache 90 días (publicaciones DOF son inmutables — una vez publicado, no se modifica).

Modo mock por default. Real: setear MP_DOF_REAL=1 (sin credenciales — portal público).
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    McpError,
    NotFoundError,
    UpstreamError,
    ValidationError,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "dof_api"

URL_BASE = "https://www.dof.gob.mx"
URL_SUMARIO = URL_BASE + "/index_111.php?year={year}&month={month:02d}&day={day:02d}"
URL_NOTA = URL_BASE + "/nota_detalle.php?codigo={codigo}&fecha={fecha}"
URL_BUSQUEDA = URL_BASE + "/busqueda_detalle.php"

# Validación fecha DD/MM/YYYY (formato DOF)
FECHA_DOF_REGEX = re.compile(r"^\d{2}/\d{2}/\d{4}$")
# Validación código (7 dígitos típicamente, range 1-8 dígitos)
CODIGO_REGEX = re.compile(r"^\d{4,8}$")

# Dependencias frecuentes para clasificación
DEPENDENCIAS = {
    "SHCP": "Secretaría de Hacienda y Crédito Público",
    "SAT": "Servicio de Administración Tributaria",
    "BANXICO": "Banco de México",
    "CNBV": "Comisión Nacional Bancaria y de Valores",
    "STPS": "Secretaría del Trabajo y Previsión Social",
    "IMSS": "Instituto Mexicano del Seguro Social",
    "INFONAVIT": "Instituto del Fondo Nacional de la Vivienda para los Trabajadores",
    "COFEPRIS": "Comisión Federal para la Protección contra Riesgos Sanitarios",
    "PROFECO": "Procuraduría Federal del Consumidor",
    "IMPI": "Instituto Mexicano de la Propiedad Industrial",
    "SEMARNAT": "Secretaría de Medio Ambiente y Recursos Naturales",
    "SEP": "Secretaría de Educación Pública",
    "SSA": "Secretaría de Salud",
    "CRE": "Comisión Reguladora de Energía",
    "CNH": "Comisión Nacional de Hidrocarburos",
}


class DofApiClient:
    """Cliente DOF — scraping HTML simple, sin auth."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if os.environ.get("MP_DOF_REAL") == "1":
            return False
        return is_mock_mode(credential_env_vars=[])

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    # ============================================================
    # Tools principales
    # ============================================================

    def sumario_dia(self, fecha: str) -> dict[str, Any]:
        """Devuelve todas las notas publicadas un día específico.

        Args:
            fecha: formato DD/MM/YYYY (ej. "12/06/2026")

        Returns:
            {
              "fecha": "DD/MM/YYYY",
              "url_consultado": "...",
              "total_notas": int,
              "notas": [
                {
                  "codigo": "5790442",
                  "titulo": "Acuerdo por el que...",
                  "dependencia": "SHCP",
                  "seccion": "PODER EJECUTIVO",
                  "url_detalle": "https://...nota_detalle.php?codigo=...",
                }
              ],
              "simulated": bool
            }
        """
        fecha_dt = self._parsear_fecha(fecha)
        fecha_iso = fecha_dt.strftime("%Y-%m-%d")
        fecha_dof = fecha_dt.strftime("%d/%m/%Y")

        cache_key = f"sumario_{fecha_iso}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("sumario_dia", {"fecha": fecha_dof})

        url = URL_SUMARIO.format(year=fecha_dt.year, month=fecha_dt.month, day=fecha_dt.day)

        if self._is_mock():
            resultado = self._mock_sumario(fecha_dof, url)
        else:
            resultado = self._sumario_real(fecha_dt, url)

        self._cache.set(cache_key, resultado, ttl_days=90)
        return resultado

    def buscar_texto(
        self,
        texto: str,
        desde: Optional[str] = None,
        hasta: Optional[str] = None,
        limite: int = 20,
    ) -> dict[str, Any]:
        """Búsqueda full-text en el DOF.

        Args:
            texto: término a buscar
            desde: fecha DD/MM/YYYY (default: hace 10 años)
            hasta: fecha DD/MM/YYYY (default: hoy)
            limite: máx resultados (1-100)

        Returns:
            {
              "texto_buscado": str,
              "periodo": {"desde": str, "hasta": str},
              "total_resultados": int,
              "resultados": [{codigo, titulo, dependencia, fecha, url_detalle}],
              "url_consultado": "...",
            }
        """
        if not texto or len(texto.strip()) < 3:
            raise ValidationError("texto debe tener al menos 3 caracteres.")
        if limite < 1 or limite > 100:
            raise ValidationError("limite entre 1 y 100.")

        # Default: últimos 10 años
        if not hasta:
            hasta_dt = date.today()
        else:
            hasta_dt = self._parsear_fecha(hasta).date()
        if not desde:
            desde_dt = hasta_dt - timedelta(days=365 * 10)
        else:
            desde_dt = self._parsear_fecha(desde).date()

        if desde_dt > hasta_dt:
            raise ValidationError("desde debe ser anterior a hasta.")

        cache_key = (
            f"busq_{texto[:30].replace(' ', '_')}_"
            f"{desde_dt.isoformat()}_{hasta_dt.isoformat()}_{limite}"
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("buscar_texto", {
            "texto": texto[:30], "desde": str(desde_dt), "hasta": str(hasta_dt),
            "limite": limite,
        })

        if self._is_mock():
            resultado = self._mock_busqueda(texto, desde_dt, hasta_dt, limite)
        else:
            resultado = self._busqueda_real(texto, desde_dt, hasta_dt, limite)

        self._cache.set(cache_key, resultado, ttl_days=30)
        return resultado

    def detalle_nota(self, codigo: str, fecha: str) -> dict[str, Any]:
        """Devuelve texto completo + metadatos de una nota DOF.

        Args:
            codigo: identificador numérico (4-8 dígitos, ej. "5790442")
            fecha: DD/MM/YYYY
        """
        if not CODIGO_REGEX.match(codigo):
            raise ValidationError(
                f"Código '{codigo}' inválido. Debe ser 4-8 dígitos numéricos."
            )
        fecha_dt = self._parsear_fecha(fecha)
        fecha_dof = fecha_dt.strftime("%d/%m/%Y")

        cache_key = f"nota_{codigo}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("detalle_nota", {"codigo": codigo, "fecha": fecha_dof})

        url = URL_NOTA.format(codigo=codigo, fecha=fecha_dof)

        if self._is_mock():
            resultado = self._mock_detalle(codigo, fecha_dof, url)
        else:
            resultado = self._detalle_real(codigo, fecha_dof, url)

        self._cache.set(cache_key, resultado, ttl_days=90)
        return resultado

    def monitorear_por_keyword(
        self,
        keywords: list[str],
        dias_atras: int = 7,
    ) -> dict[str, Any]:
        """Tool de alto nivel: monitorea N keywords en los últimos N días.

        Útil para compliance horizontal — vigilar cambios fiscales,
        sanciones a competidores, nuevas NOMs aplicables, etc.

        Returns:
            {
              "periodo": {"desde": str, "hasta": str},
              "keywords": [...],
              "hallazgos_por_keyword": {
                "keyword": [{codigo, titulo, fecha, dependencia, url}, ...]
              },
              "total_hallazgos": int,
            }
        """
        if not keywords:
            raise ValidationError("Debe pasar al menos 1 keyword.")
        if dias_atras < 1 or dias_atras > 365:
            raise ValidationError("dias_atras entre 1 y 365.")

        hasta_dt = date.today()
        desde_dt = hasta_dt - timedelta(days=dias_atras)

        hallazgos = {}
        total = 0
        for kw in keywords:
            try:
                r = self.buscar_texto(
                    texto=kw,
                    desde=desde_dt.strftime("%d/%m/%Y"),
                    hasta=hasta_dt.strftime("%d/%m/%Y"),
                    limite=20,
                )
                hallazgos[kw] = r["resultados"]
                total += len(r["resultados"])
            except (ValidationError, UpstreamError) as e:
                hallazgos[kw] = {"error": str(e)}

        return {
            "periodo": {
                "desde": desde_dt.strftime("%d/%m/%Y"),
                "hasta": hasta_dt.strftime("%d/%m/%Y"),
            },
            "keywords": keywords,
            "hallazgos_por_keyword": hallazgos,
            "total_hallazgos": total,
        }

    def listar_dependencias_comunes(self) -> dict[str, Any]:
        """Catálogo de dependencias frecuentes para clasificar notas."""
        return {
            "dependencias": DEPENDENCIAS,
            "total": len(DEPENDENCIAS),
        }

    # ============================================================
    # Helpers
    # ============================================================

    @staticmethod
    def _parsear_fecha(fecha: str) -> datetime:
        """Acepta DD/MM/YYYY (DOF) o YYYY-MM-DD (ISO)."""
        if not fecha:
            raise ValidationError("fecha es requerida.")
        fecha_s = fecha.strip()

        if FECHA_DOF_REGEX.match(fecha_s):
            try:
                return datetime.strptime(fecha_s, "%d/%m/%Y")
            except ValueError as e:
                raise ValidationError(f"Fecha inválida: {e}")

        try:
            return datetime.strptime(fecha_s, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                f"Fecha '{fecha}' inválida. Use DD/MM/YYYY o YYYY-MM-DD."
            )

    # ============================================================
    # Mocks
    # ============================================================

    @staticmethod
    def _mock_sumario(fecha_dof: str, url: str) -> dict[str, Any]:
        return mark_simulated({
            "fecha": fecha_dof,
            "url_consultado": url,
            "total_notas": 3,
            "notas": [
                {
                    "codigo": "5790442",
                    "titulo": "Acuerdo por el que se dan a conocer porcentajes y montos del estímulo fiscal IEPS.",
                    "dependencia": "SHCP",
                    "seccion": "PODER EJECUTIVO",
                    "url_detalle": f"{URL_BASE}/nota_detalle.php?codigo=5790442&fecha={fecha_dof}",
                },
                {
                    "codigo": "5790460",
                    "titulo": "Tipo de cambio para solventar obligaciones denominadas en moneda extranjera.",
                    "dependencia": "BANXICO",
                    "seccion": "BANCO DE MEXICO",
                    "url_detalle": f"{URL_BASE}/nota_detalle.php?codigo=5790460&fecha={fecha_dof}",
                },
                {
                    "codigo": "5790446",
                    "titulo": "Norma Oficial Mexicana NOM-005-SSA-2026, Servicios de Planificación Familiar.",
                    "dependencia": "SSA",
                    "seccion": "SECRETARIA DE SALUD",
                    "url_detalle": f"{URL_BASE}/nota_detalle.php?codigo=5790446&fecha={fecha_dof}",
                },
            ],
        })

    @staticmethod
    def _mock_busqueda(
        texto: str, desde: date, hasta: date, limite: int,
    ) -> dict[str, Any]:
        n = min(limite, 5)
        return mark_simulated({
            "texto_buscado": texto,
            "periodo": {
                "desde": desde.strftime("%d/%m/%Y"),
                "hasta": hasta.strftime("%d/%m/%Y"),
            },
            "total_resultados": n,
            "resultados": [
                {
                    "codigo": f"57900{i:02d}",
                    "titulo": f"Resultado mock #{i} con texto '{texto}'.",
                    "dependencia": "SHCP",
                    "fecha": (hasta - timedelta(days=i * 30)).strftime("%d/%m/%Y"),
                    "url_detalle": f"{URL_BASE}/nota_detalle.php?codigo=57900{i:02d}&fecha={hasta.strftime('%d/%m/%Y')}",
                }
                for i in range(1, n + 1)
            ],
            "url_consultado": URL_BUSQUEDA,
        })

    @staticmethod
    def _mock_detalle(codigo: str, fecha_dof: str, url: str) -> dict[str, Any]:
        return mark_simulated({
            "codigo": codigo,
            "fecha": fecha_dof,
            "url_detalle": url,
            "titulo": "Acuerdo MOCK por el que se establecen disposiciones aplicables.",
            "dependencia": "SHCP",
            "seccion": "PODER EJECUTIVO",
            "texto_completo": (
                "Este es el texto mock de la nota DOF. En el path real con "
                "MP_DOF_REAL=1, aquí aparecería el contenido completo del HTML "
                "de la nota, parseado de www.dof.gob.mx/nota_detalle.php."
            ),
            "url_pdf": f"{URL_BASE}/abrirPDF.php?codnota={codigo}",
        })

    # ============================================================
    # Path real (con requests/httpx) — TODO en sesión real
    # ============================================================

    def _sumario_real(self, fecha_dt, url):
        raise McpError(
            "Path real DOF requiere requests + BeautifulSoup para parsear HTML. "
            "Implementar: GET {url}, parse <table> con notas, extract codigo/titulo/dependencia.",
            {"url": url, "hint": "ver selectores en mp_dof_api/scraper.py"},
        )

    def _busqueda_real(self, texto, desde, hasta, limite):
        raise McpError(
            "Path real búsqueda DOF requiere POST a busqueda_detalle.php "
            "con form data textobusqueda + choosePath=textoCompleto.",
            {"url": URL_BUSQUEDA, "hint": "implementar parser HTML resultados"},
        )

    def _detalle_real(self, codigo, fecha_dof, url):
        raise McpError(
            "Path real detalle DOF requiere requests + BeautifulSoup.",
            {"url": url, "hint": "extract texto completo de div.Texto"},
        )
