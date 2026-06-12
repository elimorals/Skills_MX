---
name: gastos-deducibles-host
description: Identifica gastos deducibles para el host de Airbnb si está en régimen 612 PFAE (no aplica para 626 RESICO PF). Incluye limpieza profesional con CFDI, mantenimiento, internet/cable/streaming, amenidades para huéspedes (jabón, papel, etc.), reparaciones, electricidad/agua/gas de la unidad rentada (prorrateadas si vives parte del tiempo), seguro de la propiedad, depreciación de la construcción. Usar cuando el usuario diga deducciones airbnb, qué puedo deducir host, gastos deducibles hospedaje.
allowed-tools: Read, Write
---

# Gastos deducibles Airbnb host

## Aplica solo si régimen 612 PFAE

En 626 RESICO PF: NO aplica deducciones acumulables (solo Art. 151 personales).

## Categorías

### 1. Limpieza
- Servicio de limpieza profesional con CFDI (uso G03)
- 100% deducible si la propiedad es exclusivamente Airbnb
- Si vives parte del tiempo: prorratear por noches rentadas vs totales

### 2. Mantenimiento y reparaciones
- Plomería, electricidad, pintura externa
- CFDI obligatorio
- 100% deducible

### 3. Servicios
- Internet, cable, streaming (Netflix, Spotify) si están en la propiedad
- Electricidad, agua, gas
- Si vives parte del año: prorratear

### 4. Amenidades para huéspedes
- Jabón, shampoo, papel, café, café en cápsulas
- Almohadas, toallas, sábanas (depreciables si > $1k MXN)
- CFDI requerido si gasto > $2,000

### 5. Seguro
- Daños a la propiedad
- Responsabilidad civil contra huéspedes
- 100% deducible si exclusivo a Airbnb

### 6. Depreciación
- 5% anual sobre valor de construcción (no terreno)
- Solo si tu nombre figura en escritura

### 7. Renta de la propiedad (si tú la rentas y la sub-rentas en Airbnb)
- Cuidado: muchos contratos prohíben sub-rentar — riesgo legal
- Si está permitido, la renta es deducible al 100%

## Output

```json
{
  "rfc_hash": "...",
  "mes": "2026-06",
  "regimen": "612_PFAE",
  "categorias": {
    "limpieza": {"cfdis": 22, "monto_mxn": "11000.00"},
    "mantenimiento": {"cfdis": 1, "monto_mxn": "1500.00"},
    "servicios": {"prorrata_mxn": "3500.00", "detalle": "Internet+Luz+Agua"},
    "amenidades": {"cfdis": 5, "monto_mxn": "2200.00"},
    "seguro": {"prorrata_mensual_mxn": "850.00"},
    "depreciacion": {"prorrata_mensual_mxn": "5833.00"}
  },
  "total_deducible_mxn": "24883.00",
  "ingreso_bruto_mxn": "40700.00",
  "utilidad_fiscal_estimada_mxn": "15817.00",
  "advertencias": [
    "Si vives parte del año: prorratear servicios al porcentaje real de uso Airbnb",
    "Forma de pago efectivo > $2,000 NO deducible"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Propiedad rentada por ti + sub-rent en Airbnb | Verificar contrato — algunos lo prohíben (riesgo legal) |
| Host con uso mixto (vives 6 meses, rentas 6 meses) | Prorratear todos los gastos al 50% |
| Co-host (otro lo administra y cobra %) | Comisión co-host es gasto deducible (con CFDI) |
| Propiedad heredada sin valor de construcción claro | Pedir avalúo o usar 60% del catastral |

## ⚠ Compliance

- Mismas reglas que arrendador-residencial (forma de pago, 69-B, etc.)
- `vigencia_validada: false`
- Si régimen RESICO PF: no aplica este skill — solo deducciones personales Art. 151
