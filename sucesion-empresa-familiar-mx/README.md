# sucesion-empresa-familiar-mx

Plugin para familias mexicanas con patrimonio significativo: diagnóstico patrimonial, simulador donación vs herencia vs trust, cálculo ISR donaciones por relación familiar (cónyuges + ascendientes/descendientes EXENTOS), plan testamentario, protocolo familiar. Score 7.5/10. Mercado: ~500k familias.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install sucesion-empresa-familiar-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `diagnostico-patrimonial-familiar`
2. `simulador-donacion-vs-herencia`
3. `calculo-isr-donaciones`
4. `plan-testamentario-distribucion`
5. `protocolo-familiar-template`

## Comandos

- `/sucesion:diagnostico`
- `/sucesion:simulador`
- `/sucesion:calculo`
- `/sucesion:plan`
