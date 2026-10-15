# tramites-vehiculares-mx

Plugin para gestión integral de obligaciones vehiculares en México (40M+ vehículos).

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install tramites-vehiculares-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Cubre

- 🚓 Multas: detección automática por placa via `mp_cdmx_municipal`, `mp_edomex_municipal`, `mp_monterrey_municipal`
- 🌫️ Verificación vehicular: calendario semestral CDMX/EdoMex/otros
- 💰 Refrendo y tenencia: alertas + cálculo por estado
- 📋 Placas y tarjeta de circulación: trámites comunes

## Comandos

- `/vehiculos:dashboard` — status integral por placa
- `/vehiculos:multas` — detectar y pagar
- `/vehiculos:verificar` — calendario + status verificación
- `/vehiculos:refrendo` — refrendo + tenencia del año

## Diferencia vs `talleres-mx`

- `talleres-mx`: para el dueño del taller
- `tramites-vehiculares-mx`: para el dueño del vehículo

## Score research: 9.0/10
