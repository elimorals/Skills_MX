# salon-mx

Plugin para salones de belleza, estéticas, spas y barberías en México.

## Casos de uso

- **Salones de barrio** (1-3 estilistas): agenda + cobros + no-show recovery
- **Salones premium** (4-15 estilistas): comisiones distintas, paquetes membresía, loyalty
- **Spas con servicios**: facial, masaje, depilación + paquetes recurrentes
- **Barberías**: cortes + barba + servicios add-on
- **Cadenas locales** (3-10 sucursales): consolidación de KPIs

## Skills propios (5)

| Skill | Cuándo activa |
|---|---|
| `agenda-citas-salon` | Crear, modificar, cancelar citas; manejo no-shows; walk-ins |
| `servicios-tarifario` | Catálogo de servicios + variantes + add-ons |
| `comisiones-estilistas` | Cálculo de comisiones (fijas, escalonadas, mixtas) |
| `paquetes-membresia` | Diseño de paquetes (3 facial, mensualidad spa, etc.) |
| `retencion-clientes-loyalty` | Programa de puntos, descuentos por visita N |

Heredados de core-mexico: cfdi-emision, iva-retenciones-mx, rfc-validacion, whatsapp-business-mx, compliance-lfpdppp, mxn-formato.

## Comandos

```
/salon:agendar-cita
/salon:cierre-dia-salon
/salon:recordatorio-no-show
/salon:calcular-comisiones
```

## Estado

⚠ Scaffolding (v0.1.0) — lint-passing pero no validado con salonero real.

## Ver también

- `core-mexico/` para CFDI y WhatsApp
- `docs/roadmap.md` Q2 2027
