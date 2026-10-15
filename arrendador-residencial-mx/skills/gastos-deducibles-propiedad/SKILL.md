---
name: gastos-deducibles-propiedad
description: Tracking de gastos deducibles para el arrendador residencial PF en régimen 606 (Arrendamiento), agrupados por propiedad y mes, y comparación contra la deducción ciega del 35% más predial (Art. 115 LISR). Cubre predial, mantenimiento sin mejoras, agua pagada por el dueño, intereses reales de créditos del inmueble, salarios y honorarios, primas de seguro y depreciación del 5% anual de la construcción, más el cálculo de pagos provisionales (mensuales o trimestrales, Art. 116). RESICO PF (626) no permite deducciones. Usar cuando el usuario diga gastos deducibles propiedad, deducciones arrendamiento, deducción ciega, qué puedo deducir, pago provisional renta, declaración arrendador. NO usar para deducciones personales (Art. 151).
allowed-tools: Read, Write
---

# Gastos deducibles — arrendador PF

## Aplicabilidad por régimen

| Régimen | ¿Deducciones? | Nota |
|---|---|---|
| 606 (Arrendamiento) | ✅ Sí | Comprobadas (Art. 115 LISR) o ciega 35% + predial |
| 626 (RESICO PF) | ❌ No | Tasa de 1% a 2.5% sobre ingresos cobrados (Art. 113-E) |
| Asalariado que además renta | Sí, en la parte de arrendamiento (606) | Acumula ambos en la anual |

## Deducciones comprobadas (Art. 115 LISR)

1. **Predial** y contribuciones locales de mejoras/derechos del inmueble (fr. I).
2. **Mantenimiento** que no implique adiciones o mejoras, y **agua** si la paga el dueño (fr. II). Incluye pintura interior o exterior y reparaciones; ampliaciones y mejoras se capitalizan (ver inversiones).
3. **Intereses reales** de créditos usados para comprar, construir o mejorar el inmueble (fr. III). No aplica el tope de 750,000 UDIs; ese tope es de la deducción personal de casa habitación propia (Art. 151 fr. IV).
4. **Salarios, comisiones y honorarios** (p. ej. administración inmobiliaria), con sus impuestos y cuotas de seguridad social (fr. IV).
5. **Primas de seguros** del inmueble (fr. V).
6. **Inversiones en construcciones**, adiciones y mejoras: 5% anual (fr. VI y Art. 34 fr. I). No se deprecia el terreno.

Ejemplo de depreciación: casa de $2,000,000 (construcción $1,400,000 + terreno $600,000) → $1,400,000 × 5% = **$70,000** al año.

Requisitos (Art. 147 LISR): CFDI a tu RFC; pagos > $2,000 con transferencia, cheque o tarjeta; proveedor fuera de la lista 69-B definitiva.

## Deducción ciega

En lugar de las comprobadas, puedes deducir **35% de los ingresos + el predial pagado** (Art. 115, último párrafo). Se elige en el primer pago provisional del año y se mantiene en el ejercicio (confianza media: RLISR; confirmar con contador).

```python
def deduccion(ingresos, gastos_comprobados, predial, usa_ciega):
    return ingresos * 0.35 + predial if usa_ciega else gastos_comprobados
```

## Pagos provisionales (Art. 116 LISR)

- Base = ingresos del periodo − deducciones del periodo; se aplica la tarifa del Art. 96 (Anexo 8 RMF 2026) y se acredita la retención de 10% que hayan hecho personas morales.
- **Mensual**, a más tardar el día 17 del mes siguiente.
- **Trimestral** si solo tienes ingresos por arrendamiento y no exceden 10 UMA mensuales (UMA 2026: $117.31 × 30.4 × 10 = $35,662.24 al mes).

## Output

```json
{
  "operation": "gastos_deducibles_propiedad",
  "rfc_hash": "...",
  "regimen": "606",
  "ejercicio": 2025,
  "propiedades": {
    "RN-1A": {
      "predial_anual": "5000.00",
      "mantenimiento": "12000.00",
      "agua_y_servicios": "3000.00",
      "intereses_reales_credito": "0.00",
      "depreciacion_anual": "70000.00",
      "primas_seguro": "8000.00",
      "salarios_honorarios": "0.00",
      "total_anual_mxn": "98000.00"
    }
  },
  "ingresos_arrendamiento_anuales_mxn": "144000.00",
  "comparativo": {
    "comprobadas_mxn": "98000.00",
    "ciega_35_mas_predial_mxn": "55400.00",
    "conviene": "comprobadas"
  },
  "base_gravable_estimada_mxn": "46000.00",
  "advertencias": [
    "Depreciación estimada: validar valor de construcción con escritura o avalúo",
    "Intereses = 0: confirmar que no hay crédito vigente"
  ],
  "vigencia_validada": false
}
```

Cálculos: 5,000 + 12,000 + 3,000 + 70,000 + 8,000 = 98,000; ciega = 144,000 × 35% + 5,000 = 55,400; base = 144,000 − 98,000 = 46,000.

## Casos edge

| Caso | Acción |
|---|---|
| Propiedad sin crédito | Omitir intereses |
| Propiedad heredada sin valor de construcción claro | Avalúo que separe terreno y construcción |
| Decoración o mobiliario | No es mantenimiento; mobiliario es inversión al 10% (Art. 34 fr. III) si se renta amueblado |
| Ampliación o mejora | Se capitaliza y deprecia al 5% |
| Multas y recargos | No deducibles |
| Pagos en efectivo > $2,000 | No deducibles |

## Dependencias

- `mp_sat_portal` (`sat_consultar_69b_efos` para proveedores)
- `mp_facturama_extendido` (`facturama_buscar_cfdis`, requiere credenciales)
- Tracker de propiedades y de gastos

## ⚠ Compliance

- Comprobadas o ciega: una sola opción por ejercicio.
- RESICO PF: emitir reporte indicando que no hay deducciones.
- `vigencia_validada: false`: el contador valida antes de la declaración.
