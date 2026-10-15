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
- Pago de derechos (monto por estado; no hay catálogo 2026 verificado: confirmar en el portal de finanzas)
- Comprobante de pago tenencia (si aplica)

### 2. Reposición tarjeta circulación
**Requisitos:**
- Acta MP (denuncia) si fue robo
- ID oficial
- Comprobante de domicilio
- Pago de derechos (confirmar monto 2026 en el portal)

### 3. Reposición de placas perdidas
**Requisitos:**
- Acta MP
- Factura original o copia certificada
- ID + comprobante domicilio
- Pago de derechos (confirmar monto 2026 en el portal)

### 4. Baja por venta / destrucción
**Requisitos:**
- Placas físicas (se entregan)
- Factura
- ID
- Documento que acredite la venta o destrucción

### 5. Cambio de propietario
**Requisitos:**
- Endoso factura (cadena completa de facturas/endosos)
- Constancia de no adeudo de tenencia/refrendo y multas del vehículo (los adeudos siguen al auto)
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
    {"documento": "pago_derechos", "obtenido": false, "monto_mxn": null, "nota": "confirmar en portal SEMOVI/SAF"}
  ],
  "completitud_pct": 50,
  "costo_total_estimado_mxn": null,
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

## Revisión REPUVE (compra, alta o cambio de propietario)

Antes de comprar un usado o dar de alta, revisa el vehículo en el REPUVE (Registro Público Vehicular, SESNSP):

1. `repuve_consultar_niv(niv)` o `repuve_consultar_placa(placa)`; `repuve_verificar_robado(niv|placa)` para reporte de robo (`mp_repuve`).
2. Estado real del MCP: **entrega a humano** (reCAPTCHA v3). Si la respuesta trae `requiere_humano: true`, entrega `url` y `pasos` al usuario y pídele el resultado.
3. Un reporte de robo `null` significa **desconocido**, nunca "sin reporte". No digas que el auto está limpio sin la consulta oficial.
4. Coteja el NIV (17 caracteres) de la factura contra el de la tarjeta de circulación y el grabado en el vehículo.

## Licencia de conducir (referencia)

CDMX: licencia permanente tipo A por $1,500 durante el periodo de extensión que vence el 31-dic-2026 (prensa citando a la SAF, confianza media; se tramita con Llave CDMX). Otros estados: confirmar en su portal de movilidad.

## Dependencias

- Catálogo local de trámites por estado (sin montos 2026 verificados)
- `mp_repuve` (entrega a humano)
- `mp_tenencia_mx.tenencia_info_estado` para el refrendo del estado

## ⚠ Compliance

- Trámites cambian de procedimiento — siempre validar con portal oficial actual
- NO ejecutar trámites en línea por usuario (solo guía)
