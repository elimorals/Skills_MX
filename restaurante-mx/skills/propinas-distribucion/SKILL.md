---
name: propinas-distribucion
description: Distribución de propinas en restaurantes mexicanos siguiendo Art. 346 LFT (propinas son del trabajador, no patrón) y leyes estatales. Modelos: 100% al mesero (default LFT), pool con cocina y bar (Tip Pool), proporción por horas trabajadas. Implicaciones fiscales (ingreso del trabajador, no acumulable al restaurante). Cálculo justo por turno con bitácora trazable. Usar cuando el usuario diga propinas, distribución meseros, tip pool, propinas cocina, fiscalmente propinas. NO usar para inventario (otro skill) ni menú (otro skill).
allowed-tools: Read, Write, Edit
---

# Propinas — distribución en MX

## Marco legal MX

### Art. 346 LFT (Ley Federal del Trabajo)
> "Las propinas son parte del salario de los trabajadores a quienes corresponden... No podrán ser objeto de compensación, descuento o reducción."

**Implicaciones**:
- Propinas son del **trabajador**, NO del restaurante
- El restaurante NO puede retenerlas para "gastos generales"
- Cada trabajador debe recibir su parte completa
- NO se descuentan errores del trabajador (rotura, falta caja) — eso va aparte

### CFDI y propinas
- Las propinas NO son ingreso del restaurante (Art. 8 LISR — no es ingreso para PM)
- El cliente puede ver "propina sugerida" pero NO se debe forzar
- El restaurante puede actuar como intermediario/dispersador (sin retener nada)
- El trabajador declara sus propinas como ingreso por sueldos (Art. 110 LISR)

### Restricciones
- NO se puede obligar a propina mínima (PROFECO)
- Propinas voluntarias se pueden sugerir en cuenta (8-15% típico MX)
- NO se permite "tip pool" SIN consentimiento de todos los trabajadores

## Modelos de distribución

### Modelo 1: 100% al mesero (default LFT puro)

Mesero recibe TODA la propina del cliente que atendió.

**Pros**:
- Cumple Art. 346 LFT directamente
- Simple administrativamente
- Mesero altamente incentivado al servicio

**Contras**:
- Cocina, bar, lavaloza NO reciben nada
- Genera resentimiento del backend
- Meseros experimentados acaparan mejores mesas

### Modelo 2: Tip Pool (pool compartido)

Todas las propinas se juntan + se distribuyen por porcentajes:
- Meseros: 70%
- Cocina + ayudantes: 20%
- Bar (si hay): 10%

Distribución por horas trabajadas, no por mesa.

**Pros**:
- Más justo entre equipos
- Reduce rotación de cocina
- Coloboración meseros-cocina mejora

**Contras**:
- Requiere consentimiento del 100% del staff (LFT)
- Más complejo administrativamente
- Algunos meseros pierden incentivo

### Modelo 3: Híbrido (mesero 70-80% + pool 20-30%)

- Mesero conserva 70-80% de SU propina
- 20-30% va a pool para repartir entre cocina/bar/lavaloza

Es el más común en MX 2024+.

### Modelo 4: Por turno y posición

Cada turno tiene "tickets" por horas trabajadas:
- Mesero: 4 tickets/hora
- Cocinero: 2 tickets/hora
- Lavaloza: 1.5 tickets/hora

Total propinas / total tickets = valor por ticket
Cada trabajador recibe su número de tickets × valor.

## Cálculo de ejemplo (Modelo 3 híbrido)

**Día**: Sábado noche
**Total propinas**: $8,500 MXN (en pesos físicos + tarjeta)

### Por mesero (70-80% conservan su propina)
- Mesero Juan: $2,500 propinas (atendió 25 mesas) → conserva $2,000 + aporta $500 al pool
- Mesera Ana: $3,200 propinas → conserva $2,560 + aporta $640
- Mesero Luis: $2,800 propinas → conserva $2,240 + aporta $560

**Total al pool**: $500 + $640 + $560 = $1,700 MXN

### Pool a backend (distribución por horas)

Personal backend de la noche:
- Chef ejecutivo: 8 hrs → 8 tickets × 3 (multiplicador chef) = 24 tickets
- Cocinero 1: 8 hrs × 2 = 16 tickets
- Cocinero 2: 6 hrs × 2 = 12 tickets
- Lavaloza: 8 hrs × 1 = 8 tickets
- Barman: 7 hrs × 2 = 14 tickets

Total tickets: 74

Valor por ticket: $1,700 / 74 = $22.97

Distribución:
- Chef ejecutivo: 24 × $22.97 = $551.28
- Cocinero 1: 16 × $22.97 = $367.52
- Cocinero 2: 12 × $22.97 = $275.64
- Lavaloza: 8 × $22.97 = $183.76
- Barman: 14 × $22.97 = $321.58

**Total: $1,699.78** (queda diferencia mínima)

## Propinas vía pago electrónico

Cuando cliente paga con TDC/TDD:
- Tip va a la cuenta del restaurante junto con el pago
- Restaurante DEBE transferir al trabajador (Art. 346 LFT)
- Buena práctica: **dispersión semanal** (no esperar al fin de mes)

⚠ Algunos restaurantes "filtran" 8-15% de propinas TDC alegando "comisión bancaria del 5% sobre el cargo total". Esto es:
- Legalmente cuestionable (la comisión bancaria es del restaurante, no del trabajador)
- Frecuentemente denunciado en PROFECO
- Mejor práctica: **transferir 100% íntegro**

## Bitácora obligatoria

Cada distribución debe registrarse con:
```
- Fecha y turno
- Total propinas recolectadas
- Modelo aplicado (1-4)
- Distribución por trabajador con monto + horas
- Firma o acuse digital del trabajador
- Conservar por 5 años (Art. 27 CFF)
```

## Implicaciones fiscales para el trabajador

Las propinas SÍ son ingreso:
- Acumulan al salario para ISR Art. 96 LISR
- Para IMSS, propinas se acumulan al SBC para cálculo de cuotas
- El restaurante DEBE reportar propinas en CFDI nómina (concepto 049 "Propinas")

⚠ Si el restaurante NO reporta propinas en nómina, eso es:
- Evasión por parte del trabajador (en teoría debería declararlas)
- Riesgo del restaurante en auditoria SAT
- Beneficio "informal" pero arriesgado

## Output estructurado

```json
{
  "distribucion_propinas": {
    "fecha": "2026-03-15",
    "turno": "noche",
    "total_propinas_mxn": 8500.00,
    "modelo_aplicado": "hibrido_mesero_70_pool_30",
    "consentimiento_documentado": true,
    "distribucion_meseros": [
      {
        "trabajador": "Juan M.",
        "propinas_recolectadas": 2500.00,
        "porcentaje_conservado": 0.80,
        "conservado_mxn": 2000.00,
        "aportado_al_pool_mxn": 500.00,
        "recibido_pool_mxn": 0,
        "total_final_mxn": 2000.00
      }
    ],
    "distribucion_backend": [
      {
        "trabajador": "Chef Carlos",
        "puesto": "chef_ejecutivo",
        "horas_trabajadas": 8,
        "multiplicador_puesto": 3,
        "tickets": 24,
        "valor_ticket_mxn": 22.97,
        "recibido_mxn": 551.28
      }
    ],
    "alerta_cumplimiento_lft": null
  }
}
```

## Validación pendiente

- Casos PROFECO sobre tip pool sin consentimiento
- Jurisprudencia LFT sobre propinas en CDMX 2024-2026
- Mejores prácticas de software para tracking propinas
- Reportes fiscales obligatorios en CFDI nómina (versión vigente)
