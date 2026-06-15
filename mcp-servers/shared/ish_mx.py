"""Catálogo Impuesto Sobre Hospedaje (ISH) por entidad federativa MX.

ISH es un impuesto ESTATAL que grava el hospedaje de personas físicas.
Combo con airbnb-host-mx — los hosts retienen y enteran este impuesto.

Cobertura: 27 estados lo cobran. Tasas 1.5% - 6%.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EstadoISH:
    clave: str
    nombre_estado: str
    tasa_pct: float
    cobra_ish: bool = True
    portal_url: str = ""
    notas: str = ""


CATALOGO_ISH: list[EstadoISH] = [
    EstadoISH("cdmx", "Ciudad de México", 3.5, portal_url="https://www.finanzas.cdmx.gob.mx", notas="ISH 3.5% sobre tarifa cuarto."),
    EstadoISH("qroo", "Quintana Roo", 5.0, portal_url="https://sefiplan.qroo.gob.mx", notas="6% para Cancún/Cozumel turísticos."),
    EstadoISH("bcs", "Baja California Sur", 4.0, portal_url="https://finanzasbcs.gob.mx", notas="Los Cabos tasa especial."),
    EstadoISH("jal", "Jalisco", 3.0, portal_url="https://sepaf.jalisco.gob.mx"),
    EstadoISH("yuc", "Yucatán", 3.0, portal_url="https://sefin.yucatan.gob.mx"),
    EstadoISH("nay", "Nayarit", 3.0, portal_url="https://hacienda.nayarit.gob.mx", notas="Riviera Nayarit alto turismo."),
    EstadoISH("oax", "Oaxaca", 3.0, portal_url="https://www.finanzasoaxaca.gob.mx"),
    EstadoISH("gro", "Guerrero", 3.0, portal_url="https://sfa.guerrero.gob.mx", notas="Acapulco/Zihuatanejo."),
    EstadoISH("ver", "Veracruz", 3.0, portal_url="https://www.veracruz.gob.mx/finanzas"),
    EstadoISH("son", "Sonora", 3.0, portal_url="https://hacienda.sonora.gob.mx", notas="Puerto Peñasco/Bahía Kino."),
    EstadoISH("sin", "Sinaloa", 3.0, portal_url="https://saf.sinaloa.gob.mx", notas="Mazatlán."),
    EstadoISH("bc", "Baja California", 3.0, portal_url="https://www.bajacalifornia.gob.mx/finanzas"),
    EstadoISH("col", "Colima", 3.0, portal_url="https://finanzas.col.gob.mx", notas="Manzanillo."),
    EstadoISH("mich", "Michoacán", 3.0, portal_url="https://secfinanzas.michoacan.gob.mx"),
    EstadoISH("chis", "Chiapas", 3.0, portal_url="https://haciendachiapas.gob.mx", notas="Palenque/San Cristóbal."),
    EstadoISH("cam", "Campeche", 2.0, portal_url="https://finanzas.campeche.gob.mx"),
    EstadoISH("nl", "Nuevo León", 3.0, portal_url="https://www.nl.gob.mx/finanzas"),
    EstadoISH("pue", "Puebla", 3.0, portal_url="https://www.puebla.gob.mx/finanzas"),
    EstadoISH("qro", "Querétaro", 3.0, portal_url="https://sfqro.gob.mx"),
    EstadoISH("gto", "Guanajuato", 2.5, portal_url="https://finanzas.guanajuato.gob.mx", notas="San Miguel de Allende."),
    EstadoISH("slp", "San Luis Potosí", 3.0, portal_url="https://finanzas.slp.gob.mx"),
    EstadoISH("zac", "Zacatecas", 3.0, portal_url="https://finanzas.zacatecas.gob.mx"),
    EstadoISH("ags", "Aguascalientes", 3.0, portal_url="https://eservicios2.aguascalientes.gob.mx"),
    EstadoISH("dgo", "Durango", 3.0, portal_url="https://www.durango.gob.mx/sf"),
    EstadoISH("hgo", "Hidalgo", 3.0, portal_url="https://sefinanzas.hidalgo.gob.mx"),
    EstadoISH("mor", "Morelos", 3.0, portal_url="https://hacienda.morelos.gob.mx", notas="Tepoztlán/Cuernavaca."),
    EstadoISH("tab", "Tabasco", 3.0, portal_url="https://finanzas.tabasco.gob.mx"),
    # Sin ISH (5 estados)
    EstadoISH("edomex", "Estado de México", 0.0, cobra_ish=False),
    EstadoISH("coah", "Coahuila", 0.0, cobra_ish=False),
    EstadoISH("chih", "Chihuahua", 0.0, cobra_ish=False),
    EstadoISH("tlax", "Tlaxcala", 0.0, cobra_ish=False),
    EstadoISH("tam", "Tamaulipas", 0.0, cobra_ish=False),
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


def calcular_ish(estado: str, monto_hospedaje: float) -> dict:
    """Calcula ISH dado el monto del hospedaje (antes de IVA)."""
    e = buscar_ish(estado)
    if e is None:
        raise ValueError(f"Estado '{estado}' no en catálogo.")
    if monto_hospedaje < 0:
        raise ValueError("monto_hospedaje no puede ser negativo.")
    ish = round(monto_hospedaje * e.tasa_pct / 100, 2) if e.cobra_ish else 0.0
    return {
        "estado": e.clave,
        "estado_nombre": e.nombre_estado,
        "cobra_ish": e.cobra_ish,
        "tasa_pct": e.tasa_pct,
        "monto_hospedaje": monto_hospedaje,
        "ish_mxn": ish,
        "monto_total_con_ish": round(monto_hospedaje + ish, 2),
        "fuente": e.portal_url,
        "notas": e.notas,
    }


__all__ = ["EstadoISH", "CATALOGO_ISH", "buscar_ish", "listar_ish", "calcular_ish"]
