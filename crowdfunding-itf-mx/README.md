# crowdfunding-itf-mx

Plugin para participantes en plataformas IFC (Instituciones Financiamiento Colectivo) reguladas por Ley Fintech. Cubre 3 perfiles: emprendedor solicitante, inversor P2P, operador IFC. Comparador plataformas, fiscal rendimientos, tope $100k PF, compliance CNBV. Score 7.5/10.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install crowdfunding-itf-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `dashboard-portfolio-p2p`
2. `simulador-costo-financiamiento-cf`
3. `catalogo-ifc-autorizadas`
4. `fiscal-rendimientos-p2p`
5. `compliance-tope-100k-pf`

## Comandos

- `/crowdfunding:dashboard`
- `/crowdfunding:simulador`
- `/crowdfunding:catalogo`
- `/crowdfunding:fiscal`
