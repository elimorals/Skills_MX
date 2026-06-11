"""Validación estructural CURP — 100% local, sin red, instantánea.

Lo que sí cubre este módulo:
- Formato (longitud, charset, regex por posición)
- Dígito verificador (algoritmo módulo 10 con tabla SAT)
- Coherencia de fecha embebida + char homonimia → siglo
- Decodificación de sexo, estado, fecha
- Generación reversa (datos → CURP esperada)
- Validación batch

Lo que NO cubre (eso requiere RENAPO con Playwright):
- ¿Existe esta CURP en el padrón real?
- ¿Está vigente o duplicada?
- ¿La persona realmente se llama así?

Una CURP estructuralmente válida + verificador correcto NO garantiza que exista
— el algoritmo permite generar CURPs sintéticas que parecen reales. Para
existencia, llamar `consultar_renapo_via_playwright`.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_curp_renapo.catalogos import (  # noqa: E402
    CHAR_A_NUMERO,
    ESTADOS_CURP,
    PALABRAS_INCONVENIENTES,
    PSEUDO_CURP_INDICADOR,
    SEXO_CURP,
)

# Regex estricta por posición:
# - 1-4: 4 letras (incluyendo Ñ y X)
# - 5-10: 6 dígitos (fecha AAMMDD)
# - 11: H o M
# - 12-13: 2 letras (código de estado)
# - 14-16: 3 consonantes (puede ser X por reemplazo de palabras inconvenientes)
# - 17: 1 char alfanumérico (homonimia: 0-9 para 1900s, A-Z para 2000s)
# - 18: 1 dígito (verificador)
CURP_REGEX = re.compile(
    r"^[A-ZÑX][AEIOUX][A-ZÑX][A-ZÑX]"  # 4 letras del nombre
    r"\d{6}"  # AAMMDD
    r"[HM]"  # sexo
    r"[A-Z]{2}"  # estado
    r"[B-DF-HJ-NP-TV-Z]{3}"  # consonantes (excluye vocales y Ñ)
    r"[0-9A-Z]"  # homonimia
    r"\d$"  # dígito verificador
)


def normalizar(curp: str) -> str:
    """Sube a mayúsculas, quita acentos y espacios. NO valida."""
    if not curp:
        return ""
    # NFD descompone acentos; el filtro quita los diacríticos
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", curp) if unicodedata.category(c) != "Mn"
    )
    return sin_acentos.upper().strip().replace(" ", "")


# ---------- dígito verificador ----------


def calcular_digito_verificador(curp_17: str) -> int:
    """Calcula el dígito verificador para los primeros 17 chars.

    Algoritmo RENAPO/SAT:
        1. Cada char[i] (i = 1..17) → número via CHAR_A_NUMERO
        2. Multiplicar por peso (18 - i)  ⇒ pesos 17, 16, 15, …, 1
        3. Sumar
        4. d = (10 - (suma mod 10)) mod 10

    Si curp_17 contiene un char fuera de la tabla, devuelve -1 (señal de error).
    """
    if len(curp_17) != 17:
        return -1
    suma = 0
    for i, ch in enumerate(curp_17, start=1):
        n = CHAR_A_NUMERO.get(ch)
        if n is None:
            return -1
        suma += n * (18 - i)
    return (10 - (suma % 10)) % 10


# ---------- derivaciones puras ----------


def derivar_fecha_nacimiento(curp: str) -> date | None:
    """Decodifica fecha de nacimiento desde chars 5-10 + char 17 (siglo).

    El char 17 (homonimia) resuelve si AA es 1900s o 2000s:
        - dígito 0-9  → siglo XX (1900s)
        - letra A-Z   → siglo XXI (2000s)

    Devuelve None si los chars de fecha no son numéricos o la fecha es inválida
    (ej. mes 13, día 32, 29 feb en año no bisiesto).
    """
    curp = normalizar(curp)
    if len(curp) != 18:
        return None
    aa_str, mm_str, dd_str = curp[4:6], curp[6:8], curp[8:10]
    homonimia = curp[16]
    if not (aa_str.isdigit() and mm_str.isdigit() and dd_str.isdigit()):
        return None

    siglo = 1900 if homonimia.isdigit() else 2000
    aa = int(aa_str)
    yyyy = siglo + aa
    try:
        return date(yyyy, int(mm_str), int(dd_str))
    except ValueError:
        return None


def derivar_sexo(curp: str) -> str | None:
    """Devuelve 'H' o 'M' o None si el char 11 no es ninguno."""
    curp = normalizar(curp)
    if len(curp) < 11:
        return None
    sx = curp[10]
    return sx if sx in SEXO_CURP else None


def derivar_estado(curp: str) -> tuple[str, str] | None:
    """Devuelve (código, nombre del estado) o None si no se reconoce."""
    curp = normalizar(curp)
    if len(curp) < 13:
        return None
    codigo = curp[11:13]
    nombre = ESTADOS_CURP.get(codigo)
    return (codigo, nombre) if nombre else None


# ---------- validación full ----------


def validar_estructura(curp_input: str) -> dict[str, Any]:
    """Valida una CURP completa y devuelve un payload estructurado.

    Devuelve siempre el mismo shape, con `valido_estructura: bool` y listas
    `errores`/`alertas`. Una CURP que cumple regex pero falla el dígito devuelve
    `valido_estructura=False` y reporta el error en `errores`.
    """
    curp = normalizar(curp_input)
    errores: list[str] = []
    alertas: list[str] = []

    payload: dict[str, Any] = {
        "curp_input": curp_input,
        "curp_normalizado": curp,
        "valido_estructura": False,
        "fecha_nacimiento": None,
        "sexo": None,
        "estado_codigo": None,
        "estado_nombre": None,
        "consonantes_interiores": None,
        "char_homonimia": None,
        "siglo_nacimiento": None,
        "digito_verificador_calculado": None,
        "digito_verificador_provisto": None,
        "es_pseudo_curp": False,
        "alertas": alertas,
        "errores": errores,
    }

    if len(curp) != 18:
        errores.append(f"Longitud incorrecta: {len(curp)} caracteres (se esperan 18).")
        return payload

    if not CURP_REGEX.match(curp):
        errores.append("Formato no coincide con el patrón CURP por posición.")
        return payload

    # Pseudo-CURP indicator
    if curp.startswith(PSEUDO_CURP_INDICADOR):
        payload["es_pseudo_curp"] = True
        alertas.append(
            "Pseudo-CURP (XEXX...): es una CURP temporal usada para extranjeros "
            "sin CURP definitiva. Válida estructuralmente pero RENAPO no la "
            "tiene en padrón oficial."
        )

    # Palabras inconvenientes — si las 4 primeras letras forman una palabra mala
    # SIN reemplazo, alertar (RENAPO debió haber puesto X en la 2da letra)
    primeras_4 = curp[:4]
    if primeras_4 in PALABRAS_INCONVENIENTES:
        alertas.append(
            f"Las primeras 4 letras ('{primeras_4}') forman una palabra "
            "inconveniente que RENAPO normalmente reemplaza con X en la 2da posición. "
            "Verificar que la CURP esté actualizada."
        )

    # Estado
    estado_codigo = curp[11:13]
    estado_nombre = ESTADOS_CURP.get(estado_codigo)
    if not estado_nombre:
        errores.append(f"Código de estado '{estado_codigo}' no es válido.")
        return payload
    payload["estado_codigo"] = estado_codigo
    payload["estado_nombre"] = estado_nombre

    # Sexo
    payload["sexo"] = curp[10]

    # Char homonimia + siglo
    homonimia = curp[16]
    payload["char_homonimia"] = homonimia
    payload["siglo_nacimiento"] = 1900 if homonimia.isdigit() else 2000

    # Fecha nacimiento
    fecha = derivar_fecha_nacimiento(curp)
    if fecha is None:
        errores.append(
            "Fecha de nacimiento embebida en la CURP no es una fecha válida del calendario."
        )
        return payload
    payload["fecha_nacimiento"] = fecha.isoformat()

    # Coherencia con fecha actual (no nacer en el futuro)
    hoy = date.today()
    if fecha > hoy:
        errores.append(f"Fecha de nacimiento {fecha.isoformat()} está en el futuro.")
        return payload
    edad = _edad_anios(fecha, hoy)
    if edad > 120:
        alertas.append(f"Edad calculada ({edad} años) es atípicamente alta — verificar.")

    # Consonantes interiores
    payload["consonantes_interiores"] = curp[13:16]

    # Dígito verificador
    digito_provisto = int(curp[17])
    digito_calculado = calcular_digito_verificador(curp[:17])
    payload["digito_verificador_provisto"] = digito_provisto
    payload["digito_verificador_calculado"] = digito_calculado
    if digito_calculado == -1:
        errores.append("No se pudo calcular el dígito verificador (char fuera de tabla).")
        return payload
    if digito_provisto != digito_calculado:
        errores.append(
            f"Dígito verificador incorrecto. Provisto: {digito_provisto}, "
            f"esperado: {digito_calculado}. La CURP está mal escrita o el "
            "dígito se modificó."
        )
        return payload

    payload["valido_estructura"] = True
    return payload


def _edad_anios(nacimiento: date, hoy: date) -> int:
    edad = hoy.year - nacimiento.year
    if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
        edad -= 1
    return edad


# ---------- batch ----------


def validar_lote(curps: list[str]) -> dict[str, Any]:
    """Valida una lista de CURPs y devuelve resumen + detalle por CURP."""
    resultados = [validar_estructura(c) for c in curps]
    validos = sum(1 for r in resultados if r["valido_estructura"])
    return {
        "total": len(curps),
        "validos": validos,
        "invalidos": len(curps) - validos,
        "detalle": resultados,
    }


# ---------- generación reversa ----------


def generar_curp_desde_datos(
    primer_apellido: str,
    segundo_apellido: str,
    nombre: str,
    fecha_nacimiento: date | str,
    sexo: str,
    estado_codigo: str,
    char_homonimia: str = "0",
) -> dict[str, Any]:
    """Genera la CURP esperada a partir de datos personales.

    Útil para:
    - Validar que una CURP recibida es la que correspondería a los datos del padrón.
    - Sugerir la CURP a alguien que no la recuerda (con char homonimia estimado).

    ⚠ El `char_homonimia` se asigna por RENAPO según orden de registro y NO se
    puede derivar de los datos. Por default usa '0' (primer registro del siglo XX);
    para nacidos en 2000+ usa 'A'. Si el resultado no matchea con la CURP real,
    probablemente es porque RENAPO le asignó otro char (ej. 1, 2, ... o B, C, ...).

    Devuelve dict con curp_generada + componentes_intermedios para debug.
    """
    errores: list[str] = []

    if isinstance(fecha_nacimiento, str):
        try:
            fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
        except ValueError:
            errores.append(f"Fecha '{fecha_nacimiento}' no es ISO 8601 válida.")
            return {"valido": False, "errores": errores, "curp_generada": None}

    sexo = sexo.upper().strip()
    if sexo not in SEXO_CURP:
        errores.append(f"Sexo '{sexo}' debe ser 'H' o 'M'.")
    if estado_codigo.upper() not in ESTADOS_CURP:
        errores.append(f"Estado '{estado_codigo}' no es válido (ej. DF, JC, NL).")

    if errores:
        return {"valido": False, "errores": errores, "curp_generada": None}

    pa = normalizar(primer_apellido)
    ma = normalizar(segundo_apellido) or "X"  # extranjeros sin segundo apellido
    no = normalizar(_quitar_articulos(nombre))

    # 4 letras del nombre
    pa_consonante_interior = _primera_consonante_interior(pa) or "X"
    ma_consonante_interior = _primera_consonante_interior(ma) or "X"
    no_consonante_interior = _primera_consonante_interior(no) or "X"

    l1 = pa[0] if pa else "X"
    l2 = _primera_vocal_interior(pa) or "X"
    l3 = ma[0] if ma else "X"
    l4 = no[0] if no else "X"
    primeras_4 = (l1 + l2 + l3 + l4).upper()
    # Si forma palabra inconveniente, reemplazar 2da letra por X
    if primeras_4 in PALABRAS_INCONVENIENTES:
        primeras_4 = l1 + "X" + l3 + l4

    # Fecha AAMMDD
    aamm_dd = fecha_nacimiento.strftime("%y%m%d")

    # Char homonimia auto-derivado si no se proveyó explícitamente
    if char_homonimia == "0" and fecha_nacimiento.year >= 2000:
        char_homonimia = "A"
    char_homonimia = char_homonimia.upper()[:1]

    # 17 primeros chars sin dígito verificador
    base = (
        primeras_4
        + aamm_dd
        + sexo
        + estado_codigo.upper()
        + pa_consonante_interior
        + ma_consonante_interior
        + no_consonante_interior
        + char_homonimia
    )
    base = base[:17]
    if len(base) != 17:
        return {
            "valido": False,
            "errores": [f"Base generada quedó con {len(base)} chars (se esperaban 17)."],
            "curp_generada": None,
        }

    digito = calcular_digito_verificador(base)
    if digito == -1:
        return {
            "valido": False,
            "errores": ["No se pudo calcular dígito (char fuera de tabla)."],
            "curp_generada": None,
        }

    curp_generada = base + str(digito)
    return {
        "valido": True,
        "errores": [],
        "curp_generada": curp_generada,
        "componentes": {
            "primeras_4_letras": primeras_4,
            "fecha_aammdd": aamm_dd,
            "sexo": sexo,
            "estado": estado_codigo.upper(),
            "consonantes_interiores": pa_consonante_interior
            + ma_consonante_interior
            + no_consonante_interior,
            "char_homonimia": char_homonimia,
            "digito_verificador": digito,
        },
        "nota_homonimia": (
            "RENAPO asigna el char homonimia según orden de registro. Si el "
            "resultado no matchea con la CURP real, probar incrementar (1, 2, ... "
            "para 1900s; B, C, ... para 2000s)."
        ),
    }


_ARTICULOS = {"DE", "LA", "LAS", "LOS", "DEL", "Y", "MC", "MAC", "VAN", "VON"}


def _quitar_articulos(nombre: str) -> str:
    """RENAPO ignora artículos y preposiciones al derivar las letras."""
    palabras = [p for p in normalizar(nombre).split() if p not in _ARTICULOS]
    return " ".join(palabras) if palabras else normalizar(nombre)


def _primera_vocal_interior(palabra: str) -> str | None:
    """Primera vocal de la palabra excluyendo la 1ra letra."""
    for ch in palabra[1:]:
        if ch in "AEIOU":
            return ch
    return None


def _primera_consonante_interior(palabra: str) -> str | None:
    """Primera consonante después de la 1ra letra. Excluye vocales y Ñ."""
    for ch in palabra[1:]:
        if ch in "BCDFGHJKLMNPQRSTVWXYZ":
            return ch
    return None
