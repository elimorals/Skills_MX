"""Plataformas SaaS gubernamentales mexicanas — proveedores estatales/multi-municipio.

Algunos estados/proveedores ofrecen una plataforma compartida donde DECENAS de
municipios consultan predial usando la MISMA URL + form con un selector de
municipio. Esto multiplica la cobertura sin descubrir N portales individuales.

Plataformas identificadas (2026-06-13):

| Plataforma  | Estado/Provider          | URL base                                          | Municipios soportados |
|-------------|--------------------------|---------------------------------------------------|-----------------------|
| **SACPI**   | Gobierno de Michoacán    | sacpi.michoacan.gob.mx/frm_cpredial.aspx          | **95** (catálogo oficial) |
| SIM         | Provider privado MX      | {municipio}.recaudacion.net/SIM/predial.jsp       | ~5-10 (estimado, white-label per municipio) |
| SIAWeb      | Provider privado TAM     | ast.siaweb.net → ast.altamira.gob.mx              | 1 (Altamira) — possiblemente más |

**Hallazgo crítico SACPI**: el form tiene un `<select id="ddlMunicipios">` con
95 opciones — un solo MCP handler puede consultar TODOS los municipios MICH
seleccionando primero municipio + tipo (urbano/rústico) + clave catastral.

USO:
    from shared.plataformas_saas_mx import (
        SACPI_MICHOACAN,
        consulta_sacpi,
        plataforma_para_municipio,
    )

    # Opción 1: directo
    resultado = consulta_sacpi(municipio_codigo="034", cuenta="12345")

    # Opción 2: por nombre municipio (lookup en catálogo)
    plataforma = plataforma_para_municipio("mich", "morelia")
    if plataforma:
        resultado = plataforma.consulta(cuenta="...")
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ============================================================
# SACPI Michoacán — 95 municipios
# ============================================================

# Lista oficial extraída del <select id="ddlMunicipios"> 2026-06-13.
# Formato: código INEGI municipal (3 dígitos) → nombre tal como aparece en SACPI
SACPI_MUNICIPIOS_MICH: dict[str, str] = {
    "001": "ACUITZIO", "002": "AGUILILLA", "003": "ALVARO OBREGON",
    "004": "ANGAMACUTIRO", "005": "ANGANGUEO", "006": "APATZINGAN",
    "007": "APORO", "008": "AQUILA", "010": "ARTEAGA",
    "011": "BRISEÑAS", "012": "BUENAVISTA", "013": "CARACUARO",
    "014": "COAHUAYANA", "015": "COALCOMAN", "016": "COENEO",
    "017": "CONTEPEC", "018": "COPANDARO", "019": "COTIJA",
    "020": "CUITZEO", "021": "CHARAPAN", "022": "CHARO",
    "023": "CHAVINDA", "024": "CHERAN", "025": "CHILCHOTA",
    "026": "CHINICUILA", "028": "CHURINTZIO", "030": "ECUANDUREO",
    "031": "EPITACIO HUERTA", "032": "ERONGARICUARO", "033": "GABRIEL ZAMORA",
    "034": "HIDALGO", "035": "LA HUACANA", "036": "HUANDACAREO",
    "037": "HUANIQUEO", "038": "HUETAMO", "039": "HUIRAMBA",
    "040": "INDAPARAPEO", "041": "IRIMBO", "043": "JACONA",
    "044": "JIMENEZ", "045": "JIQUILPAN", "046": "JUÁREZ",
    "047": "JUNGAPEO", "048": "LAGUNILLAS", "049": "MADERO",
    "051": "MARCOS CASTELLANOS", "054": "MORELOS", "055": "MUGICA",
    "056": "NAHUATZEN", "057": "NOCUPETARO", "058": "NUEVO PARANGARICUTIRO",
    "059": "NUEVO URECHO", "060": "NUMARAN", "061": "OCAMPO",
    "062": "PAJACUARAN", "063": "PANINDICUARO", "064": "PARACUARO",
    "065": "PARACHO", "067": "PENJAMILLO", "068": "PERIBAN",
    "070": "PUREPERO", "072": "QUERENDARO", "073": "QUIROGA",
    "074": "COJUMATLAN DE REGULES", "075": "ZACÁN", "077": "SAN LUCAS",
    "078": "SANTA ANA MAYA", "079": "SALVADOR ESCALANTE", "080": "SENGUIO",
    "081": "SUSUPUATO", "083": "TANCITARO", "084": "TANGAMANDAPIO",
    "086": "TANHUATO", "087": "TARETAN", "089": "TEPALCATEPEC",
    "090": "TINGAMBATO", "091": "TINGUINDIN", "092": "TIQUICHEO",
    "093": "TLALPUJAHUA", "094": "TLAZAZALCA", "095": "TOCUMBO",
    "096": "TUMBISCATIO", "097": "TURICATO", "098": "TUXPAN",
    "100": "TZINTZUNTZAN", "101": "TZITZIO", "103": "VENUSTIANO CARRANZA",
    "104": "VILLAMAR", "105": "VISTA HERMOSA", "106": "YURECUARO",
    "107": "ZACAPU", "109": "ZINAPARO", "110": "ZINAPECUARO",
    "111": "ZIRACUARETIRO", "113": "JOSÉ SIXTO VERDUZCO",
}


@dataclass
class PlataformaSaaS:
    """Configuración de una plataforma SaaS gubernamental multi-municipio."""
    nombre: str
    operador: str  # "Gobierno de Michoacán", "Provider X", etc.
    url_consulta: str
    estados_cubiertos: list[str] = field(default_factory=list)
    municipios_soportados: dict[str, str] = field(default_factory=dict)  # codigo → nombre
    selectores: dict[str, list[str]] = field(default_factory=dict)
    requiere_seleccionar_municipio: bool = True
    requiere_seleccionar_tipo: bool = False  # urbano/rústico
    notas: str = ""
    validado: bool = False


SACPI_MICHOACAN = PlataformaSaaS(
    nombre="SACPI",
    operador="Gobierno del Estado de Michoacán",
    url_consulta="http://www.sacpi.michoacan.gob.mx/frm_cpredial.aspx",
    estados_cubiertos=["mich"],
    municipios_soportados=SACPI_MUNICIPIOS_MICH,
    selectores={
        "select_municipio": ["select[name='ddlMunicipios']", "select#ddlMunicipios"],
        "select_localidad": ["select[name='ddlLocalidades']", "select#ddlLocalidades"],
        "select_tipo": ["select[name='ddlTipo']", "select#ddlTipo"],
        "input_cuenta": ["input[name='txtCuenta']", "input#txtCuenta"],
        "input_clave": ["input[name='clave']"],
        "input_apellido": ["input[name='txtApellido']"],
        "submit": ["input[type='submit'][value*='Consultar']", "button:has-text('Consultar')"],
        "result": "table, .resultado, #pnlResultado",
    },
    requiere_seleccionar_municipio=True,
    requiere_seleccionar_tipo=True,
    notas="✅ Validado Playwright MCP 2026-06-13: ASP.NET WebForms con select de 95 municipios. Tipo: 1=URBANO 2=RÚSTICO. Cubre la mayoría de municipios pequeños de Michoacán que NO tienen portal propio.",
    validado=True,
)


# ============================================================
# Registro central
# ============================================================

PLATAFORMAS_SAAS: list[PlataformaSaaS] = [
    SACPI_MICHOACAN,
    # Futuras: SIM-recaudacion, SIAWeb, OPDAPAS, GTM-municipal, etc.
]


def plataforma_para_municipio(estado: str, municipio_clave: str) -> Optional[PlataformaSaaS]:
    """Devuelve la plataforma SaaS que cubre un municipio, si existe.

    Implementación actual: solo soporta lookup por nombre (case-insensitive).
    Futuro: lookup por código INEGI cuando esté en el catálogo central.
    """
    municipio_norm = municipio_clave.upper().replace("_", " ")
    for plat in PLATAFORMAS_SAAS:
        if estado not in plat.estados_cubiertos:
            continue
        for codigo, nombre in plat.municipios_soportados.items():
            # Match por nombre (con normalización básica)
            if nombre.upper() == municipio_norm:
                return plat
            # Match parcial (Ciudad Hidalgo → HIDALGO)
            if municipio_norm in nombre.upper() or nombre.upper() in municipio_norm:
                return plat
    return None


def codigo_municipio_sacpi(municipio_nombre: str) -> Optional[str]:
    """Para SACPI específicamente: devuelve el código INEGI del municipio.

    Ejemplo: codigo_municipio_sacpi("Ciudad Hidalgo") → "034"
    """
    nombre_norm = municipio_nombre.upper().replace("CIUDAD ", "").strip()
    for codigo, nombre in SACPI_MUNICIPIOS_MICH.items():
        if nombre == nombre_norm or nombre_norm in nombre or nombre in nombre_norm:
            return codigo
    return None


def consulta_sacpi(municipio_codigo: str, cuenta: str, tipo: str = "1") -> dict[str, Any]:
    """Consulta predial vía SACPI Michoacán.

    Args:
        municipio_codigo: código INEGI 3 dígitos (ej. "034" para Hidalgo)
        cuenta: clave catastral o cuenta predial
        tipo: "1"=urbano, "2"=rústico (default urbano)

    Returns:
        Dict con estructura estándar de `consulta_portal()`.
    """
    from shared.playwright_real import playwright_session, safe_text, parse_precio_mxn
    from shared.errors import UpstreamError

    if municipio_codigo not in SACPI_MUNICIPIOS_MICH:
        raise UpstreamError(
            f"Código de municipio {municipio_codigo} no encontrado en SACPI. "
            f"Códigos válidos: {list(SACPI_MUNICIPIOS_MICH.keys())[:5]}...",
            {"municipio_codigo": municipio_codigo},
        )

    with playwright_session() as page:
        try:
            page.goto(SACPI_MICHOACAN.url_consulta, wait_until="domcontentloaded")
        except Exception as e:
            raise UpstreamError(f"No se pudo cargar SACPI: {e}", {})

        # 1. Seleccionar municipio (ASP.NET postback puede recargar la página)
        try:
            page.locator("select[name='ddlMunicipios']").select_option(value=municipio_codigo)
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            raise UpstreamError(f"Error seleccionando municipio SACPI: {e}", {})

        # 2. Seleccionar tipo (urbano/rústico)
        try:
            page.locator("select[name='ddlTipo']").select_option(value=tipo)
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass  # algunos municipios podrían no requerirlo

        # 3. Llenar cuenta
        try:
            page.locator("input[name='txtCuenta']").fill(cuenta)
        except Exception as e:
            raise UpstreamError(f"Error llenando cuenta SACPI: {e}", {})

        # 4. Submit
        try:
            page.locator("input[type='submit'][value*='Consultar'], button:has-text('Consultar')").first.click()
        except Exception:
            page.keyboard.press("Enter")

        # 5. Esperar resultado
        try:
            page.wait_for_selector("table, .resultado, #pnlResultado", timeout=20000)
        except Exception as e:
            raise UpstreamError(f"Timeout esperando resultado SACPI: {e}", {})

        # 6. Parsear tabla
        adeudos = []
        for row in page.locator("table tr").all()[:50]:
            celdas = row.locator("td").all()
            if len(celdas) < 2:
                continue
            concepto = safe_text(celdas[0])
            monto = parse_precio_mxn(safe_text(celdas[-1]))
            if concepto and monto is not None and monto > 0:
                adeudos.append({"concepto": concepto, "monto_mxn": monto})

        total = sum(a["monto_mxn"] for a in adeudos)

        return {
            "plataforma": "SACPI",
            "estado": "mich",
            "municipio_codigo": municipio_codigo,
            "municipio_nombre": SACPI_MUNICIPIOS_MICH[municipio_codigo],
            "tipo": "urbano" if tipo == "1" else "rustico",
            "estatus": "al_corriente" if total == 0 else "con_adeudo",
            "adeudo_total_mxn": total,
            "conceptos_pendientes": len(adeudos),
            "adeudos": adeudos,
            "url_consultada": SACPI_MICHOACAN.url_consulta,
            "simulated": False,
        }


def listar_municipios_cubiertos_por_saas() -> dict[str, list[str]]:
    """Devuelve dict {estado: [nombres_municipios]} cubiertos por alguna plataforma SaaS."""
    por_estado: dict[str, list[str]] = {}
    for plat in PLATAFORMAS_SAAS:
        if not plat.validado:
            continue
        for estado in plat.estados_cubiertos:
            por_estado.setdefault(estado, []).extend(plat.municipios_soportados.values())
    return por_estado


def estadisticas_saas() -> dict[str, Any]:
    """Devuelve stats globales de cobertura SaaS."""
    return {
        "plataformas_registradas": len(PLATAFORMAS_SAAS),
        "plataformas_validadas": sum(1 for p in PLATAFORMAS_SAAS if p.validado),
        "municipios_cubiertos_via_saas": sum(
            len(p.municipios_soportados) for p in PLATAFORMAS_SAAS if p.validado
        ),
        "estados_con_saas": sorted({
            e for p in PLATAFORMAS_SAAS if p.validado for e in p.estados_cubiertos
        }),
    }
