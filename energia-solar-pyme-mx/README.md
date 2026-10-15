# energia-solar-pyme-mx

Plugin para PyMEs con paneles solares interconectados a CFE. Cubre lectura factura CFE bidireccional (consumo + inyección), cálculo crédito kWh acumulado, validación contra errores facturación, ROI del sistema, calendario tarifa GDMTH. Score 7.5/10.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install energia-solar-pyme-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `lectura-factura-cfe-pdf`
2. `validacion-factura-cfe`
3. `credito-kwh-tracking`
4. `roi-solar-payback`
5. `optimizacion-tarifa-gdmth`

## Comandos

- `/energia:lectura`
- `/energia:validacion`
- `/energia:credito`
- `/energia:roi`
