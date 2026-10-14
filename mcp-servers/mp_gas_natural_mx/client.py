"""Cliente mp_gas_natural_mx.

- Tarifas vigentes (real): PDFs oficiales que el distribuidor publica en su
  página de tarifas. Hoy: Ecogas (verificado 2026-10-14).
- Recibo del titular: todos los portales exigen login → handoff humano.
"""
from __future__ import annotations

import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    ConfigError,
    NotFoundError,
    UpstreamError,
    ValidationError,
    handle_httpx_error,
)
from shared.gas_natural_mx import CATALOGO_GAS_NATURAL, DistribuidorGas, buscar_distribuidor  # noqa: E402
from shared.handoff_humano import handoff_humano  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "gas_natural_mx"
_HEADERS = {"User-Agent": "Mozilla/5.0 (plugins-mx)"}
_MONEY = r"\$\s*([\d,]+(?:\.\d+)?)"


def _f(txt: str) -> float:
    return float(txt.replace(",", ""))


def pdf_texto(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ConfigError(
            "pypdf requerido para leer las tarifas publicadas.",
            {"hint": "pip install 'plugins-mx-mcp[estatal-resto]'"},
        ) from exc
    if not data.startswith(b"%PDF"):
        raise UpstreamError("El distribuidor no devolvió un PDF.", {"inicio": data[:20].decode("latin-1")})
    return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)


def parse_documento(texto: str) -> dict[str, Any]:
    """Clasifica y extrae un PDF de tarifas de Ecogas."""
    m = re.search(r"Usuarios Residenciales de (.+?)\s*\n\s*Precio del mes de (\w+)\s*" + _MONEY, texto)
    if m:
        gj = re.search(r"MXP/Gjoule\s*" + _MONEY, texto)
        return {
            "tipo": "precio_mensual_residencial",
            "zona": m.group(1).strip(),
            "mes": m.group(2),
            "precio_mxn_m3": _f(m.group(3)),
            "precio_mxn_gj": _f(gj.group(1)) if gj else None,
            "incluye_iva": False,
        }
    if "LISTA DE TARIFAS" in texto.upper():
        zona = re.search(r"Zona Geogr[aá]fica\s+(.+)", texto)
        titulo = re.search(r"(LISTA DE TARIFAS[^\n]+)", texto, re.I)
        permiso = re.search(r"permiso\s+(G/\S+)", texto)
        oficio = re.search(r"oficio\s+(\S+)\s+de fecha\s+([^,]+)", texto)
        return {
            "tipo": "lista_tarifas_maximas",
            "zona": zona.group(1).strip() if zona else None,
            "titulo": re.sub(r"\s+", " ", titulo.group(1)).strip() if titulo else None,
            "permiso": permiso.group(1).rstrip(",") if permiso else None,
            "oficio_aprobacion": f"{oficio.group(1)} ({oficio.group(2).strip()})" if oficio else None,
            "texto": re.sub(r"[ \t]+", " ", texto)[:4000],
        }
    raise UpstreamError("PDF de tarifas con formato desconocido.", {"inicio": texto[:200]})


class GasNaturalMxClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None,
                 http: httpx.Client | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._http = http

    def _distribuidor(self, clave: str) -> DistribuidorGas:
        d = buscar_distribuidor(clave)
        if d is None:
            raise NotFoundError(f"Distribuidor '{clave}' no en catálogo.")
        return d

    def consultar_recibo(self, distribuidor: str, contrato: str) -> dict[str, Any]:
        """Recibo del titular: requiere login en el portal del distribuidor → handoff."""
        d = self._distribuidor(distribuidor)
        contrato = contrato.strip()
        if len(contrato) < 4:
            raise ValidationError("contrato muy corto")
        self._bitacora.log("consultar_recibo", success=True, params_summary={
            "distribuidor": d.clave, "contrato_hash": self._bitacora.hash_sensitive(contrato)})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"distribuidor": d.clave, "contrato": contrato, "monto_mxn": 450.0})
        return handoff_humano(
            portal=d.url_portal,
            motivo="login",
            detalle=f"{d.nombre} solo muestra recibos al titular con sesión iniciada. {d.notas}".strip(),
            pasos=[f"Entrar a {d.url_portal} con la cuenta del titular",
                   f"Abrir el recibo del contrato {contrato}"],
        )

    def tarifas_vigentes(self, distribuidor: str = "ecogas", zona: str | None = None) -> dict[str, Any]:
        """Tarifas publicadas por el distribuidor (PDFs oficiales), con fuente citada."""
        d = self._distribuidor(distribuidor)
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"distribuidor": d.clave, "documentos": []})
        if not d.tarifas_url:
            raise UpstreamError(
                f"{d.nombre}: sin página pública de tarifas verificada. {d.notas}".strip(),
                {"distribuidor": d.clave, "portal": d.url_portal, "implementado": False},
            )
        cache_key = f"tarifas:{d.clave}:{zona or ''}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        client = self._http or httpx.Client(timeout=60, headers=_HEADERS, follow_redirects=True)
        try:
            r = client.get(d.tarifas_url)
            r.raise_for_status()
            links = sorted(set(re.findall(r'href="(pdf/index\.php\?file=[^"]+)"', r.text)))
            if not links:
                raise UpstreamError("La página de tarifas no trae PDFs (¿cambió el sitio?)", {"url": d.tarifas_url})
            documentos = []
            for rel in links:
                if zona and zona.lower() not in rel.lower() and "precios" in rel.lower():
                    continue
                url = urljoin(d.tarifas_url, rel)
                pdf = client.get(url)
                pdf.raise_for_status()
                documentos.append({**parse_documento(pdf_texto(pdf.content)), "fuente": url})
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc) from exc
        finally:
            if self._http is None:
                client.close()

        result = {
            "distribuidor": d.clave,
            "pagina_tarifas": d.tarifas_url,
            "documentos": documentos,
            "nota": "Tarifas máximas aprobadas por la autoridad reguladora (DIR-GAS-001-2007, disp. 21.1) "
                    "y precio mensual del gas trasladado al usuario, sin IVA.",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
        self._cache.set(cache_key, result, ttl_hours=24)
        return result

    def listar_distribuidores(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_GAS_NATURAL),
            "distribuidores": [{
                "clave": d.clave, "nombre": d.nombre, "zona": d.zona,
                "portal": d.url_portal, "metodo": d.metodo,
                "poblacion_aprox": d.poblacion_aprox,
                "tarifas_publicas": bool(d.tarifas_url),
            } for d in CATALOGO_GAS_NATURAL],
        }
