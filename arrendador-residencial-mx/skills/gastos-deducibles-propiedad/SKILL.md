---
name: gastos-deducibles-propiedad
description: Tracking de gastos deducibles para el arrendador residencial PF, agrupados por propiedad y mes. Cubre las categorías típicas: impuesto predial (deducible en arrendamiento), mantenimiento estructural, reparaciones autorizadas, agua y servicios pagados por el dueño, intereses de hipoteca de la propiedad rentada (si aplica), depreciación del 5% anual sobre valor de construcción, primas de seguro del inmueble. Aplica reglas específicas del régimen (PFAE 612 o RESICO PF 626 — RESICO no permite deducciones acumulables). Genera reporte deducible para integrar en la declaración anual. Usar cuando el usuario diga gastos deducibles propiedad, deducciones arrendamiento, qué puedo deducir, declaración arrendador. NO usar para deducciones personales (Art. 151).
allowed-tools: Read, Write
---

# Gastos deducibles — arrendador PF

## Aplicabilidad por régimen

| Régimen | Aplica deducciones acumulables | Nota |
|---|---|---|
| 612 (PFAE arrendamiento) | ✅ SÍ | Deducciones bajo Art. 142 LISR |
| 626 (RESICO PF) | ❌ NO | Régimen simplificado — solo tasa sobre ingresos cobrados |
| 605 (asalariado + arrendamiento) | Sólo arrendamiento parte 612 | Mixto |

Este skill aplica **solo a régimen 612**. Para RESICO PF emitir reporte indicando "no aplica deducciones".

## Categorías deducibles (Art. 142 LISR)

### 1. Impuesto predial
- 100% deducible
- Por cada propiedad
- CFDI o recibo oficial del municipio
- Mensual o anual

### 2. Mantenimiento estructural
- Reparaciones mayores (techo, plomería estructural, instalación eléctrica)
- Pintura externa (no interior — eso es ornamental)
- CFDI con uso G03

### 3. Servicios pagados por el dueño
- Agua, mantenimiento de áreas comunes del condominio (cuota)
- NO incluye luz, gas, internet (eso paga el inquilino)

### 4. Intereses de hipoteca
- Solo del año del crédito sobre la propiedad rentada
- Banco emite constancia anual de intereses reales
- Hasta 750k UDIs

### 5. Depreciación
- 5% anual sobre valor de construcción (no terreno)
- Ejemplo: casa con valor $2,000,000 (construcción $1,400,000 + terreno $600,000)
  - Depreciación anual deducible: $1,400,000 * 5% = $70,000

### 6. Prima de seguro del inmueble
- Solo de daños / contenidos
- 100% deducible
- CFDI del seguro

### 7. Salarios de personal de la propiedad (si aplica)
- Conserje, jardinero, etc. — solo si están dados de alta
- Cuotas IMSS patronales

### 8. Honorarios de gestión inmobiliaria (si los hay)
- Comisión cobrada por inmobiliaria administradora
- CFDI con uso G03

## Cálculo

### Por mes

```python
total_deducciones_mes = (
    predial_mes
    + mantenimiento_mes
    + servicios_pagados_dueño_mes
    + intereses_hipoteca_mes
    + (depreciacion_anual / 12)
    + (prima_seguro_anual / 12)
    + salarios_mes
    + honorarios_administracion_mes
)
```

### Validaciones

- CFDI debe estar a nombre del arrendador (su RFC)
- Forma de pago **no efectivo** para montos > $2,000 (recomendable validar todos)
- Si CFDI cancelado → excluir
- Si proveedor en lista 69-B definitivo → excluir + warning

## Output

```json
{
  "operation": "gastos_deducibles_propiedad",
  "rfc_hash": "...",
  "regimen": "612",
  "ejercicio": 2025,
  "propiedades": {
    "RN-1A": {
      "predial_anual": "5000.00",
      "mantenimiento": "12000.00",
      "servicios": "3000.00",
      "intereses_hipoteca": "0.00",
      "depreciacion_anual": "70000.00",
      "primas_seguro": "8000.00",
      "salarios": "0.00",
      "honorarios_administracion": "0.00",
      "total_anual_mxn": "98000.00"
    }
  },
  "total_deducciones_acumulables_mxn": "98000.00",
  "ingresos_arrendamiento_anuales_mxn": "144000.00",
  "utilidad_fiscal_estimada_arrendamiento_mxn": "46000.00",
  "advertencias": [
    "Depreciación es estimada — validar con avalúo o documentos catastrales",
    "Intereses hipoteca = 0 — confirmar que no hay crédito vigente"
  ],
  "vigencia_validada": false
}
```

## Opción simplificada: deducción ciega 35%

Alternativa al rastreo de gastos: deducir el **35% de los ingresos** (sin comprobar).

```python
if usuario.elige_deduccion_ciega:
    deduccion = ingresos_arrendamiento * 0.35
else:
    deduccion = sum_gastos_comprobados
```

Conviene si gastos comprobados < 35% de ingresos. Conviene comparar ambos escenarios antes de elegir.

## Casos edge

| Caso | Acción |
|---|---|
| Propiedad sin hipoteca | Saltar categoría 4 |
| Propiedad heredada (sin valor de construcción claro) | Pedir avalúo o usar % del catastral (60% típico) |
| Reparaciones cosméticas (pintura interior, decoración) | NO deducibles — uso ornamental |
| Mejoras estructurales (ampliación) | Capitalizar (suman al valor del inmueble, depreciable) |
| Multas por trámites tardíos | NO deducibles |
| Pagos en efectivo > $2,000 | NO deducibles para impuestos (regla SAT) |

## Dependencias

- `mp_facturama_extendido` (validar CFDIs recibidos)
- `mp_sat_portal` (consultar 69-B de proveedores)
- Tracker de propiedades + tracker de gastos

## ⚠ Compliance

- Deducción ciega 35% vs comprobada: declarar UNA en la anual, no ambas
- Si régimen RESICO PF: emitir reporte pero indicar que NO se aplican estas deducciones (régimen simplificado)
- `vigencia_validada: false` — contador valida en declaración anual
