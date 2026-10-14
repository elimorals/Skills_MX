# Conversión de número a letra — reglas para CFDI y contratos

Convención mexicana para escribir montos en letra dentro de documentos legales y CFDIs.

## Formato canónico CFDI

```
($monto_canónico) NÚMERO EN LETRAS PESOS XX/100 M.N.
```

Ejemplos:
- `($1,234.56 MXN) UN MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 M.N.`
- `($1,500,000.00 MXN) UN MILLÓN QUINIENTOS MIL PESOS 00/100 M.N.`
- `($0.50 MXN) CERO PESOS 50/100 M.N.`

## Reglas

1. **Mayúsculas sostenidas** en la versión CFDI.
2. **`PESOS` o `PESOS M.N.`** (Moneda Nacional). Para otras monedas: `DÓLARES AMERICANOS XX/100 USD`.
3. **Centavos como fracción `XX/100`** (siempre dos dígitos).
4. **Sufijo `M.N.`** refuerza moneda nacional. Obligatorio en contratos formales.

## Cardinales españoles — casos que confunden

### Mil
- `1,000` → `UN MIL` en CFDI por convención contable, aunque la RAE permite solo `MIL`.
- `2,000` → `DOS MIL`
- `1,000,000` → `UN MILLÓN` (sí lleva "un")

### Diez a veinte
- `15` → `QUINCE` (no `DIEZ Y CINCO`)
- `20` → `VEINTE` (no `DOS DIEZES`)
- `16` → `DIECISÉIS` (una palabra)
- `21` → `VEINTIUNO` (una palabra)
- `22` → `VEINTIDÓS`
- `30` → `TREINTA`
- `31` → `TREINTA Y UNO` (separado con "y" a partir del 31)

### Centenas
- `100` → `CIEN` (no `CIENTO`) cuando es exactamente 100.
- `101` → `CIENTO UNO` (no `CIEN Y UNO`).
- `200` → `DOSCIENTOS`
- `300` → `TRESCIENTOS`
- `500` → `QUINIENTOS` (irregular, no `CINCOCIENTOS`)
- `700` → `SETECIENTOS` (irregular, no `SIETECIENTOS`)
- `900` → `NOVECIENTOS` (irregular, no `NUEVECIENTOS`)

### Millones
- `1,000,000` → `UN MILLÓN`
- `2,000,000` → `DOS MILLONES`
- `1,500,000` → `UN MILLÓN QUINIENTOS MIL`
- `1,001` → `UN MIL UNO` (en contexto CFDI) o `MIL UNO`
- `1,000,001` → `UN MILLÓN UNO`

## Centavos

Siempre dos dígitos como fracción:
- `$1,234.50` → `... PESOS 50/100 M.N.`
- `$1,234.05` → `... PESOS 05/100 M.N.`
- `$1,234.00` → `... PESOS 00/100 M.N.`

**Nunca** escribir centavos en letra: `... CINCUENTA CENTAVOS` es incorrecto en formato CFDI. Siempre `50/100`.

## Casos edge

### Cero
- `$0.00` → `CERO PESOS 00/100 M.N.`
- `$0.50` → `CERO PESOS 50/100 M.N.`

### Montos en otra moneda
- `$1,234.56 USD` → `($1,234.56 USD) UN MIL DOSCIENTOS TREINTA Y CUATRO DÓLARES AMERICANOS 56/100 USD`

### Negativos (notas de crédito)
- `-$1,234.56` → `MENOS UN MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 M.N.`

### Montos enormes
- `$1,234,567,890.12` → `UN MIL DOSCIENTOS TREINTA Y CUATRO MILLONES QUINIENTOS SESENTA Y SIETE MIL OCHOCIENTOS NOVENTA PESOS 12/100 M.N.`

## Acentos

- `MILLÓN` lleva tilde
- `DÉCIMO`, `VIGÉSIMO`, etc. (en ordinales) llevan tilde — pero los CFDIs no usan ordinales en montos
- En mayúsculas sostenidas SÍ se conservan los acentos (la RAE confirmó esta regla).

## Implementación sugerida

Python tiene la librería `num2words` que cubre español con flag `lang='es'`:

```python
from num2words import num2words

monto = 1234.56
parte_entera = int(monto)
centavos = round((monto - parte_entera) * 100)
letras_enteros = num2words(parte_entera, lang='es').upper()
resultado = f"{letras_enteros} PESOS {centavos:02d}/100 M.N."
# UN MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 M.N.
```

Notas sobre `num2words`:
- Por default usa `mil` (no `un mil`); para CFDI hay que ajustar.
- Maneja acentos correctamente.
- Maneja millones, mil millones, billones (español usa escala larga: billón = 10^12, no 10^9).

## Reservas

La RAE recomienda separar grupos de tres con comas en español: `1,234,567.89`. Esta es la convención mexicana también. **No usar punto como separador de miles** (eso es España/Europa) ni espacio (eso es internacional ISO).

Para documentos bilingües: explicitar la convención usada en una nota al pie.
