"""Catastros estatales unificados — IGECEM (EdoMex), IRCEP (Puebla), Veracruz.

A diferencia del predial (que es municipal), el catastro es ESTATAL en algunos
estados que ejercen la facultad. IGECEM EdoMex es el más grande (125 muns).

Universo: Notarías, peritos valuadores, due-diligence M&A, hipoteca.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


MetodoCatastro = Literal["publica", "publica_captcha", "login", "indirecto", "no_implementado"]


@dataclass
class CatastroEstatal:
    clave: str
    nombre_estado: str
    organismo: str
    cobertura_muns: int  # cuántos muns del estado cubre
    url_portal: str
    url_consulta: str = ""
    identificador_label: str = "Cuenta Catastral"
    identificador_regex: str = r"^\d{6,20}$"
    metodo: MetodoCatastro = "no_implementado"
    notas: str = ""


CATALOGO_CATASTRO_ESTATAL: list[CatastroEstatal] = [
    CatastroEstatal(
        clave="igecem",
        nombre_estado="Estado de México",
        organismo="Instituto de Información e Investigación Geográfica, Estadística y Catastral del Estado de México",
        cobertura_muns=125,
        url_portal="https://igecem.edomex.gob.mx",
        url_consulta="https://igecem.edomex.gob.mx/consulta-cuenta-catastral",
        identificador_label="Cuenta Catastral Única",
        identificador_regex=r"^\d{16}$",  # 16 dígitos
        metodo="publica_captcha",
        notas="125 muns. CCU 16 dígitos = clave estado(2) + mun(3) + zona(3) + manzana(3) + predio(3) + condom(2)",
    ),
    CatastroEstatal(
        clave="ircep",
        nombre_estado="Puebla",
        organismo="Instituto Registral y Catastral del Estado de Puebla",
        cobertura_muns=217,
        url_portal="https://ircep.puebla.gob.mx",
        url_consulta="https://ircep.puebla.gob.mx/consulta-publica",
        identificador_label="Clave Catastral",
        identificador_regex=r"^\d{12,18}$",
        metodo="login",
        notas="Requiere registro de usuario (gratuito).",
    ),
    CatastroEstatal(
        clave="catastro_ver",
        nombre_estado="Veracruz",
        organismo="Dirección General del Catastro del Estado de Veracruz",
        cobertura_muns=212,
        url_portal="https://www.veracruz.gob.mx/finanzas/catastro/",
        identificador_label="Clave Catastral",
        identificador_regex=r"^\d{10,18}$",
        metodo="publica",
        notas="Portal estatal — cobertura completa de los 212 muns.",
    ),
    CatastroEstatal(
        clave="catastro_qroo",
        nombre_estado="Quintana Roo",
        organismo="Instituto del Patrimonio Inmobiliario de QRoo",
        cobertura_muns=11,
        url_portal="https://www.ipi.qroo.gob.mx",
        identificador_label="Clave Catastral",
        metodo="no_implementado",
    ),
    CatastroEstatal(
        clave="catastro_yuc",
        nombre_estado="Yucatán",
        organismo="Instituto de Catastro del Estado de Yucatán",
        cobertura_muns=106,
        url_portal="https://www.catastro.yucatan.gob.mx",
        identificador_label="Clave Catastral",
        metodo="no_implementado",
    ),
]


def buscar_catastro(clave: str) -> CatastroEstatal | None:
    clave_norm = clave.strip().lower()
    for c in CATALOGO_CATASTRO_ESTATAL:
        if c.clave == clave_norm:
            return c
    return None


def listar_catastros() -> list[CatastroEstatal]:
    return list(CATALOGO_CATASTRO_ESTATAL)


__all__ = ["CatastroEstatal", "MetodoCatastro", "CATALOGO_CATASTRO_ESTATAL",
           "buscar_catastro", "listar_catastros"]
