# despacho-contable-mx

Plugin para contadores y despachos contables con N clientes.

> Score research: **7.9/10**. Extensión multi-tenant de `freelancers-mx`.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install despacho-contable-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Diferencia clave

- `freelancers-mx`: contador es **el cliente** del plugin (su propia fiscal)
- `despacho-contable-mx`: contador gestiona **N clientes** distintos

## Skills

1. `gestion-clientes-multi-rfc` — directorio + datos por cliente
2. `calendario-fiscal-clientes` — fechas por cliente (multi-régimen)
3. `facturacion-recurrente-despacho` — el despacho factura a sus clientes
4. `comunicacion-clientes-batch` — WhatsApp/email masivo
5. `dashboard-despacho-mes`
