---
name: verificacion-vehicular
description: Calcula el periodo de verificación vehicular 2026 por color de engomado / terminación de placa en la Megalópolis (CDMX, EdoMex y estados de la CAMe), el costo 2026 (CDMX $765.45, EdoMex desde $469.24) y la multa por verificar tarde, y explica qué implica cada holograma (00, 0, 1, 2, exento) en el Hoy No Circula. El estatus real de la verificación en CDMX tiene CAPTCHA y se entrega al usuario. Usar cuando el usuario diga cuándo verifico mi auto, verificación pendiente, calendario de verificación, engomado, holograma, verificentro, multa por verificar tarde. NO usar para vehículos de carga pesada (otra normativa) ni para planear la semana con Hoy No Circula (optimizador-horarios-hoy-no-circula).
allowed-tools: Read, Write
---

# Verificación vehicular — calendario y estatus (2026)

## Calendario 2026 (Megalópolis)

Fuente: calendario SEDEMA CDMX 2026 (Gaceta Oficial 2-ene-2026, vía prensa) en `mcp-servers/shared/verificacion_vehicular.py`. Dos meses por semestre:

| Engomado | Terminación | 1er semestre | 2º semestre |
|---|---|---|---|
| Amarillo | 5, 6 | ene–feb | jul–ago |
| Rosa | 7, 8 | feb–mar | ago–sep |
| Rojo | 3, 4 | mar–abr | sep–oct |
| Verde | 1, 2 | abr–may | oct–nov |
| Azul | 9, 0 | may–jun | nov–dic |

Placas con letra al final: se toma el último **dígito** de la placa. Si no hay dígito, pide el color del engomado.

No hay periodo de gracia: verificar fuera de los dos meses es extemporáneo y genera multa.

## Costos 2026

| Estado | Costo | Multa extemporánea | Fuente |
|---|---|---|---|
| CDMX | $765.45 (5.625 UMA + IVA; igual para todos los hologramas) | 20 UMA = $2,346.20 | El Universal, cálculo con UMA $117.31 |
| EdoMex | $469.24 (hologramas 1 y 2); 0 ≈ $610; 00 ≈ $1,196 | 30 UMA = $3,519.30 | UnoTV 2026 |
| Hidalgo, Morelos, Puebla, Tlaxcala | sin fuente 2026 | verificar | — |
| Jalisco | programa propio; el calendario de engomados no aplica | verificar | — |

Cálculo CDMX: 5.625 × $117.31 = $659.87; + IVA 16% = $765.45.

## Hologramas

| Holograma | Para quién (resumen) | Hoy No Circula |
|---|---|---|
| 00 | Vehículos nuevos (exención inicial; el plazo lo fija el programa vigente) | Circula diario |
| 0 | Cumple los límites de emisión más estrictos | Circula diario |
| 1 | Cumple límites intermedios | No circula 1 día entre semana + 2 sábados al mes (impares: 1º y 3º; pares: 2º y 4º) |
| 2 | Resto que aprueba | No circula 1 día entre semana + todos los sábados |
| Exento | Eléctricos e híbridos con constancia | Circula diario; no verifica |

Las reglas finas para obtener 0 o 00 (año modelo, tecnología) cambian con el programa semestral: confírmalas en SEDEMA o en el portal del estado.

## Flujo

1. Pide placa (o terminación), estado de registro y último holograma.
2. `verificacion_proximo_periodo(placa, estado)` (`mp_verificacion_vehicular_mx`) da color y meses; es cálculo local con el calendario de arriba.
3. Para saber si ya verificó: `verificacion_consultar_estatus(placa, estado)`. En CDMX devuelve `requiere_humano: true` (CAPTCHA del portal SAF): entrega `url` y `pasos` del handoff y pide al usuario el resultado.
4. Costo: `verificacion_listar_programas`. Si `costo_mxn` es `null`, di que no hay monto 2026 verificado.
5. Cita: CDMX en verificentros autorizados SEDEMA; EdoMex en `citaverificacion.edomex.gob.mx`.

## Ejemplo

Placa CDMX terminación 1, consulta 14-oct-2026 → engomado verde → periodo oct–nov 2026. Costo $765.45. Si no verifica antes del 30-nov-2026: multa de $2,346.20 más la verificación.

## Output

```json
{
  "placa_hash": "...",
  "entidad": "cdmx",
  "engomado": "verde",
  "ultimo_holograma": "1",
  "proxima_verificacion": {"periodo": "octubre-noviembre 2026", "fecha_inicio": "2026-10-01", "fecha_fin": "2026-11-30"},
  "costo_mxn": "765.45",
  "multa_extemporanea_mxn": "2346.20",
  "estatus_real": "requiere_humano",
  "portal_consulta": "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Eléctrico / híbrido | Exento; tramitar constancia de exención |
| Placa de estado fuera de la Megalópolis | Su programa estatal; no apliques este calendario |
| Cambio de estado de registro | Verificar con el calendario del nuevo estado |
| Verificación vencida | Multa + verificar cuanto antes; con multa pendiente puede bloquearse el trámite |
| Contingencia ambiental | Restricciones extra; ver optimizador-horarios-hoy-no-circula |

## Advertencias

- Calendario y costos 2026 vienen de prensa que cita a SEDEMA y a la Secretaría del Medio Ambiente del EdoMex (confianza media). Confirmar en el portal oficial antes de ir al verificentro.
- La skill no consulta el estatus por sí sola ni reemplaza el portal oficial.
