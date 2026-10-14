"""Impuesto Sobre Hospedaje (ISH) por entidad federativa MX — tasas 2026.

Revisado 2026-10-14 (grupo E1). Las 32 entidades lo cobran en 2026 (Veracruz
con duda). Fuentes secundarias: no se abrió el texto legal primario de ningún
estado, así que la confianza máxima es "media":

- [T] El Contribuyente, tabla ISH 2026: https://www.elcontribuyente.mx/impuesto-sobre-hospedaje/
- [A] Airbnb, estados donde recauda y remite: https://es-l.airbnb.com/help/article/2288
- [B] BHR ene-2026 (Yucatán, EdoMex): https://www.bhrmx.com/wp-content/uploads/2026/01/IMPUESTO-SOBRE-HOSPEDAJE-2026-NUEVAS-OBLIGACIONES-Y-BENEFICIOS.pdf
- [C] El Contribuyente feb-2026: https://www.elcontribuyente.mx/2026/02/airbnb-hoteles-y-rentas-asi-cambia-el-impuesto-sobre-hospedaje-en-2026/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

T = "https://www.elcontribuyente.mx/impuesto-sobre-hospedaje/"
A = "https://es-l.airbnb.com/help/article/2288"
B = "https://www.bhrmx.com/wp-content/uploads/2026/01/IMPUESTO-SOBRE-HOSPEDAJE-2026-NUEVAS-OBLIGACIONES-Y-BENEFICIOS.pdf"
C = "https://www.elcontribuyente.mx/2026/02/airbnb-hoteles-y-rentas-asi-cambia-el-impuesto-sobre-hospedaje-en-2026/"


@dataclass
class EstadoISH:
    clave: str
    nombre_estado: str
    tasa_pct: float
    tasa_plataformas_pct: Optional[float] = None  # casas/deptos vía plataformas digitales
    cobra_ish: bool = True
    confianza: str = "media"
    fuentes: tuple[str, ...] = (T,)
    notas: str = ""


CATALOGO_ISH: list[EstadoISH] = [
    EstadoISH("ags", "Aguascalientes", 3.0),
    EstadoISH("bc", "Baja California", 5.0, 5.0, fuentes=(T, A), notas="Moteles 7%."),
    EstadoISH("bcs", "Baja California Sur", 4.0, fuentes=(T, A)),
    EstadoISH("cam", "Campeche", 2.0, fuentes=(T, A)),
    EstadoISH("chis", "Chiapas", 2.0, fuentes=(T, A), notas="Moteles 5%."),
    EstadoISH("chih", "Chihuahua", 4.0, confianza="baja", notas="Otra fuente reporta 3%."),
    EstadoISH("cdmx", "Ciudad de México", 3.5, 5.0, fuentes=(T, A),
              notas="Código Fiscal CDMX art. 162 (3.5% hoteles; 5% casas/deptos/plataformas)."),
    EstadoISH("coah", "Coahuila", 3.0),
    EstadoISH("col", "Colima", 3.0, fuentes=(T, A), notas="Moteles 5%."),
    EstadoISH("dgo", "Durango", 3.0, confianza="baja", notas="Moteles 5%. Un portal estatal reporta 2%/3% por tamaño."),
    EstadoISH("edomex", "Estado de México", 4.0, fuentes=(T, B, C),
              notas="Subsidio 50% a estancias > 15 días (LI EdoMex 2026 art. 12)."),
    EstadoISH("gto", "Guanajuato", 4.0),
    EstadoISH("gro", "Guerrero", 4.0, 5.0, fuentes=(T, A)),
    EstadoISH("hgo", "Hidalgo", 3.0, confianza="baja", fuentes=(T, C), notas="[T] dice 2.5%, [C] 3%."),
    EstadoISH("jal", "Jalisco", 4.0, confianza="baja", fuentes=(T, A), notas="Airbnb reporta 5%."),
    EstadoISH("mich", "Michoacán", 3.0, fuentes=(T, A)),
    EstadoISH("mor", "Morelos", 3.75),
    EstadoISH("nay", "Nayarit", 5.0, fuentes=(T, A)),
    EstadoISH("nl", "Nuevo León", 3.0, fuentes=(T, A)),
    EstadoISH("oax", "Oaxaca", 3.0, confianza="baja", fuentes=(T, A), notas="Airbnb reporta 3–5%."),
    EstadoISH("pue", "Puebla", 3.0, fuentes=(T, A)),
    EstadoISH("qro", "Querétaro", 3.5, 5.0, fuentes=(T, A)),
    EstadoISH("qroo", "Quintana Roo", 5.0, 6.0, fuentes=(C, A),
              notas="Ley del Impuesto al Hospedaje del Estado de QRoo (reforma POE 16-dic-2025)."),
    EstadoISH("slp", "San Luis Potosí", 4.0),
    EstadoISH("sin", "Sinaloa", 3.0, fuentes=(T, A)),
    EstadoISH("son", "Sonora", 3.0, fuentes=(T, A)),
    EstadoISH("tab", "Tabasco", 3.0),
    EstadoISH("tam", "Tamaulipas", 3.0),
    EstadoISH("tlax", "Tlaxcala", 2.0, confianza="baja"),
    EstadoISH("ver", "Veracruz", 2.0, confianza="baja",
              fuentes=(T, "https://elcongresista.mx/politica/veracruz/impuesto-3-plataformas-hospedaje-veracruz-2026"),
              notas="Vigencia dudosa; 3% a plataformas aprobado sin convenio con SAT."),
    EstadoISH("yuc", "Yucatán", 4.5, fuentes=(B, C), notas="Baja a 4.5% en 2026."),
    EstadoISH("zac", "Zacatecas", 3.0),
]


def buscar_ish(clave: str) -> EstadoISH | None:
    cn = clave.strip().lower()
    for e in CATALOGO_ISH:
        if e.clave == cn:
            return e
    return None


def listar_ish(solo_aplicables: bool = False) -> list[EstadoISH]:
    if solo_aplicables:
        return [e for e in CATALOGO_ISH if e.cobra_ish]
    return list(CATALOGO_ISH)


def calcular_ish(estado: str, monto_hospedaje: float, plataforma_digital: bool = False) -> dict:
    """ISH sobre el monto del hospedaje (antes de IVA)."""
    e = buscar_ish(estado)
    if e is None:
        raise ValueError(f"Estado '{estado}' no en catálogo.")
    if monto_hospedaje < 0:
        raise ValueError("monto_hospedaje no puede ser negativo.")
    tasa = e.tasa_plataformas_pct if (plataforma_digital and e.tasa_plataformas_pct) else e.tasa_pct
    ish = round(monto_hospedaje * tasa / 100, 2) if e.cobra_ish else 0.0
    return {
        "estado": e.clave,
        "estado_nombre": e.nombre_estado,
        "cobra_ish": e.cobra_ish,
        "tasa_pct": tasa,
        "plataforma_digital": plataforma_digital,
        "monto_hospedaje": monto_hospedaje,
        "ish_mxn": ish,
        "monto_total_con_ish": round(monto_hospedaje + ish, 2),
        "confianza": e.confianza,
        "fuentes": list(e.fuentes),
        "notas": e.notas,
        "simulated": False,
    }


__all__ = ["EstadoISH", "CATALOGO_ISH", "buscar_ish", "listar_ish", "calcular_ish"]
