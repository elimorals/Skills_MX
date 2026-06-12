---
name: tramites-residencia-inm
description: Guía completa de trámites de residencia ante el Instituto Nacional de Migración (INM) México. Cubre solicitud de residencia temporal (1 año renovable hasta 4), residencia permanente (sin caducidad), cambio de condición migratoria, vinculo familiar (matrimonio mexicano), oferta de empleo. Listado de requisitos por trámite + costos vigentes. Usar cuando el usuario diga residencia mexico, INM tramite, visa residente, cambiar condicion migratoria.
allowed-tools: Read, Write
---

# Trámites residencia INM

## Tipos de residencia

### Residente temporal
- Plazo: 1-4 años (renovaciones)
- Trabajar: permiso adicional
- Familia: dependientes pueden venir
- Pasos: solicitud consular (en país origen) o canje (si entró como visitante)
- Costo: ~$5,500 MXN inicial + $5,500 anual

### Residente permanente
- Sin caducidad
- Trabajar: permiso automático
- Requisitos: 4 años residencia temporal previa, o vínculo familiar mexicano, o pensionado con ingreso estable
- Costo: ~$7,000 MXN

### Otros
- Refugio/asilo (gratuito)
- Estudiante (1 año renovable)
- Visitante (180 días, sin permiso trabajo)

## Documentos típicos

- Pasaporte vigente
- Acta nacimiento apostillada + traducida (skill `validador-traduccion-documentos`)
- Comprobante de ingresos o solvencia económica
- Comprobante domicilio en México
- Fotos
- Pago de derechos

## Output

```json
{
  "tipo_tramite": "residencia_temporal_inicial",
  "via": "canje_visitante_a_temporal",
  "documentos_requeridos": [...],
  "documentos_presentados": [...],
  "completitud_pct": 85,
  "costo_total_estimado_mxn": "5500",
  "donde_acudir": "Oficina INM más cercana — cita previa",
  "tiempo_estimado_resolucion": "30-90 días",
  "vigencia_validada": false
}
```
