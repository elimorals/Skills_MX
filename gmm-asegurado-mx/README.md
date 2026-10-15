# gmm-asegurado-mx

Plugin para asegurados GMM (Gastos Médicos Mayores) en México.

> Score: **7.5/10**. ~7M asegurados.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install gmm-asegurado-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `dashboard-poliza-gmm` — vigencia + suma asegurada + usos
2. `calculo-deducible-coaseguro` — qué pagas tú vs lo que paga aseguradora
3. `autorizacion-medica-pre-evento` — para procedimientos > $10k
4. `comparador-aseguradoras-gmm` — al renovar o cambiar
5. `renovacion-poliza-anual`

## Aseguradoras principales MX

GNP, AXA, MetLife, MAPFRE, Banorte, Inbursa, Allianz, BBVA Bancomer, Plan Seguro.
