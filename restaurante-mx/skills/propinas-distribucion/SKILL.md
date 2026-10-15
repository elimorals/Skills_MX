---
name: propinas-distribucion
description: Distribución de propinas en restaurantes mexicanos siguiendo Arts. 346-347 LFT (las propinas son salario del trabajador; el patrón no puede participar en ellas). Modelos: 100% al mesero (default LFT), pool con cocina y bar (Tip Pool), proporción por horas trabajadas. Implicaciones fiscales y de IMSS (ingreso por salarios del trabajador, CFDI de nómina). Cálculo justo por turno con bitácora trazable. Usar cuando el usuario diga propinas, distribución meseros, tip pool, propinas cocina, fiscalmente propinas, propina con tarjeta, reparto de propinas, propinas nómina. NO usar para inventario (otro skill) ni menú (otro skill).
allowed-tools: Read, Write, Edit
---

# Propinas — distribución en MX

## Marco legal MX (verificado contra LFT, última reforma DOF 14-05-2026)

### Arts. 346 y 347 LFT (capítulo de trabajadores en hoteles, restaurantes, bares)
> Art. 346: "Las propinas son parte del salario de los trabajadores a que se refiere este capítulo en los términos del artículo 347. Los patrones no podrán reservarse ni tener participación alguna en ellas."

> Art. 347: si no se fija la propina como porcentaje sobre consumos, las partes fijan el aumento al salario base para el pago de indemnizaciones y prestaciones.

**Implicaciones**:
- Las propinas son del **trabajador**: el restaurante NO puede quedarse con ninguna parte (ni para "gastos generales" ni para cubrir la comisión bancaria)
- NO se descuentan errores del trabajador (rotura, faltante de caja) — eso va aparte y con los límites del Art. 110 LFT
- Las propinas cuentan como salario para indemnizaciones y prestaciones (Art. 347)

**Reforma en trámite (no vigente)**: la Cámara de Diputados aprobó en 2025 una reforma a los Arts. 90, 346, 347 y otros (salario base no menor al mínimo que no se sustituye con propinas; reparto equitativo). Al 2026-10-15 el texto vigente del Art. 346 sigue siendo el citado arriba; **verificar** en el DOF si ya se publicó antes de aplicarla (confianza media, fuente: Gaceta Parlamentaria y prensa 2025).

### Propinas y facturación del restaurante
- Si el restaurante entrega la propina íntegra al trabajador, es un cobro **por cuenta de terceros**: no se trata como ingreso propio del restaurante (criterio usual; documentar la dispersión). Si se la queda, además de violar el Art. 346 LFT, se vuelve ingreso acumulable
- La propina es voluntaria: puede sugerirse en la cuenta pero no cobrarse sin consentimiento del cliente (criterio PROFECO)
- Para el trabajador es ingreso por salarios (Art. 94 LISR); si se paga vía nómina, el patrón retiene ISR conforme al Art. 96 LISR

### Restricciones
- NO se puede obligar a propina mínima (PROFECO)
- Propinas voluntarias se pueden sugerir en cuenta (10-15% es lo usual en MX)
- Tip pool: la LFT no lo regula expresamente; como el patrón "no puede tener participación", el reparto debe pactarse con los trabajadores (por escrito, idealmente en contrato colectivo o reglamento interior) y el patrón no decide unilateralmente quién recibe qué. Recomendación práctica: consentimiento firmado de todo el personal que aporta

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
- Colaboración meseros-cocina mejora

**Contras**:
- Requiere pacto documentado con el personal (ver Restricciones)
- Más complejo administrativamente
- Algunos meseros pierden incentivo

### Modelo 3: Híbrido (mesero 70-80% + pool 20-30%)

- Mesero conserva 70-80% de SU propina
- 20-30% va a pool para repartir entre cocina/bar/lavaloza

Es un esquema frecuente (no hay estadística oficial de prevalencia).

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
- Contrario al Art. 346 LFT (el patrón no puede tener participación en la propina; la comisión bancaria es gasto del restaurante)
- Reclamable ante la autoridad laboral (Centro de Conciliación / Inspección del Trabajo)
- Mejor práctica: **transferir 100% íntegro**

## Fuente de datos

Si el restaurante usa Soft Restaurant y está configurado el MCP `mp_softrestaurant`, `softrest_meseros_ventas` y `softrest_corte_z` devuelven propinas por mesero y por método de pago. Ese MCP lee **exports CSV** (`SOFT_RESTAURANT_EXPORTS_DIR`) o los parsea con `softrest_parsear_export`; no es una API en vivo. Sin exports configurados devuelve datos simulados (marcados `simulated`): no los uses para pagar; pide al usuario el CSV del corte.

## Bitácora (recomendada)

Cada distribución debe registrarse con:
```
- Fecha y turno
- Total propinas recolectadas
- Modelo aplicado (1-4)
- Distribución por trabajador con monto + horas
- Firma o acuse digital del trabajador
- Conservar al menos 5 años (Art. 30 CFF, como parte de la contabilidad)
```

## Implicaciones fiscales y de seguridad social

- **ISR**: las propinas son ingreso por salarios del trabajador (Art. 94 LISR). Si se dispersan vía nómina, el patrón las suma a la base de retención (Art. 96 LISR)
- **CFDI de nómina**: el catálogo `c_TipoPercepcion` no tiene clave específica de propinas; en la práctica se usa `038` "Otros ingresos por salarios". Desde el complemento de nómina 1.2 rev. 2026 la clave 038 debe ir **totalmente gravada** (importe exento = 0). Confianza media (fuentes: KPMG Flash SAT dic-2025, IDC 08-12-2025); **verificar** el catálogo vigente del SAT antes de timbrar
- **IMSS (SBC)**: el Art. 27 LSS integra al SBC "cualquier otra cantidad o prestación que se entregue al trabajador por su trabajo". Que las propinas pagadas por clientes integren o no el SBC es un **criterio discutido** (más defendible que integren cuando el patrón las recibe y dispersa, p. ej. propina con tarjeta). **Verificar con el contador/abogado laboral** antes de definir la política; no lo resuelvas por tu cuenta
- Para indemnizaciones y prestaciones laborales, la propina sí cuenta como salario (Arts. 346-347 LFT)

⚠ Si el restaurante NO registra las propinas que dispersa:
- Riesgo de diferencias en auditoría SAT/IMSS (depósitos con tarjeta mayores a ventas facturadas)
- Riesgo laboral (indemnizaciones calculadas sin propinas)

> Validación profesional: la integración de propinas a nómina/IMSS tiene consecuencias fiscales y laborales. Confirma la política con un contador y un abogado laboral.

## Output estructurado

```json
{
  "distribucion_propinas": {
    "fecha": "2026-03-15",
    "turno": "noche",
    "total_propinas_mxn": 8500.00,
    "modelo_aplicado": "hibrido_mesero_80_pool_20",
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
- Clave `c_TipoPercepcion` vigente para propinas (038 vs claves nuevas 054/055)
- Estatus en Senado/DOF de la reforma LFT de propinas aprobada por Diputados en 2025
