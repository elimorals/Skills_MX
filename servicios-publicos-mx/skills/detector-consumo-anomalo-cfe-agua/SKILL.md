---
name: detector-consumo-anomalo-cfe-agua
description: Detecta consumo anómalo en recibos de luz (CFE), agua (organismo operador municipal) y gas natural comparando contra el histórico del mismo domicilio (12-24 meses). Separa la variación estacional (verano sube la luz, invierno el gas) de saltos reales (CFE +30%, agua +50%, gas +40%) y da la causa probable y qué revisar primero (medidor, fugas, electrodomésticos). Detecta también la reclasificación a tarifa DAC (promedio de 12 meses arriba del límite de la tarifa) y sus causas. Trabaja con recibos PDF, fotos o datos de portales. Usar cuando el usuario diga "consumo anómalo", "recibo CFE alto", "me llegó muy cara la luz", "fuga de agua", "tarifa DAC", "recibo de gas raro". NO usar para predial ni para pagar servicios.
allowed-tools: Read, Write, Edit
---

# Detector de consumo anómalo en servicios públicos

## Histórico requerido

```yaml
domicilio_id: ABC...
servicios:
  cfe:
    medidor: 12345678
    tarifa: doméstica  # o DAC
    historial_bimestral:
      - periodo: 2024-01
        kwh: 320
        monto: 850
      - periodo: 2024-03
        kwh: 380
        monto: 1020
      # ... mínimo 12 meses
  agua:
    cuenta: ...
    historial_mensual: [...]
  gas:
    cuenta: ...
    historial_mensual: [...]
```

## Algoritmo de detección

### Para CFE (bimestral)

```python
def es_anomalo_cfe(consumo_actual, historico_12m):
    mismo_mes_anio_pasado = filtrar(historico_12m, mismo_periodo)
    promedio_anual = mean(historico_12m)
    
    if consumo_actual > 1.30 * mismo_mes_anio_pasado:
        return ALERTA_ALTA
    if consumo_actual > 1.50 * promedio_anual:
        return ALERTA_ALTA
    return NORMAL
```

### Para agua (mensual)

```python
def es_anomalo_agua(consumo_actual, historico_12m):
    if consumo_actual > 1.50 * mismo_mes_anio_pasado:
        return ALERTA_CRITICA  # posible fuga
```

### Para gas (mensual)

```python
def es_anomalo_gas(consumo_actual, historico_12m):
    if consumo_actual > 1.40 * mismo_mes_anio_pasado:
        return ALERTA_PELIGRO_SEGURIDAD  # fuga = peligro
```

## Causas probables por tipo de anomalía

### CFE +30%

1. Refrigerador descompuesto (consume excesivo)
2. Aire acondicionado nuevo o más uso
3. Aumento de electrodomésticos
4. Posible robo de luz
5. Medidor con problema
6. Cambio a tarifa DAC sin querer

### Agua +50%

1. Fuga en tinaco (boya descompuesta — flota muerta)
2. Fuga en tubería oculta (humedad en paredes)
3. Fuga en inodoro (suena agua)
4. Riego excesivo
5. Llenado de alberca

### Gas +40%

1. **Fuga peligrosa** — verificar olor inmediato
2. Calefactor mal regulado
3. Mayor consumo cocina o agua caliente

## Output alerta

```
🚨 CONSUMO ANÓMALO DETECTADO

Servicio: CFE
Periodo: nov-dic 2025
Consumo: 580 kWh
Periodo equivalente anterior: 350 kWh
Aumento: +66%

Causas probables:
1. Reclasificación a DAC (en tarifa 1, si el promedio mensual de los últimos 12 meses pasa de 250 kWh)
2. Refrigerador con problema (revisar empaques + termostato)
3. Aire acondicionado uso excesivo o falla

Acción recomendada:
1. Revisar consumos individuales por electrodoméstico (smart plugs)
2. Si no encuentra causa: solicitar verificación del medidor a CFE
3. Si confirma DAC: bajar el consumo; CFE regresa a la tarifa doméstica cuando el promedio de 12 meses queda debajo del límite (puede tardar hasta un año)
```

## Detección de tarifa DAC mal aplicada

CFE reclasifica a DAC (Doméstica de Alto Consumo, sin subsidio) cuando el **promedio mensual de los últimos 12 meses** supera el límite de la tarifa:

| Tarifa | 1 | 1A | 1B | 1C | 1D | 1E | 1F |
|---|---|---|---|---|---|---|---|
| Límite kWh/mes | 250 | 300 | 400 | 850 | 1,000 | 2,000 | 2,500 |

Fuente: prensa 2025-2026 que cita a CFE (confianza media); la tarifa aplicable viene impresa en el recibo. Un solo bimestre alto no basta: calcula el promedio con los últimos 6 recibos bimestrales (suma de kWh / 12).

Si detectamos consumo en DAC pero el inmueble es residencial:
- Revisar si hubo aumento real o lectura errónea
- Calcular ahorro potencial al volver a doméstica
- Si fue error de CFE (lectura estimada o mal tomada): pedir revisión en el centro de atención y, si no se resuelve, queja ante PROFECO
