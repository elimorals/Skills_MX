# donatarias-ongs-mx

Plugin para donatarias autorizadas (Art. 79 LISR). Cubre CFDI D04 a donantes, declaración anual transparencia (31 mayo), reporte mensual donativos efectivo > $100k (LFPRH), renovación anual autorización SAT. Score 7.5/10. Mercado: ~9,500 donatarias.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install donatarias-ongs-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `dashboard-donataria-mes`
2. `cfdi-donativo-d04`
3. `reporte-mensual-efectivo-100k`
4. `declaracion-anual-transparencia`
5. `renovacion-autorizacion-anual`

## Comandos

- `/donatarias:dashboard`
- `/donatarias:cfdi`
- `/donatarias:reporte`
- `/donatarias:declaracion`
