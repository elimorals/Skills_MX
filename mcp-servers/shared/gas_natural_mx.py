"""Catálogo distribuidores gas natural MX (~4M usuarios)."""
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


CATALOGO_GAS_NATURAL: list[DistribuidorGas] = [
    DistribuidorGas("naturgy", "Naturgy México", "CDMX, EdoMex, Hidalgo, Querétaro",
                    "https://www.naturgy.com.mx", metodo="login",
                    poblacion_aprox=1900000,
                    notas="Mayor distribuidor MX. Portal MiNaturgy con login."),
    DistribuidorGas("engie", "ENGIE México", "GDL, Monterrey, varios",
                    "https://www.engie.mx", metodo="login",
                    poblacion_aprox=1500000,
                    notas="Segunda distribuidora. Mi Espacio ENGIE."),
    DistribuidorGas("fenosa", "Fenosa Distribución", "Norte MX",
                    "https://www.fenosa.com.mx", metodo="login",
                    poblacion_aprox=300000),
    DistribuidorGas("ecogas", "Ecogas (Iberdrola)", "Mexicali, Chihuahua, La Laguna",
                    "https://www.ecogas.com.mx", metodo="login",
                    poblacion_aprox=350000),
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
