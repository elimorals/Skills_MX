---
name: optimizador-horarios-hoy-no-circula
description: Planea la semana del vehículo bajo el programa Hoy No Circula (16 alcaldías de CDMX y municipios conurbados del Estado de México, 5:00 a 22:00 h). Calcula qué día entre semana y qué sábados no circula según holograma y color de engomado / terminación de placa, y avisa de restricciones extra por contingencia ambiental. Usar cuando el usuario diga hoy no circula, no circula mi auto, qué día no circulo, sábado no circula, calendario de restricción, contingencia ambiental, doble hoy no circula.
allowed-tools: Read, Write
---

# Optimizador Hoy No Circula

## Reglas (programa permanente, 5:00–22:00 h)

Día entre semana por engomado (hologramas 1 y 2):

| Engomado | Terminación | No circula |
|---|---|---|
| Amarillo | 5, 6 | Lunes |
| Rosa | 7, 8 | Martes |
| Rojo | 3, 4 | Miércoles |
| Verde | 1, 2 | Jueves |
| Azul | 9, 0 | Viernes |

Sábados:

| Holograma | Sábados que no circula |
|---|---|
| 00, 0, exento | Ninguno |
| 1, terminación impar (1, 3, 5, 7, 9) | 1º y 3º sábado del mes |
| 1, terminación par (0, 2, 4, 6, 8) | 2º y 4º sábado del mes |
| 2 | Todos los sábados |
| 5º sábado del mes | Solo holograma 2 (y foráneos sin holograma); holograma 1 circula |

Multa por circular en día restringido: 20 a 30 UMA según la entidad ($2,346.20 a $3,519.30 con UMA 2026 $117.31), más posible remisión al corralón.

Fuentes: SEDEMA / CAMe vía prensa 2026 (UnoTV, Excélsior, Xataka; confianza media). Hay notas con discrepancias en el detalle de los sábados: ante duda, confirma el sábado concreto en `sedema.cdmx.gob.mx` o la cuenta oficial de la CAMe.

## Contingencia ambiental

Fase 1 o 2 se declara el mismo día (CAMe). Se suma una restricción por holograma y engomado que cambia en cada comunicado. No la deduzcas: pide al usuario el comunicado del día o remite a la CAMe. Los vehículos exentos (eléctricos, híbridos con constancia) circulan.

## Flujo

1. Pide holograma, terminación de placa y, si se planea una fecha, la semana.
2. `cdmx_consultar_hoy_no_circula` (`mp_cdmx_municipal`) hace el cálculo local; si no está disponible, aplica las tablas de arriba.
3. Cuenta los sábados del mes en el calendario real (1º sábado = primer sábado del mes).

## Ejemplo

Holograma 1, terminación 4 (rojo, par), semana del 19 al 25 de octubre de 2026. Los sábados de octubre son 3, 10, 17, 24 y 31; el 24 es el 4º.

```
Lun 19: circula
Mar 20: circula
Mié 21: NO CIRCULA (engomado rojo)
Jue 22: circula
Vie 23: circula
Sáb 24: NO CIRCULA (4º sábado, terminación par)
Dom 25: circula

Sáb 31 (5º sábado): circula (solo restringe holograma 2)
```

## Advertencias

- Fuera de CDMX y los municipios conurbados del EdoMex el programa no aplica.
- El programa y la lista de municipios pueden cambiar; confirma antes de planear viajes.
