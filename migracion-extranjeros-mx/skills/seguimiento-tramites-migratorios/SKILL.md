---
name: seguimiento-tramites-migratorios
description: Seguimiento del estatus de un trámite migratorio en proceso ante el INM. El usuario consulta el portal oficial con su número de trámite (NUT) y contraseña; la skill interpreta la etapa (recibido, en estudio, prevención/requerimiento, resuelto, entrega de tarjeta), estima tiempos, lista documentos pendientes y propone qué hacer si se atrasa o si lo niegan (recurso de revisión o juicio de nulidad). Usar cuando el usuario diga estatus trámite INM, dónde va mi residencia, en qué va mi visa, me pidieron documentos INM, me negaron la residencia.
allowed-tools: Read, Write
---

# Seguimiento de trámite migratorio

No hay MCP para el portal del INM. Pide al usuario que consulte el estatus en el portal del INM con su NUT y contraseña y que pegue el resultado o una captura; la skill lo interpreta.

## Estados

Los nombres exactos varían en el portal; los tiempos son típicos, no legales.

| Estado | Descripción | Acción |
|---|---|---|
| Recibido | El INM recibió la solicitud | Esperar; guardar acuse y NUT |
| En estudio | Revisión de documentos | Esperar; tiempos varían por oficina |
| Prevención / requerimiento | Piden documentos o aclaraciones | ⚠ Responder dentro del plazo del oficio (verificar en el propio oficio; si no se cumple, el trámite se desecha) |
| Resuelto positivo | Autorizado | Acudir a toma de huellas y entrega de tarjeta según la cita |
| Resuelto negativo | Negado | Recurso de revisión ante el INM (15 días hábiles, Art. 85 LFPA) o juicio de nulidad ante el TFJA; consultar abogado |

Mientras el trámite está en curso, el comprobante (acuse) acredita que hay solicitud en proceso. Para viajar fuera de México durante el trámite se necesita permiso de salida y regreso ($591.06, Art. 13 fr. II LFD 2026).

## Output

```json
{
  "tramite_id": "NUT-...",
  "tipo": "residencia_temporal_canje",
  "fecha_solicitud": "2026-03-15",
  "estado_actual": "en_estudio",
  "dias_en_estado_actual": 65,
  "documentos_pendientes": [],
  "recomendacion": "Sin requerimiento: esperar. Si pasan más de 90 días sin movimiento, acudir a la oficina con el acuse o pedir orientación a un abogado.",
  "vigencia_validada": false
}
```

> Los tiempos de resolución no tienen una cifra oficial única: no prometas fechas.
