---
name: detector-consumo-anomalo-cfe-agua
description: Detecta consumo anómalo en recibos de servicios públicos (CFE electricidad, Conagua/operadores municipales agua, Naturgy gas) comparando contra histórico del mismo domicilio en últimos 12-24 meses para identificar saltos inexplicables (CFE +30% sin razón sugiere fuga eléctrica o lectura mal o robo de luz; agua +50% sugiere fuga interna típicamente en tinaco o tubería oculta; gas +40% sugiere fuga peligrosa o calefactor con problema). Diferencia entre variaciones estacionales esperadas (verano CFE sube por refrigerador y AC, invierno gas sube por calefacción) y anomalías reales. Detecta también tarifa CFE mal aplicada (DAC vs doméstico — la DAC es 50-100% más cara, cae cuando consumes > kWh categoría). Genera alerta accionable con causa probable + qué revisar primero (medidor, instalación, electrodomésticos). Cubre histórico OCR'eado de recibos PDF/papel + portales digitales (CFE Recibo Digital, operadores agua municipales que tengan). Usar cuando el usuario diga "consumo anómalo", "recibo CFE alto", "fuga agua", "tarifa DAC", "recibo gas raro". NO usar para cálculo de tarifas predial ni para pago de servicios.
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
1. Cambio a tarifa DAC (si > 250 kWh/mes)
2. Refrigerador con problema (revisar empaques + termostato)
3. Aire acondicionado uso excesivo o falla

Acción recomendada:
1. Revisar consumos individuales por electrodoméstico (smart plugs)
2. Si no encuentra causa: solicitar verificación del medidor a CFE
3. Si confirma DAC: ajustar consumo para regresar a doméstica
```

## Detección de tarifa DAC mal aplicada

CFE pone en DAC cuando consumes > X kWh (varía por región tarifaria 1A, 1B, etc.).

Si detectamos consumo en DAC pero el inmueble es residencial:
- Revisar si hubo aumento real o lectura errónea
- Calcular ahorro potencial al volver a doméstica
- Si fue error CFE: gestionar reembolso
