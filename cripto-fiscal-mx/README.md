# cripto-fiscal-mx

Plugin para PF mexicanas que operan criptomonedas.

> Spec: `docs/specs/09-vertical-cripto-fiscal-mx.md`
> **CARF (OCDE) vigente desde 2026** — TODO exchange con clientes MX reportará al SAT

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install cripto-fiscal-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `dashboard-cripto-portafolio`
2. `importar-operaciones-exchange` (Bitso CSV, Binance, Coinbase, etc.)
3. `calcular-costo-base-fifo`
4. `calculadora-isr-cripto-detallada` (permutas, staking, NFTs)
5. `riesgo-carf-2026`

## Reglas SAT 2026

- Permuta cripto-cripto = gravable (Art. 119 LISR enajenación)
- Staking/airdrops = ingreso al valor de mercado
- NFTs = enajenación de bienes
- CARF: > $200k MXN en Bitso ya se reporta al SAT
