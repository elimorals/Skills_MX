# servicios-publicos-mx

Plugin para gestión integral de servicios públicos en México.

> Score: **7.8/10**.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install servicios-publicos-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Cubre

- 🔌 CFE (eléctrico)
- 💧 Agua (organismo municipal/estatal)
- 🏠 Predial municipal
- 🔥 Gas natural / LP
- 🌊 Drenaje (en algunos municipios)

## Skills

1. `dashboard-facturas-servicios`
2. `alertas-vencimientos-pagos`
3. `detector-anomalias-consumo` — fugas, sobrecargos
4. `programacion-pagos-batch` — pagar todo del mes
5. `cfdi-servicios-deducible` — gastos deducibles PyME
