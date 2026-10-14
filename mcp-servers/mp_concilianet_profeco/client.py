"""Cliente mp_concilianet_profeco — Concilianet + Buró Comercial PROFECO (consultas reales).

Fuentes públicas, sin login ni CAPTCHA (verificadas 2026-10-14):
- Proveedores con convenio Concilianet: dos PDF enlazados desde
  https://concilianet.profeco.gob.mx/Concilianet/proveedores_que_concilian.jsp
  (servicios y telecomunicaciones). Se descargan, se extrae el texto con pypdf y se
  busca la razón social normalizada.
- Buró Comercial: endpoints JSON que usa https://burocomercial.profeco.gob.mx/js/consulta.js
  (`proveedores` DataTables server-side y `consulta?type=anio|edo|quejas`).

Estatus de un caso y registro de quejas requieren cuenta del consumidor → handoff.
Mock solo con PLUGINS_MX_MOCK=1. Fallas → UpstreamError.
"""
from __future__ import annotations

import io
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.http_helpers import default_user_agent  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402


NAMESPACE = "concilianet"
URL_CONCILIANET = "https://concilianet.profeco.gob.mx/Concilianet/"
URL_PROVEEDORES_PAGINA = URL_CONCILIANET + "proveedores_que_concilian.jsp"
PDFS_CONVENIO = {
    "servicios": URL_CONCILIANET + "archivos/LISTADO%20DE%20PROVEEDORES%20PARTICIPANTES%20CONCILIANET.pdf",
    "telecomunicaciones": URL_CONCILIANET + "archivos/PROVEEDORES%20PARA%20PLATAFORMA%20CONCILIANET.pdf",
}
URL_BURO = "https://burocomercial.profeco.gob.mx/"
_COLS_BURO = ["razon_social", "nombre_comercial", "total_quejas", "ca", "giros"]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return " ".join(re.sub(r"[^A-Z0-9&]+", " ", s).split())


def _sin_html(s: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", s or "").split())


def _json(r: httpx.Response) -> Any:
    # `consulta?type=edo` responde JSON en latin-1 aunque declare UTF-8 (visto 2026-10-14).
    r.raise_for_status()
    try:
        return json.loads(r.content.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(r.content.decode("latin-1"))


def _entero(s: Any) -> int | None:
    try:
        return int(str(s).replace(",", ""))
    except (TypeError, ValueError):
        return None


def parse_buro_proveedores(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in payload.get("data", []):
        m = re.search(r"mostrarProve\('([0-9a-f]+)'", row.get("razon_social", ""))
        out.append({
            "razon_social": _sin_html(row.get("razon_social", "")),
            "nombre_comercial": _sin_html(row.get("nombre_comercial", "")),
            "total_quejas": _entero(row.get("total_quejas")),
            "giros": row.get("giros"),
            "token_buro": m.group(1) if m else None,
        })
    return out


class ConcilianetClient:
    def __init__(self, bitacora: Bitacora | None = None, cache: FileCache | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._cache = cache or FileCache(NAMESPACE)

    def _http(self) -> httpx.Client:
        return httpx.Client(timeout=45.0, follow_redirects=True,
                            headers={"User-Agent": default_user_agent("mp_concilianet_profeco")})

    def _texto_convenios(self) -> dict[str, str]:
        cached = self._cache.get("pdfs_convenio")
        if cached is not None:
            return cached
        try:
            import pypdf
        except ImportError as e:  # pragma: no cover
            raise UpstreamError("Falta pypdf: instala el extra publicos-federales-2") from e
        textos = {}
        try:
            with self._http() as c:
                for clave, url in PDFS_CONVENIO.items():
                    r = c.get(url)
                    r.raise_for_status()
                    reader = pypdf.PdfReader(io.BytesIO(r.content))
                    textos[clave] = _norm(" ".join(p.extract_text() or "" for p in reader.pages))
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        if not all(textos.values()):
            raise UpstreamError("Un listado de Concilianet vino sin texto extraíble", {"urls": PDFS_CONVENIO})
        self._cache.set("pdfs_convenio", textos, ttl_days=7)
        return textos

    def _buro_buscar(self, texto: str, length: int = 10) -> dict[str, Any]:
        params: dict[str, Any] = {"draw": 1, "start": 0, "length": length,
                                  "search[value]": texto, "search[regex]": "false"}
        for i, col in enumerate(_COLS_BURO):
            params.update({f"columns[{i}][data]": col, f"columns[{i}][name]": "",
                           f"columns[{i}][searchable]": "true", f"columns[{i}][orderable]": "false",
                           f"columns[{i}][search][value]": "", f"columns[{i}][search][regex]": "false"})
        try:
            with self._http() as c:
                r = c.get(URL_BURO + "proveedores", params=params,
                          headers={"X-Requested-With": "XMLHttpRequest"})
                data = _json(r)
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        except ValueError as e:
            raise UpstreamError("Buró Comercial no devolvió JSON", {"url": URL_BURO}) from e
        return {"total": data.get("recordsFiltered"), "proveedores": parse_buro_proveedores(data)}

    # ── tools ──────────────────────────────────────────────────────────────
    def consultar_proveedor(self, razon_social: str) -> dict[str, Any]:
        if not razon_social or len(razon_social.strip()) < 3:
            raise ValidationError(f"razon_social muy corta: {razon_social!r}")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"razon_social_buscada": razon_social,
                                   "tiene_convenio_concilianet": True})

        q = _norm(razon_social)
        textos = self._texto_convenios()
        listados = [k for k, t in textos.items() if q in t]
        buro = self._buro_buscar(razon_social.strip(), length=5)
        self._bitacora.log("consultar_proveedor", success=True, params_summary={"q": q})
        return {
            "razon_social_buscada": razon_social,
            "tiene_convenio_concilianet": bool(listados),
            "listados_donde_aparece": listados,
            "nota_convenio": (None if listados else
                              "No aparece literalmente en los listados publicados; prueba con la razón "
                              "social exacta o el nombre comercial antes de concluir."),
            "buro_comercial": buro,
            "fuentes": [URL_PROVEEDORES_PAGINA, URL_BURO],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def buro_quejas(self, proveedor: str, anio: int | None = None) -> dict[str, Any]:
        """Quejas por año (nacional) + principales motivos del Buró Comercial."""
        if not proveedor or len(proveedor.strip()) < 3:
            raise ValidationError(f"proveedor muy corto: {proveedor!r}")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"proveedor": proveedor, "quejas_recibidas": 100})
        buro = self._buro_buscar(proveedor.strip(), length=1)
        if not buro["proveedores"]:
            return {"proveedor": proveedor, "encontrado": False, "fuente": URL_BURO, "simulated": False,
                    "nota": "Sin quejas concluidas publicadas para ese nombre (el Buró omite quejas en trámite)."}
        prov = buro["proveedores"][0]
        tkn = prov["token_buro"]
        try:
            with self._http() as c:
                anios = _json(c.get(URL_BURO + "consulta", params={"type": "anio", "proveedor": tkn}))["anios"]
                anio = anio or max(anios)
                if anio not in anios:
                    raise ValidationError(f"anio sin datos; disponibles: {anios}")
                edo = _json(c.get(URL_BURO + "consulta",
                                  params={"type": "edo", "anio": anio, "proveedor": tkn}))
                q = _json(c.get(URL_BURO + "consulta",
                                params={"type": "quejas", "anio": anio, "proveedor": tkn, "ur": "-1"}))
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        except (ValueError, KeyError) as e:
            raise UpstreamError("Respuesta inesperada del Buró Comercial", {"raw": str(e)}) from e
        return {
            "proveedor": prov["razon_social"],
            "nombre_comercial": prov["nombre_comercial"],
            "encontrado": True,
            "total_quejas_historico": prov["total_quejas"],
            "anio": anio,
            "anios_disponibles": anios,
            "nacional": {k: _entero(v) for k, v in q.items() if k != "anio"},
            "principales_motivos": edo.get("motivos", []),
            "fuente": URL_BURO,
            "simulated": False,
        }

    def estatus_caso(self, folio: str) -> dict[str, Any]:
        if not folio or len(folio) < 6:
            raise ValidationError(f"folio inválido: {folio!r}")
        return armar_handoff(
            motivo="login",
            detalle="El expediente solo es visible para el consumidor con su cuenta de Concilianet.",
            url=URL_CONCILIANET,
            pasos=["Iniciar sesión en Concilianet con la cuenta del consumidor y abrir el folio."],
            folio=folio,
            fase_actual=None,
        )

    def listar_proveedores_convenio(self) -> dict[str, Any]:
        """Los listados oficiales son PDF con columnas de logos; se entregan las fuentes y se
        busca con concilianet_consultar_proveedor en vez de devolver una lista mal parseada."""
        return {
            "fuentes_pdf": PDFS_CONVENIO,
            "pagina": URL_PROVEEDORES_PAGINA,
            "nota": "Usa concilianet_consultar_proveedor(razon_social) para buscar dentro de los listados.",
        }

    def registrar_queja(self, consumidor_curp_hash: str | None, proveedor: str,
                        descripcion: str, monto_reclamado_mxn: float | None = None) -> dict[str, Any]:
        if not proveedor:
            raise ValidationError("proveedor requerido")
        if not descripcion or len(descripcion) < 20:
            raise ValidationError("descripcion debe ser ≥20 caracteres")
        return armar_handoff(
            motivo="accion_del_titular",
            detalle="Presentar una queja es un acto del consumidor; este MCP es de solo lectura.",
            url=URL_CONCILIANET + "registro.jsp",
            pasos=[
                "Registrarse en Concilianet (si el proveedor está en convenio) o acudir a la ODECO.",
                "Capturar la reclamación con la descripción preparada y anexar comprobantes.",
            ],
            proveedor=proveedor,
            registrada=False,
            borrador={"descripcion": descripcion, "monto_reclamado_mxn": monto_reclamado_mxn},
        )
