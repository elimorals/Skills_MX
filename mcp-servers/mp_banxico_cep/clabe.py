"""Validación y decodificación de CLABE (18 dígitos) — 100% local.

Estructura CLABE:
    BBB PPP CCCCCCCCCCC D
    ├─┘ ├─┘ ├─────────┘ │
    │   │   │            └── Dígito de control
    │   │   └── Número de cuenta interno del banco (11 dígitos)
    │   └── Código de plaza (3 dígitos) — referencia geográfica
    └── Código de banco (3 dígitos) — ver catalogos.BANCOS_CLABE

Algoritmo dígito de control (oficial Banxico):
    1. Multiplicar cada uno de los primeros 17 dígitos por pesos cíclicos: 3, 7, 1
    2. Tomar el último dígito de cada producto (producto mod 10)
    3. Sumar los 17 últimos-dígitos
    4. resultado = (10 - (suma mod 10)) mod 10

⚠ El algoritmo CLABE difiere del RFC/CURP: los pesos son cíclicos 3,7,1 (no
descendentes), y la tabla es solo dígitos (no letras). Es más simple porque
CLABE es 100% numérica.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_banxico_cep.catalogos import BANCOS_TODOS  # noqa: E402

CLABE_REGEX = re.compile(r"^\d{18}$")
PESOS_CLABE = (3, 7, 1)


def calcular_digito_control_clabe(clabe_17: str) -> int:
    """Calcula el dígito de control para los primeros 17 dígitos.

    Devuelve -1 si el input no tiene 17 dígitos numéricos.
    """
    if len(clabe_17) != 17 or not clabe_17.isdigit():
        return -1
    suma = 0
    for i, ch in enumerate(clabe_17):
        peso = PESOS_CLABE[i % 3]
        suma += (int(ch) * peso) % 10
    return (10 - (suma % 10)) % 10


def validar_clabe(clabe: str) -> dict[str, Any]:
    """Valida formato CLABE y devuelve componentes + verificación de dígito.

    Devuelve siempre el mismo shape con `valida: bool` y `errores`/`alertas`.
    """
    clabe_norm = (clabe or "").strip().replace(" ", "").replace("-", "")
    errores: list[str] = []
    alertas: list[str] = []

    payload: dict[str, Any] = {
        "clabe_input": clabe,
        "clabe_normalizada": clabe_norm,
        "valida": False,
        "banco_codigo": None,
        "banco_nombre": None,
        "plaza_codigo": None,
        "cuenta_interna": None,
        "digito_control_provisto": None,
        "digito_control_calculado": None,
        "errores": errores,
        "alertas": alertas,
    }

    if not CLABE_REGEX.match(clabe_norm):
        errores.append(
            f"CLABE debe ser exactamente 18 dígitos numéricos (recibidos: {len(clabe_norm)} chars)."
        )
        return payload

    banco = clabe_norm[:3]
    plaza = clabe_norm[3:6]
    cuenta = clabe_norm[6:17]
    digito_provisto = int(clabe_norm[17])
    digito_calculado = calcular_digito_control_clabe(clabe_norm[:17])

    payload["banco_codigo"] = banco
    payload["plaza_codigo"] = plaza
    payload["cuenta_interna"] = cuenta
    payload["digito_control_provisto"] = digito_provisto
    payload["digito_control_calculado"] = digito_calculado

    banco_nombre = BANCOS_TODOS.get(banco)
    if banco_nombre:
        payload["banco_nombre"] = banco_nombre
    else:
        alertas.append(
            f"Código de banco '{banco}' no está en el catálogo conocido. "
            "Puede ser una fintech nueva — verificar contra catálogo Banxico vigente."
        )

    if digito_calculado == -1:
        errores.append("No se pudo calcular el dígito de control.")
        return payload
    if digito_provisto != digito_calculado:
        errores.append(
            f"Dígito de control incorrecto. Provisto: {digito_provisto}, "
            f"calculado: {digito_calculado}. La CLABE está mal escrita."
        )
        return payload

    payload["valida"] = True
    return payload


# ---------- Clave de rastreo SPEI ----------
# Cada banco emisor define su formato de clave de rastreo. No hay estándar.
# Algunos patrones comunes (no exhaustivo):
#   BBVA:     MBAN0100xxxxxxxxxxxxxxxx   (MBAN + dígitos)
#   Banamex:  BNETxxxxxxxxxxxx
#   Banorte:  BNET0xxxxxxxxxxxxxx        (a veces)
#   STP:      <UUID-like alfanumérico>
#   Mercado Pago: MERPAGO + dígitos
# Lo que sí es estándar: la clave es alfanumérica, ≥ 8 chars, sin espacios.

CLAVE_RASTREO_REGEX = re.compile(r"^[A-Z0-9]{8,40}$", re.IGNORECASE)

# Heurística por prefijo → emisor probable (no garantizado)
PREFIJOS_CLAVE_RASTREO: dict[str, str] = {
    "MBAN": "BBVA México",
    "BBVA": "BBVA México",
    "BNET": "Banamex / Banorte",  # ambiguo
    "CITI": "Banamex",
    "SANT": "Santander",
    "HSBC": "HSBC",
    "BANORTE": "Banorte",
    "STP": "STP / fintechs",
    "MERPAGO": "Mercado Pago",
    "MP": "Mercado Pago",
    "NU": "NU México",
    "STORI": "Stori",
}


def parsear_clave_rastreo(clave: str) -> dict[str, Any]:
    """Parsea una clave de rastreo SPEI y trata de identificar el emisor.

    NO valida en Banxico — solo extrae info heurística. Para confirmación real
    hay que llamar `generar_cep` o `consultar_pago_por_clave`.
    """
    clave_norm = (clave or "").strip().upper().replace(" ", "")
    payload: dict[str, Any] = {
        "clave_input": clave,
        "clave_normalizada": clave_norm,
        "formato_valido": False,
        "emisor_probable": None,
        "prefijo_detectado": None,
        "sufijo": None,
        "alertas": [],
    }

    if not CLAVE_RASTREO_REGEX.match(clave_norm):
        payload["alertas"].append(
            "Formato no parece clave de rastreo SPEI (debe ser 8-40 chars alfanuméricos). "
            "Verificar transcripción."
        )
        return payload

    payload["formato_valido"] = True

    # Buscar el prefijo más largo que matchea
    prefijo_match = None
    for prefijo in sorted(PREFIJOS_CLAVE_RASTREO, key=len, reverse=True):
        if clave_norm.startswith(prefijo):
            prefijo_match = prefijo
            break

    if prefijo_match:
        payload["prefijo_detectado"] = prefijo_match
        payload["emisor_probable"] = PREFIJOS_CLAVE_RASTREO[prefijo_match]
        payload["sufijo"] = clave_norm[len(prefijo_match):]
    else:
        payload["alertas"].append(
            "No se identificó banco emisor por prefijo. Probablemente una fintech "
            "no listada o una clave personalizada. Esto no impide consultar el CEP — "
            "Banxico decide la validez por los datos del pago, no por el prefijo."
        )

    return payload
