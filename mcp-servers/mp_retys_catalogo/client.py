"""Cliente mp_retys_catalogo — Catálogo Nacional CONAMER normalizado.

CONAMER (catalogonacional.gob.mx) tiene 5,000+ trámites/regulaciones federales
y estatales, pero su API NO es pública. Búsqueda real es ASP.NET con
AntiForgeryToken + form POST. Validado vivo 2026-06-15: search input
`#txtSearch`, botón `#btnSearch`, filtro dependencias `#selectDependencias-selectized`.

Este MCP entrega:
- Catálogo curado de 24 sectores oficiales
- Trámites de alta demanda con clave homoclave CONAMER
- Path real Playwright para búsqueda en vivo (opt-in)
- Normalización a formato datos.gob.mx (DCAT)
"""
from __future__ import annotations

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


NAMESPACE = "retys_catalogo"
URL_CONAMER = "https://www.catalogonacional.gob.mx/"
URL_DATOS_GOBMX = "https://www.datos.gob.mx/"

# 24 sectores oficiales del Catálogo Nacional (verificados 2026-06-15)
SECTORES_CONAMER: dict[str, str] = {
    "hacienda_finanzas": "Hacienda y Finanzas Públicas",
    "comunicaciones_transporte": "Comunicaciones, Transporte y Movilidad",
    "energia": "Energía",
    "salud_deporte": "Salud y Deporte",
    "medio_ambiente": "Medio Ambiente, Recursos Naturales y Pesca",
    "desarrollo_economico": "Desarrollo económico",
    "no_sectorizado": "No sectorizado",
    "agricultura": "Agricultura, Ganadería y Desarrollo rural",
    "ciencia_educacion": "Ciencia y Educación",
    "gobernacion": "Gobernación",
    "relaciones_exteriores": "Relaciones Exteriores",
    "marina": "Marina",
    "cultura_recreacion": "Cultura y Recreación",
    "desarrollo_social": "Desarrollo Social",
    "sedatu": "Desarrollo Agrario, Territorial y Urbano",
    "trabajo_prevision": "Trabajo y Previsión Social",
    "turismo": "Turismo",
    "funcion_publica": "Función Pública y Contraloría",
    "seguridad_justicia": "Seguridad, Legalidad y Justicia",
    "proteccion_civil": "Protección Civil",
    "igualdad_sustantiva": "Igualdad Sustantiva",
    "ayuntamiento": "Ayuntamiento",
    "agua": "Agua",
    "desarrollo_sustentable": "Desarrollo Sustentable",
    "construccion": "Construcción",
    "sector_electoral": "Sector Electoral",
    "transformacion_digital": "Transformación Digital",
}

# Trámites de alta demanda con homoclave CONAMER (curados manualmente)
TRAMITES_DEMANDA_ALTA: list[dict[str, Any]] = [
    {"homoclave": "SAT-04-022", "nombre": "Constancia de Situación Fiscal",
     "dependencia": "SAT", "sector": "hacienda_finanzas",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.sat.gob.mx/portal/public/tramites/constancia-de-situacion-fiscal",
     "fundamento_legal": "Art. 27 CFF"},
    {"homoclave": "SAT-08-001", "nombre": "Inscripción al RFC",
     "dependencia": "SAT", "sector": "hacienda_finanzas",
     "modalidad": "Mixto", "costo_mxn": 0,
     "url_tramite": "https://www.sat.gob.mx/tramites/operacion/15433/inscribete-en-el-rfc-como-persona-fisica-con-curp",
     "fundamento_legal": "Art. 27 CFF + RCFF Art. 22"},
    {"homoclave": "IMSS-02-025-A", "nombre": "Semanas cotizadas IMSS",
     "dependencia": "IMSS", "sector": "trabajo_prevision",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.imss.gob.mx/tramites/imss02025a",
     "fundamento_legal": "Art. 295 LSS"},
    {"homoclave": "RENAPO-CURP", "nombre": "Consulta CURP",
     "dependencia": "RENAPO", "sector": "gobernacion",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.gob.mx/curp/",
     "fundamento_legal": "Reglamento Ley General Población"},
    {"homoclave": "INE-CV", "nombre": "Credencial para votar",
     "dependencia": "INE", "sector": "sector_electoral",
     "modalidad": "Mixto", "costo_mxn": 0,
     "url_tramite": "https://www.ine.mx/credencial/",
     "fundamento_legal": "LGIPE Art. 130"},
    {"homoclave": "SRE-PASAPORTE", "nombre": "Pasaporte mexicano",
     "dependencia": "SRE", "sector": "relaciones_exteriores",
     "modalidad": "Presencial", "costo_mxn": 1830,
     "url_tramite": "https://www.gob.mx/tramites/ficha/pasaporte-ordinario-en-territorio-nacional/SRE227",
     "fundamento_legal": "Ley de Migración Art. 11"},
    {"homoclave": "COFEPRIS-AVISO-FUNC", "nombre": "Aviso de Funcionamiento COFEPRIS",
     "dependencia": "COFEPRIS", "sector": "salud_deporte",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.gob.mx/cofepris",
     "fundamento_legal": "Ley General Salud Art. 200 bis"},
    {"homoclave": "STPS-REPSE", "nombre": "Registro REPSE",
     "dependencia": "STPS", "sector": "trabajo_prevision",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://repse.stps.gob.mx/",
     "fundamento_legal": "LFT Art. 15"},
    {"homoclave": "IMPI-MARCA", "nombre": "Registro de marca IMPI",
     "dependencia": "IMPI", "sector": "desarrollo_economico",
     "modalidad": "Mixto", "costo_mxn": 3231,
     "url_tramite": "https://www.gob.mx/impi",
     "fundamento_legal": "Ley Federal Protección Propiedad Industrial"},
    {"homoclave": "CRE-20-001-I", "nombre": "Permiso comercialización hidrocarburos",
     "dependencia": "CRE", "sector": "energia",
     "modalidad": "Mixto", "costo_mxn": 47000,
     "url_tramite": "https://catalogonacional.gob.mx/FichaTramite?traHomoclave=CRE-20-001-I",
     "fundamento_legal": "Ley Hidrocarburos"},
    {"homoclave": "CONAGUA-REPDA", "nombre": "Inscripción REPDA",
     "dependencia": "CONAGUA", "sector": "agua",
     "modalidad": "Presencial", "costo_mxn": 0,
     "url_tramite": "https://www.gob.mx/conagua",
     "fundamento_legal": "Ley Aguas Nacionales Art. 30"},
    {"homoclave": "SEP-CEDULA", "nombre": "Cédula profesional SEP",
     "dependencia": "SEP", "sector": "ciencia_educacion",
     "modalidad": "Digital", "costo_mxn": 1670,
     "url_tramite": "https://www.cedulaprofesional.sep.gob.mx/",
     "fundamento_legal": "Ley Reglamentaria Art. 5 Constitucional"},
]


class RetysCatalogoClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    def listar_sectores(self) -> dict[str, Any]:
        """Los 24 sectores oficiales del Catálogo Nacional."""
        self._log("listar_sectores", {})
        return {
            "total_sectores": len(SECTORES_CONAMER),
            "sectores": [{"clave": k, "nombre": v} for k, v in SECTORES_CONAMER.items()],
            "fuente": URL_CONAMER,
        }

    def buscar_tramite(
        self, q: str, sector: str | None = None
    ) -> dict[str, Any]:
        """Búsqueda de trámites por texto + filtro de sector."""
        self._log("buscar_tramite", {"q": q, "sector": sector})
        if not q or len(q) < 2:
            raise ValidationError("Query debe tener al menos 2 caracteres")
        q_norm = q.lower().strip()
        candidatos = TRAMITES_DEMANDA_ALTA
        if sector:
            sector_norm = sector.lower().strip()
            if sector_norm not in SECTORES_CONAMER:
                raise ValidationError(f"sector inválido: {sector!r}")
            candidatos = [t for t in candidatos if t["sector"] == sector_norm]
        matches = [
            t for t in candidatos
            if q_norm in t["nombre"].lower()
            or q_norm in t["homoclave"].lower()
            or q_norm in t["dependencia"].lower()
        ]
        return mark_simulated(
            {
                "query": q,
                "sector_filtro": sector,
                "total_resultados": len(matches),
                "resultados": matches,
                "fuente": URL_CONAMER,
                "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            },
            note="Mock — catálogo curado. Para vivo: MP_PLAYWRIGHT_PUBLIC=1 (ASP.NET + AntiForgeryToken).",
        )

    def detalle_tramite(self, homoclave: str) -> dict[str, Any]:
        """Detalle por homoclave CONAMER."""
        self._log("detalle_tramite", {"homoclave": homoclave})
        hc = (homoclave or "").upper().strip()
        for t in TRAMITES_DEMANDA_ALTA:
            if t["homoclave"].upper() == hc:
                return mark_simulated(
                    {**t, "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                    note="Catálogo curado — para detalle oficial: portal CONAMER.",
                )
        raise ValidationError(f"Homoclave no en catálogo curado: {homoclave!r}")

    def exportar_dcat(self) -> dict[str, Any]:
        """Exporta a formato DCAT (Data Catalog Vocabulary) compatible datos.gob.mx."""
        self._log("exportar_dcat", {})
        return {
            "@context": "https://www.w3.org/ns/dcat",
            "@type": "Catalog",
            "title": "Catálogo de Trámites Federales MX — Plugins MX",
            "description": (
                "Catálogo curado de trámites federales de alta demanda, "
                "normalizado para datos.gob.mx (Sistema Ajolote)."
            ),
            "publisher": "Plugins MX (elimoralsmendox@gmail.com)",
            "issued": "2026-06-15",
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "dataset": [
                {
                    "@type": "Dataset",
                    "identifier": t["homoclave"],
                    "title": t["nombre"],
                    "publisher": t["dependencia"],
                    "theme": SECTORES_CONAMER.get(t["sector"], t["sector"]),
                    "accessURL": t["url_tramite"],
                    "fundamentoLegal": t["fundamento_legal"],
                    "costoMXN": t["costo_mxn"],
                    "modalidad": t["modalidad"],
                }
                for t in TRAMITES_DEMANDA_ALTA
            ],
        }

    def buscar_en_vivo(self, q: str) -> dict[str, Any]:
        """Path real Playwright contra catalogonacional.gob.mx (ASP.NET)."""
        self._log("buscar_en_vivo", {"q": q})
        from shared.playwright_real import is_public_real_enabled
        if not is_public_real_enabled():
            return mark_simulated(
                self.buscar_tramite(q),
                note="Path real requiere MP_PLAYWRIGHT_PUBLIC=1",
            )

        from shared.playwright_real import playwright_session, with_real_or_fallback

        def _real() -> dict[str, Any]:
            with playwright_session() as page:
                page.goto(URL_CONAMER, wait_until="domcontentloaded")
                page.fill("#txtSearch", q)
                page.click("#btnSearch")
                page.wait_for_load_state("networkidle", timeout=15000)
                # Resultados aparecen en lista — parser heurístico
                resultados = page.eval_on_selector_all(
                    ".resultado-tramite, .ficha-tramite",
                    "els => els.slice(0,10).map(e => ({texto: e.innerText.slice(0,200)}))",
                ) or []
                return {
                    "query": q,
                    "total_resultados_vivo": len(resultados),
                    "resultados_vivo": resultados,
                    "fuente": URL_CONAMER,
                    "simulated": False,
                }

        def _fb() -> dict[str, Any]:
            return self.buscar_tramite(q)

        return with_real_or_fallback(_real, _fb, portal="conamer_catalogo")
