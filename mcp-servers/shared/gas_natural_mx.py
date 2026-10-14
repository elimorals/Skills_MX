"""Catálogo distribuidores gas natural MX.

Ningún distribuidor ofrece consulta pública de recibo (todos piden login del
titular). Lo público y real son las tarifas: la Directiva DIR-GAS-001-2007
(disp. 21.1) obliga a publicar la lista de tarifas máximas aprobadas por la
CRE/CNE, y los distribuidores publican el precio mensual del gas trasladado.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DistribuidorGas:
    clave: str
    nombre: str
    zona: str
    url_portal: str
    metodo: str = "login"
    poblacion_aprox: int = 0
    notas: str = ""
    tarifas_url: str = ""  # página pública de tarifas verificada en vivo


CATALOGO_GAS_NATURAL: list[DistribuidorGas] = [
    DistribuidorGas("naturgy", "Naturgy México", "CDMX, EdoMex, Hidalgo, Querétaro",
                    "https://www.naturgy.com.mx", metodo="login",
                    poblacion_aprox=1900000,
                    notas="Portal MiNaturgy con login. 2026-10-14: sin página pública de tarifas localizada."),
    DistribuidorGas("engie", "ENGIE México", "GDL, Monterrey, varios",
                    "https://www.engie.mx", metodo="login",
                    poblacion_aprox=1500000,
                    notas="2026-10-14: engie.mx no resuelve en DNS."),
    DistribuidorGas("fenosa", "Fenosa Distribución", "Norte MX",
                    "https://www.fenosa.com.mx", metodo="login",
                    poblacion_aprox=300000),
    DistribuidorGas("ecogas", "Ecogas México", "Mexicali, Chihuahua, Durango, La Laguna",
                    "https://www.ecogas.com.mx", metodo="login",
                    poblacion_aprox=350000,
                    tarifas_url="https://www.ecogas.com.mx/tarifas.php",
                    notas="Publica precio mensual por zona y lista de tarifas máximas (PDF). Permiso G/013/DIS/1997."),
    DistribuidorGas("gasnatdf", "Gas Natural del Norte", "Norte",
                    "https://www.gasnatural.com.mx", metodo="login",
                    poblacion_aprox=200000),
]


def buscar_distribuidor(clave: str) -> DistribuidorGas | None:
    cn = clave.strip().lower()
    for d in CATALOGO_GAS_NATURAL:
        if d.clave == cn:
            return d
    return None


__all__ = ["DistribuidorGas", "CATALOGO_GAS_NATURAL", "buscar_distribuidor"]
