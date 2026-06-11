"""Catálogos para el sistema SPEI/CLABE de Banxico.

Bancos identificados por su código de 3 dígitos asignado por Banxico. Este
código aparece en:
- Los primeros 3 dígitos de cualquier CLABE (estandarizada)
- El campo "banco emisor/receptor" del CEP
- El prefijo (a veces) de la clave de rastreo SPEI

Fuente: catálogo oficial Banxico SPEI/SPID. Códigos estables desde 1996; nuevas
fintechs se añaden periódicamente (Mercado Pago 722, NU 638, etc.).

⚠ Datos a verificar vigentes: si una clave de rastreo apunta a un banco que NO
está aquí, probablemente es una fintech nueva (post-2024). Reportar para que
se actualice el catálogo.
"""

from __future__ import annotations

# ---------- Bancos (Banca Múltiple) ----------
# Códigos 001-199 corresponden a banca tradicional + fintechs reguladas.

BANCOS_CLABE: dict[str, str] = {
    "002": "Banamex",
    "006": "Bancomext",
    "009": "Banobras",
    "012": "BBVA México",
    "014": "Santander",
    "019": "Banjército",
    "021": "HSBC",
    "030": "Bajío",
    "036": "Inbursa",
    "042": "Mifel",
    "044": "Scotiabank",
    "058": "Banregio",
    "059": "Invex",
    "060": "Bansi",
    "062": "Afirme",
    "072": "Banorte",
    "106": "Bank of America",
    "108": "MUFG Bank",
    "110": "JP Morgan",
    "112": "BMonex",
    "113": "VePor Más",
    "116": "ING",
    "124": "Deutsche Bank",
    "126": "Credit Suisse",
    "127": "Banco Azteca",
    "128": "Autofin",
    "129": "Barclays",
    "130": "Compartamos",
    "132": "BMultiva",
    "133": "Actinver",
    "135": "Nafin",
    "136": "Intercam Banco",
    "137": "BanCoppel",
    "138": "ABC Capital",
    "140": "Consubanco",
    "141": "Volkswagen",
    "143": "CIBanco",
    "145": "BBASE",
    "147": "Bankaool",
    "148": "PagaTodo",
    "150": "Inmobiliario Mexicano",
    "151": "Dondé",
    "152": "Bancrea",
    "154": "Banco Forjadores",
    "155": "ICBC",
    "156": "Sabadell",
    "157": "Shinhan",
    "158": "Mizuho Bank",
    "159": "Bank of China",
    "160": "Banco S3",
    "166": "Banco del Bienestar",
    "168": "Hipotecaria Federal",
    "169": "Banco Inmobiliario Mexicano",
    "194": "Klar",
    "195": "Tribal",
    "196": "Cuenca",
}

# ---------- SOFOMES / Casas de Bolsa / Otros (200-999) ----------
# Códigos altos: casas de bolsa, fintechs no bancarias, instituciones especiales.

OTROS_PARTICIPANTES_CLABE: dict[str, str] = {
    "600": "Monex",
    "601": "GBM",
    "602": "Masari",
    "605": "Value",
    "608": "Vector",
    "613": "Multiva CB",
    "616": "Finamex",
    "617": "Valmex",
    "620": "Profuturo",
    "630": "Intercam CB",
    "631": "CI Bolsa",
    "634": "Fincomún",
    "638": "Nu Mexico",  # NU Financiera SOFOM, opera SPEI vía STP
    "646": "STP",  # Sistema de Transferencias y Pagos — backbone de muchas fintechs
    "652": "Asea",
    "653": "Kuspit",
    "656": "Unagra",
    "659": "Opciones Empresariales del Noroeste",
    "670": "Libertad",
    "674": "AXA",
    "677": "Caja Popular Mexicana",
    "683": "Caja Telefonistas",
    "684": "Transfer",
    "703": "Tesored",
    "706": "Arcus",
    "710": "NVIO",
    "722": "Mercado Pago",
    "728": "Stori",
    "740": "Lector",
    "901": "CLS",
    "902": "Indeval",
}

# Vista combinada — usar para lookup general
BANCOS_TODOS: dict[str, str] = {**BANCOS_CLABE, **OTROS_PARTICIPANTES_CLABE}


# ---------- Tipos de operación SPEI ----------

TIPO_OPERACION_SPEI: dict[str, str] = {
    "1": "Tercero a tercero",
    "3": "Tercero a ventanilla",
    "5": "Tercero a tercero vector",
    "7": "Tercero a participante",
    "10": "Tercero a tercero FSW (Fondeo de Seguros)",
    "11": "Participante a tercero",
    "12": "Participante a tercero vector",
    "13": "Participante a participante",
    "14": "Participante a participante FSW",
    "16": "Devolución no acreditada",
    "17": "Devolución extemporánea",
    "18": "Devolución de devolución",
    "19": "Devolución acreditada",
}


# ---------- Estados de un CEP ----------

ESTADO_CEP: dict[str, str] = {
    "disponible": "CEP emitido por Banxico — el SPEI fue procesado y liquidado.",
    "no_encontrado": "Banxico no encuentra el pago con esos datos. Verificar fecha, monto, clave de rastreo y bancos.",
    "pendiente": "Pago en proceso — Banxico todavía no liquida. Reintentar en unas horas.",
    "rechazado": "El SPEI fue rechazado y no se procesó.",
}


def lookup_banco(codigo: str) -> str | None:
    """Devuelve nombre del banco por código de 3 dígitos. None si no se reconoce."""
    return BANCOS_TODOS.get(codigo.zfill(3))
