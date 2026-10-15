---
name: aguinaldo-y-ptu-anual
description: Calcula aguinaldo (mínimo 15 días de salario, Art. 87 LFT, a más tardar el 20 de diciembre) y PTU (10% de la renta gravable, Arts. 117-131 LFT, con tope de 3 meses de salario o promedio de 3 años) por empleado, con la parte exenta de ISR 2026 (30 UMA aguinaldo, 15 UMA PTU) y su CFDI de nómina extraordinaria. Usar cuando el usuario diga aguinaldo, aguinaldo proporcional, prima navideña, PTU, reparto de utilidades, utilidades a trabajadores, tope PTU.
allowed-tools: Read, Write
---

# Aguinaldo + PTU anual

## Aguinaldo (Art. 87 LFT)

- **Mínimo 15 días de salario** (salario diario, no SBC); el contrato o CCT puede dar más.
- Pago **antes del 20 de diciembre**.
- Proporcional si no laboró el año completo (incluye a quien ya se fue: va en el finiquito).

```python
def aguinaldo(salario_diario: D, dias_laborados: int, dias_aguinaldo: int = 15) -> D:
    return (salario_diario * dias_aguinaldo * dias_laborados / 365).quantize(D("0.01"))
```

**Exento de ISR:** hasta 30 UMA (Art. 93 fr. XIV LISR) = 30 × $117.31 = **$3,519.30** (2026). El excedente es gravable; la retención puede hacerse con la tarifa del Art. 96 sumándolo al mes o con el procedimiento opcional del Art. 174 RLISR.

## PTU (Arts. 117-131 LFT)

- **10% de la renta gravable** del patrón del ejercicio anterior (resolución de la Comisión Nacional; base Art. 9 LISR).
- Plazo: **dentro de los 60 días** siguientes a la fecha en que debe pagarse el impuesto anual (Art. 122): PM a más tardar **30 de mayo**, PF **29 de junio**.
- Reparto (Art. 123): 50% por días trabajados en el año, 50% en proporción al salario (salario por cuota diaria, sin prestaciones).
- **Tope individual** (Art. 127 fr. VIII, reforma DOF 23-04-2021): 3 meses de salario o el promedio de PTU recibida en los últimos 3 años, lo que más favorezca al trabajador.
- Trabajadores de confianza: su salario para el reparto se topa al del sindicalizado/de base de mayor salario + 20% (Art. 127 fr. II).

### Quién no participa (Art. 127 LFT)
- Directores, administradores y gerentes generales.
- Trabajadores eventuales con menos de 60 días trabajados en el año.
- Quien presta servicios profesionales por honorarios (no es trabajador).
- Trabajadores del hogar.
- Empresas exentas (Art. 126: primer año de operación, etc.) no reparten.

**Exento de ISR:** hasta 15 UMA = **$1,759.65** (2026).

## Ejemplo recalculado

Salario diario $600, 320 días laborados en 2026:
600 × 15 × 320 / 365 = **$7,890.41**; exento $3,519.30; gravable **$4,371.11**.

```json
{
  "ejercicio": 2026,
  "concepto": "aguinaldo",
  "empleado_id_hash": "...",
  "dias_laborados_año": 320,
  "dias_aguinaldo_aplicables": 15,
  "salario_diario_mxn": "600.00",
  "aguinaldo_bruto_mxn": "7890.41",
  "exento_30_uma": "3519.30",
  "aguinaldo_gravable_mxn": "4371.11",
  "isr_a_retener_mxn": "<tarifa Art. 96 LISR o Art. 174 RLISR — usar calculo-isr-salarios-art96>",
  "deadline_pago": "2026-12-19",
  "cfdi_nomina_extraordinario_pendiente": true,
  "vigencia_validada": true
}
```

El 20-dic-2026 es domingo: programa el pago a más tardar el viernes 18 o sábado 19 según tu calendario.

CFDI: nómina tipo `E` (extraordinaria); percepciones 002 (gratificación anual/aguinaldo) y 003 (PTU) del catálogo `c_TipoPercepcion`.

## ⚠ Sanciones

- Aguinaldo no pagado: multa genérica de 50 a 5,000 UMA (Art. 1002 LFT).
- PTU no repartida: 250 a 5,000 UMA (Art. 994 fr. I LFT), además de la obligación de pago.
- Valida montos y retenciones con tu contador.
