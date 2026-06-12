---
name: workflow-corrida-nomina-quincenal
description: Workflow end-to-end de corrida de nómina quincenal. Carga empleados activos, calcula ISR + IMSS + INFONAVIT por cada uno, aplica descuentos (alimentaria, otros), genera CFDI Nómina por empleado, archivo dispersión SPEI, archivo SUA para IDSE, envía recibo al empleado. Usar al cierre de cada quincena. Usar cuando el usuario diga correr nomina, cierre quincena, generar nomina completa.
allowed-tools: Read, Write
---

# Workflow corrida nómina quincenal

## Fase 0 — Pre-requisitos

1. Verificar e.firma patrón vigente (CFDI Nómina requiere)
2. Cargar empleados activos del periodo
3. Verificar que tarifa Art. 96 LISR vigente está cargada (`references/tarifa-art96-anual-{año}.json`)
4. Verificar que cuotas IMSS están vigentes

## Fase 1 — Cálculos por empleado

Por cada empleado activo:

### 1.1 Cálculo ISR Art. 96
Invocar `calculo-isr-salarios-art96` con sueldo bruto del periodo.

### 1.2 Cuotas IMSS obrero
Invocar `cuotas-imss-sbc` para retención al trabajador.

### 1.3 INFONAVIT (si aplica)
Invocar `cuotas-infonavit-5pct` para descuento si tiene crédito.

### 1.4 Otros descuentos
- Alimentaria (orden judicial)
- Préstamos internos
- Cuotas sindicales (si aplica)

### 1.5 Suma neta
neto = sueldo_bruto - ISR - IMSS_obrero - INFONAVIT_descontado - otros_descuentos

## Fase 2 — Emisión CFDIs

Por cada empleado: invocar `cfdi-nomina-quincenal`.

Si pre-timbrado-validation falla: bloquear ese empleado, continuar resto.

## Fase 3 — Generación dispersión SPEI

Generar archivo CSV para banca múltiple con:
- CLABE empleado
- Monto neto
- Concepto: "Nómina Q1 jun 2026"
- Referencia: empleado_id

## Fase 4 — Archivo SUA

Si es fin de mes: invocar `sua-idse-export` con movimientos del mes.

## Fase 5 — Notificación empleados

A cada empleado:
- Email con CFDI XML + PDF
- WhatsApp opcional con resumen

## Fase 6 — Reporte

```json
{
  "workflow": "corrida_nomina_quincenal",
  "periodo": "2026-06-01_2026-06-15",
  "empleados_procesados": 28,
  "cfdis_timbrados_ok": 27,
  "cfdis_bloqueados": 1,
  "razones_bloqueo": ["EMP-005: RFC sin actualizar en padrón"],
  "neto_total_dispersado_mxn": "319390.00",
  "costo_total_empresa_mxn": "447950.00",
  "archivo_spei_path": "...",
  "archivo_sua_path": null,
  "tiempo_total_segundos": 45,
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Empleado sin RFC | Bloquear CFDI, alerta al patrón |
| Empleado con SBC > 25 UMAs | Capar al tope para IMSS |
| Empleado dado de baja mid-quincena | CFDI por días reales + finiquito |
| Vacaciones del periodo | Incluir prima vacacional 25% |
| Bono extraordinario | Tipo de nómina "E" Extraordinaria |
