---
name: dashboard-portfolio-p2p
description: Status del portafolio de crowdfunding/P2P de un inversionista - capital prestado vigente, intereses cobrados y por cobrar, ISR retenido por la IFC, cartera en mora por buckets de atraso, diversificación por plataforma, tipo de operación e industria, y uso de los límites de inversión por solicitud (Art. 49 CNBV). Usar cuando el usuario diga dashboard portfolio p2p, dashboard_portfolio_p2p, cómo va mi crowdfunding, mora en mis préstamos P2P, diversificación crowdfunding, ayuda con dashboard portfolio p2p.
allowed-tools: Read, Write
---

# Dashboard portafolio P2P

## Bloques

1. **Capital vigente** por plataforma (verificar que cada una esté autorizada: skill `catalogo-ifc-autorizadas`).
2. **Intereses**: cobrados en el año (nominales), ISR retenido por la IFC (20%, ver `fiscal-rendimientos-p2p`), por cobrar.
3. **Mora**: al corriente, 1-30, 31-90, > 90 días, castigado; tasa de mora = saldo con atraso > 30 días ÷ saldo total.
4. **Concentración**: % por plataforma, por solicitante e industria; alerta si un solo solicitante > 5% del portafolio.
5. **Límites CNBV**: uso del máximo por solicitud en cada IFC (skill `compliance-tope-100k-pf`).

Los datos vienen de los estados de cuenta o exportaciones que el usuario aporte; no hay MCP de plataformas P2P en el repo.

## Output esperado

```json
{
  "operation": "dashboard-portfolio-p2p",
  "data": {
    "fecha_corte": "2026-09-30",
    "capital_vigente_mxn": "200000.00",
    "intereses_cobrados_ytd_mxn": "15600.00",
    "isr_retenido_ytd_mxn": "3120.00",
    "mora_mayor_30_dias_mxn": "9000.00",
    "tasa_mora_30": 0.045,
    "plataformas": 3,
    "max_concentracion_solicitante": 0.03,
    "alertas": []
  },
  "vigencia_validada": false
}
```

Comprobación: 15,600 × 20% = 3,120; 9,000 ÷ 200,000 = 4.5%.

## Casos edge

- Plataforma no autorizada: excluir del cálculo de límites y alertar.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (mxn-formato); skills `catalogo-ifc-autorizadas`, `fiscal-rendimientos-p2p`, `compliance-tope-100k-pf`

No es asesoría de inversión.
