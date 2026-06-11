"""Catálogos para validación CURP.

Origen: especificación oficial RENAPO (Registro Nacional de Población).

Anatomía de una CURP (18 chars):
    AABB CCDDEE F GGGGG HH I
    ├──┘ ├────┘ │ │ ├─┘ │ │
    │    │      │ │ │   │ └── Dígito verificador (módulo 10 con pesos descendentes)
    │    │      │ │ │   └── Char homonimia: dígito 0-9 = 1900s, letra A-Z = 2000s
    │    │      │ │ └── 3 consonantes interiores (paterno, materno, nombre)
    │    │      │ └── 2 letras código de estado
    │    │      └── Sexo: H (hombre) o M (mujer)
    │    └── Fecha nacimiento AAMMDD (2 dígitos año, mes, día)
    └── 4 letras del nombre: 1ra+1ra-vocal-int paterno, 1ra materno, 1ra nombre

⚠ Datos a verificar vigentes: códigos de estado son estables desde 1996. Si RENAPO
añade un código nuevo (raro), actualizar ESTADOS_CURP.
"""

from __future__ import annotations

# ---------- 32 entidades federativas + extranjero ----------

ESTADOS_CURP: dict[str, str] = {
    "AS": "Aguascalientes",
    "BC": "Baja California",
    "BS": "Baja California Sur",
    "CC": "Campeche",
    "CL": "Coahuila",
    "CM": "Colima",
    "CS": "Chiapas",
    "CH": "Chihuahua",
    "DF": "Ciudad de México",  # Ex DF — la CURP histórica usa DF
    "DG": "Durango",
    "GT": "Guanajuato",
    "GR": "Guerrero",
    "HG": "Hidalgo",
    "JC": "Jalisco",
    "MC": "Estado de México",
    "MN": "Michoacán",
    "MS": "Morelos",
    "NT": "Nayarit",
    "NL": "Nuevo León",
    "OC": "Oaxaca",
    "PL": "Puebla",
    "QT": "Querétaro",
    "QR": "Quintana Roo",
    "SP": "San Luis Potosí",
    "SL": "Sinaloa",
    "SR": "Sonora",
    "TC": "Tabasco",
    "TS": "Tamaulipas",
    "TL": "Tlaxcala",
    "VZ": "Veracruz",
    "YN": "Yucatán",
    "ZS": "Zacatecas",
    "NE": "Nacido en el Extranjero",
}


# ---------- Sexo ----------

SEXO_CURP: dict[str, str] = {
    "H": "Hombre",
    "M": "Mujer",
}


# ---------- Tabla char → número para dígito verificador ----------
# Misma tabla que SAT usa para RFC. Letras A-Z arrancan en 10.
# Ñ ocupa la posición 24, justo después de N.

_TABLA_CARS = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

CHAR_A_NUMERO: dict[str, int] = {c: i for i, c in enumerate(_TABLA_CARS)}


# ---------- Palabras "inconvenientes" reemplazadas por X ----------
# RENAPO sustituye iniciales que formen palabras malsonantes por X.
# Lista oficial publicada por RENAPO (no exhaustiva, pero las más comunes).

PALABRAS_INCONVENIENTES: set[str] = {
    "BACA", "BAKA", "BUEI", "BUEY", "CACA", "CACO", "CAGA", "CAGO",
    "CAKA", "CAKO", "COGE", "COGI", "COJA", "COJE", "COJI", "COJO",
    "COLA", "CULO", "FALO", "FETO", "GETA", "GUEI", "GUEY", "JETA",
    "JOTO", "KACA", "KACO", "KAGA", "KAGO", "KAKA", "KAKO", "KOGE",
    "KOGI", "KOJA", "KOJE", "KOJI", "KOJO", "KOLA", "KULO", "LILO",
    "LOCA", "LOCO", "LOKA", "LOKO", "MAME", "MAMO", "MEAR", "MEAS",
    "MEON", "MIAR", "MION", "MOCO", "MOKO", "MULA", "MULO", "NACA",
    "NACO", "PEDA", "PEDO", "PENE", "PIPI", "PITO", "POPO", "PUTA",
    "PUTO", "QULO", "RATA", "ROBA", "ROBE", "ROBO", "RUIN", "SENO",
    "TETA", "VACA", "VAGA", "VAGO", "VAKA", "VUEI", "VUEY", "WUEI",
    "WUEY",
}


# ---------- Pseudo-CURP (para extranjeros sin CURP definitivo) ----------

PSEUDO_CURP_INDICADOR = "XEXX"  # CURPs que arrancan con XEXX son temporales
