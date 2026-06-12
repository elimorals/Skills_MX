---
name: tramites-placas-tarjeta
description: Guía para trámites menos frecuentes pero críticos: alta de placas (vehículo nuevo o cambio de entidad), reposición de placas perdidas/robadas, reposición de tarjeta de circulación, baja por venta/destrucción, y cambio de propietario. Reúne requisitos por estado, costos aproximados, y checklist de documentos. NO ejecuta el trámite (solo guía + prepara). Usar cuando el usuario diga alta placas, reposición tarjeta circulación, baja vehículo, cambio propietario. NO usar para multas/verificación/refrendo (son skills dedicados).
allowed-tools: Read, Write
---

# Trámites placas y tarjeta de circulación

## Trámites cubiertos

### 1. Alta de placas — vehículo nuevo
**Requisitos comunes:**
- Factura original del vehículo
- ID oficial del propietario
- Comprobante de domicilio (no mayor a 3 meses)
- Pago de derechos (varía por estado, $500-$1,500)
- Comprobante de pago tenencia (si aplica)

### 2. Reposición tarjeta circulación
**Requisitos:**
- Acta MP (denuncia) si fue robo
- ID oficial
- Comprobante de domicilio
- Pago derechos $300-$500

### 3. Reposición de placas perdidas
**Requisitos:**
- Acta MP
- Factura original o copia certificada
- ID + comprobante domicilio
- Pago $1,000-$2,000

### 4. Baja por venta / destrucción
**Requisitos:**
- Placas físicas (se entregan)
- Factura
- ID
- Documento que acredite la venta o destrucción

### 5. Cambio de propietario
**Requisitos:**
- Endoso factura
- ID nuevo propietario + comprobante domicilio
- Pago de derechos por la transferencia

## Output

```json
{
  "tramite": "alta_placas",
  "entidad": "cdmx",
  "requisitos_checklist": [
    {"documento": "factura_original", "obtenido": false, "notas": "..."},
    {"documento": "id_oficial", "obtenido": true},
    {"documento": "comprobante_domicilio", "obtenido": true},
    {"documento": "pago_derechos", "obtenido": false, "monto_estimado_mxn": "1200"}
  ],
  "completitud_pct": 50,
  "costo_total_estimado_mxn": "1200.00",
  "donde_acudir": "Oficinas SEMOVI (CDMX) — cita previa",
  "tiempo_estimado": "1-2 visitas, 2-4 horas total",
  "siguiente_paso": "Agendar cita en portal SEMOVI"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Vehículo importado de USA | Requiere pedimento de importación |
| Vehículo de agencia oficial | Agencia hace el alta inicial, propietario solo recoge |
| Vehículo familiar heredado | Carta poder o sucesión hereditaria |
| Cambio entidad federativa | Baja en estado anterior + alta en nuevo |

## Dependencias

- Catálogo local de trámites por estado
- `mp_cdmx_municipal` (futuro: status de citas)

## ⚠ Compliance

- Trámites cambian de procedimiento — siempre validar con portal oficial actual
- NO ejecutar trámites en línea por usuario (solo guía)
