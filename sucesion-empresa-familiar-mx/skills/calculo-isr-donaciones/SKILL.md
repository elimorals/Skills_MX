---
name: calculo-isr-donaciones
description: Determina si una donación recibida por persona física está exenta de ISR (Art. 93 fr. XXIII LISR - cónyuges y de ascendientes a descendientes en línea recta sin tope; de descendientes a ascendientes con condición; demás donativos hasta 3 UMA anuales = $128,454.45 en 2026), calcula el ISR del excedente (pago provisional 20% Art. 132 y anual con tarifa Art. 152) y la obligación de informar donativos que sumen más de $600,000 (Art. 90). Usar cuando el usuario diga cálculo isr donaciones, calculo_isr_donaciones, impuesto por donación, mis papás me regalan una casa, donar acciones a un hijo, regalo de dinero SAT, ayuda con cálculo isr donaciones.
allowed-tools: Read, Write
---

# ISR por donaciones (persona física que recibe)

Fuente: LISR texto vigente (Cámara de Diputados, última reforma DOF 01-04-2024; el Paquete 2026 no reformó estos artículos — verificar).

## 1. ¿Está exento? (Art. 93 fr. XXIII)

| Relación donante → donatario | Exención |
|---|---|
| Entre cónyuges | Total, cualquier monto |
| Ascendiente → descendiente en línea recta (padres/abuelos → hijos/nietos) | Total, cualquier monto |
| Descendiente → ascendiente en línea recta (hijos → padres) | Total, **siempre que** el ascendiente no enajene ni done los bienes a otro descendiente en línea recta |
| Cualquier otra persona (hermanos, tíos, sobrinos, amigos, concubinos) | Hasta **3 UMA anuales** en el año: 3 × 117.31 × 365 = **$128,454.45** (2026). El excedente es gravable |

El texto legal dice "tres veces el salario mínimo general... elevado al año"; por la desindexación (DOF 27-01-2016) se usa la UMA.

## 2. Obligación de informar (Art. 90, 2.º párrafo)

Si los préstamos, donativos y premios del año suman **más de $600,000**, deben informarse en la declaración anual **aunque estén exentos**. Si no se informan, el SAT puede considerarlos ingreso omitido (Art. 91, discrepancia fiscal) y gravarlos.

## 3. ISR del excedente gravable

- Ingreso por adquisición de bienes (Art. 130 fr. I). Valor: avalúo cuando el bien lo requiere.
- **Pago provisional 20%** sin deducciones, dentro de 15 días (Art. 132); si es en escritura, lo calcula y entera el notario.
- En la anual se acumula y se aplica la tarifa del Art. 152 (2026: Anexo 8 RMF 2026); el pago provisional se acredita.

```python
from decimal import Decimal as D
UMA = D("117.31")

def isr_donacion(monto: D, relacion: str, otros_donativos_anio: D = D(0)) -> dict:
    exentas = {"conyuge", "ascendiente_a_descendiente", "descendiente_a_ascendiente"}
    if relacion in exentas:
        gravable = D(0)
    else:
        tope = 3 * UMA * 365
        gravable = max(D(0), monto + otros_donativos_anio - tope) - max(D(0), otros_donativos_anio - tope)
    return {"gravable": gravable, "pago_provisional_20": (gravable * D("0.20")).quantize(D("0.01"))}
```

## Ejemplo

Tío dona $500,000 en efectivo a su sobrino (sin otros donativos en 2026):
gravable = 500,000 − 128,454.45 = **$371,545.55**; pago provisional 20% = **$74,309.11**; en la anual se acumula con sus demás ingresos.

## Output esperado

```json
{
  "operation": "calculo-isr-donaciones",
  "data": {
    "relacion": "otro",
    "monto_mxn": "500000.00",
    "exento_mxn": "128454.45",
    "gravable_mxn": "371545.55",
    "pago_provisional_20pct_mxn": "74309.11",
    "informar_en_anual_art90": false,
    "costo_fiscal_para_venta_futura": "valor de avalúo usado para el ISR (Art. 124)"
  },
  "vigencia_validada": false
}
```

`informar_en_anual_art90` es false porque $500,000 no supera $600,000; si recibiera otro donativo o préstamo y el total pasara de $600,000, cambia a true.

## Puntos clave

- Bienes recibidos exentos conservan el **costo y fecha de adquisición del donante** (Art. 124): al venderlos después, la ganancia puede ser alta. Considéralo en el simulador.
- Donación de inmueble: además ISAI/impuesto local de traslado de dominio y derechos registrales, según la entidad (verificar ley de hacienda estatal).
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (RFC, mxn-formato)
- Tarifa anual Art. 152 de 2026: Anexo 8 RMF 2026 (DOF 28-12-2025), apartado C, fracción II

Orientativo: confirma con contador y notario antes de firmar.
