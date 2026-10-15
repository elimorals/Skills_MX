# notarias-mx

Plugin para notarías y oficinas notariales en México.

> Score research: **8.0/10**. Patrón adaptado de `freelancers-mx` (servicio profesional con honorarios).

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install notarias-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Servicios cubiertos

- Compraventa de inmuebles
- Testamentos
- Poderes
- Constitución de sociedades
- Sucesiones intestadas
- Hipotecas
- Donaciones

## Skills

1. `agenda-citas-notariales`
2. `registro-escrituras-tipos`
3. `calculo-isabi-por-estado` (varía 2-6% por estado)
4. `honorarios-notariales-arancel` (tabla oficial por estado)
5. `dashboard-notaria-mes`
