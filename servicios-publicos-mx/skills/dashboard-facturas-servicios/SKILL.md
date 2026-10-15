---
name: dashboard-facturas-servicios
description: Dashboard consolidado de facturas de servicios públicos del mes (CFE + agua + predial + gas). Muestra montos por servicio, vencimientos próximos, tendencias de consumo vs históricos. Usar cuando el usuario diga dashboard servicios, facturas servicios publicos, consumo del mes.
allowed-tools: Read, Write
---

# Dashboard servicios públicos

## Output

```
💡 SERVICIOS PÚBLICOS — Junio 2026

🔌 CFE:           $4,250  vence 2026-06-18 (en 6 días)
💧 Agua:          $   850  vence 2026-06-25
🏠 Predial:        Pagado anual 2026 — al corriente
🔥 Gas natural:    $   620  vence 2026-06-15 (3 días) ⚠

📊 vs mes pasado:
  CFE:   +18% (alerta — revisar consumo)
  Agua:  -5%
  Gas:    estable

⚠ Próximos a vencer:
  • Gas — 3 días — pagar hoy
  • CFE — 6 días
```

## Fuentes de datos

- Recibos que el usuario comparte (PDF, foto o XML): fuente principal.
- `mp_cfe_facturacion` (`cfe_descargar_factura_mes`, `cfe_consumo_historico`): sin verificar; el portal de CFE pide CAPTCHA y sesión, así que puede requerir al usuario.
- `mp_agua_mx.agua_consultar_adeudo`: real solo para algunos organismos (JMAS Juárez); el resto devuelve `requiere_humano` → entrega URL y pasos.
- `mp_gas_natural_mx.gas_consultar_recibo`: confirmar disponibilidad por distribuidor.

Si un monto no viene de un recibo o de una consulta real, márcalo "pendiente", no lo estimes.
