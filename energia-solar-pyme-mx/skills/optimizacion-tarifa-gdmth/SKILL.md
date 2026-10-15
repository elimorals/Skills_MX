---
name: optimizacion-tarifa-gdmth
description: Sugiere cómo bajar el recibo de una PyME o industria en tarifa GDMTH (Gran Demanda en Media Tensión Horaria) moviendo consumo del periodo punta a base o intermedio, recortando la demanda máxima en punta, corrigiendo el factor de potencia y aprovechando la generación solar. Usa los horarios y precios impresos en el recibo de la región tarifaria; no los supone. Usar cuando el usuario diga optimizacion tarifa gdmth, bajar recibo GDMTH, horario punta CFE, cargo por demanda, demanda máxima, factor de potencia, mover consumo a horario base, tarifa horaria.
allowed-tools: Read, Write
---

# Optimización de tarifa GDMTH

## Cómo cobra GDMTH

- Energía por periodo horario: **base** (más barato), **intermedio** y **punta** (más caro).
- Cargo por **capacidad/demanda**, ligado a la demanda máxima medida en punta.
- Cargo por **factor de potencia** si es < 90%; bonificación si es > 90%.
- Cargos fijos y de transmisión/distribución.

Los horarios de cada periodo **cambian por región tarifaria y temporada** (y el sábado/domingo tienen otro esquema). Los precios cambian cada mes. No uses un "horario punta típico": toma los horarios y precios del recibo del cliente o de la publicación tarifaria de CFE para su región. Las tarifas finales del suministro básico las determina hoy la CNE (sustituyó a la CRE, LSE DOF 18-03-2025).

## Flujo

1. Extrae del recibo (con `lectura-factura-cfe-pdf`) kWh y demanda por periodo, precios por periodo, FP y región tarifaria.
2. Calcula el peso de cada bloque: `costo_punta = kwh_punta × precio_punta`, etc., y el cargo por demanda.
3. Identifica cargas desplazables (bombeo, compresores, hornos, carga de montacargas, refrigeración con inercia) y cuántos kWh pueden salir de punta.
4. Ahorro por desplazamiento = kWh movidos × (precio punta − precio del periodo destino).
5. Demanda: escalonar arranques de motores en punta; el ahorro se calcula con el cargo por kW del recibo.
6. FP < 90%: recomendar estudio y banco de capacitores; comparar costo contra el cargo mensual.
7. Solar: la generación cae en horas de sol; ver en el recibo si coincide con intermedio o punta en esa región antes de prometer ahorro en punta.

## Ejemplo (precios ilustrativos, reemplazar con los del recibo)

Recibo: punta 1,300 kWh a $3.10; base a $1.20. Se mueven 800 kWh de bombeo de punta a base.

- Ahorro energía = 800 × (3.10 − 1.20) = 800 × 1.90 = **$1,520/mes** antes de IVA.
- Si además la demanda en punta baja 15 kW y el cargo es $400/kW (ilustrativo): 15 × 400 = $6,000/mes.

## Output

```json
{
  "tarifa": "GDMTH",
  "region_tarifaria": "del recibo",
  "fuente_precios": "recibo 2026-09",
  "acciones": [
    {"accion": "Mover bombeo a periodo base", "kwh_mes": 800, "ahorro_mensual_mxn": 1520.00},
    {"accion": "Escalonar arranque de compresores en punta", "kw_reduccion": 15, "ahorro_mensual_mxn": "calcular con cargo por kW del recibo"},
    {"accion": "Banco de capacitores (FP 88.4%)", "ahorro_mensual_mxn": "cargo FP del recibo"}
  ],
  "advertencias": ["Horarios y precios cambian por región y mes"]
}
```

## Advertencias

- Recomendaciones de operación, no de ingeniería eléctrica: cambios en la instalación los valida un ingeniero electricista.
- Un cambio de tarifa (p. ej. GDMTH ↔ GDMTO) se tramita con CFE y depende de la demanda contratada; no lo prometas.
