---
name: regularizacion-migratoria
description: Guía para extranjeros en situación migratoria irregular (FMM vencido, residencia expirada, entrada sin documentos). Cubre programa de regularización del INM, multas aplicables, plazos, requisitos por situación. NO sustituye asesoría legal especializada. Usar cuando el usuario diga sin papeles, irregular mexico, FMM vencido, regularizar migratoria.
allowed-tools: Read, Write
---

# Regularización migratoria

## Situaciones comunes

| Situación | Acción posible |
|---|---|
| FMM vencido 1-180 días | Pago multa + salida del país |
| FMM vencido > 180 días | Multa + posible regularización in situ |
| Residencia temporal vencida | Re-tramitar con multa |
| Entró sin papeles (frontera) | Trámite especial |
| Hijo mexicano | Acceso facilitado a residencia permanente |
| Matrimonio mexicano | Cambio de condición acelerado |

## Costos típicos multa

- $5,400 MXN base
- Aumenta con tiempo irregular

## Output

```json
{
  "situacion": "FMM_vencido_45_dias",
  "opciones": [
    "Salir del país y reentrar (más fácil)",
    "Regularizar in situ (más caro, 60-90d)"
  ],
  "costo_multa_estimado_mxn": "5400",
  "tiempo_resolucion": "60-90 días si regulariza in situ",
  "recomendacion": "Consultar abogado especializado antes de actuar",
  "vigencia_validada": false
}
```

## ⚠ Compliance

- Recomendar siempre consultar abogado migratorio
- No tomar acciones que empeoren la situación
- Algunos casos requieren amparo
