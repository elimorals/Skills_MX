# inmobiliaria-mx

Plugin para corredores inmobiliarios, brokers e inmobiliarias en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install inmobiliaria-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Casos de uso

- **Corredor independiente** (1-5 inmuebles/mes): screening + contratos + comisiones
- **Agencia inmobiliaria** (5-20 inmuebles/mes): comparables + ficha + comisión team
- **Property management**: contratos renta + cobranza + mantenimiento
- **Especialista en venta**: análisis de mercado + pricing + comisión venta

## Skills propios (5)

| Skill | Cuándo activa |
|---|---|
| `contrato-arrendamiento-mx` | Contrato CCF / CCDF con cláusulas vigentes |
| `screening-inquilinos` | Buró + ingresos + referencias |
| `comparables-zona` | Estadísticas precio por zona + tipo |
| `ficha-inmueble` | Datos catastrales + amenidades + estado |
| `comisiones-corredor` | Cálculo comisión venta (3-7%) / renta (1 mes) |

## Comandos

```
/inm:contrato-renta
/inm:screen-inquilino
/inm:comparables-zona
/inm:comisiones-mes
```

## Estado

⚠ Scaffolding (v0.1.0). Contratos requieren revisión legal antes de uso real.
