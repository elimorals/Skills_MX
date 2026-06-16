# mp_imss_continuidad

Adapter Plugins MX → **licitación IMSS Continuidad Operativa Sistemas Sustantivos** (mayo 2026).

**Comprador**: IMSS directo o integradora primaria.
**Vehículo**: Subcontrato MIPYME bajo integradora ganadora.

## 8 sistemas sustantivos IMSS con RTO/RPO

| Sistema | Criticidad | RTO | RPO |
|---|---|---|---|
| IDSE | muy_alta | 4h | 1h |
| SUA | muy_alta | 4h | 1h |
| EMCR | muy_alta | 6h | 2h |
| Incapacidades Digitales | muy_alta | 4h | 1h |
| Semanas Cotizadas | alta | 8h | 4h |
| Asignación NSS | alta | 8h | 4h |
| Cita Pensión | alta | 12h | 8h |
| Alfresco | alta | 12h | 4h |

## Tools

- `imss_continuidad_listar_sistemas()` — 8 sistemas con RTO/RPO
- `imss_continuidad_health_check(clave)` — verde/amarillo/rojo + latencia
- `imss_continuidad_plan(clave)` — DR/BCP con NMX-COPANT-ISO 22301
- `imss_continuidad_reporte_ejecutivo(periodo)` — formato compatible licitación

## Diferenciador

Cero overlap con `mp_imss_patronal` (afiliación, SBC, EMCR) — esto es la capa **encima**, SRE/continuidad.
