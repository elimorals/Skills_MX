# agencia-marketing-mx

Plugin para agencias de marketing digital (1-25 personas) operando en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install agencia-marketing-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills propios

| Skill | Propósito |
|---|---|
| `reporte-mensual-cliente` | Reporte ejecutivo con KPIs por canal, insights, próximos pasos |
| `meta-ads-optimization` | Análisis de fatiga creativa, audiencias saturadas, redistribución de presupuesto |
| `copy-mexicano` | Copy optimizado para audiencia mexicana, evita "español neutro" |
| `community-management-mx` | Respuestas a comentarios/DMs con tono de marca, escalación de quejas |
| `briefing-creativo` | Brief estructurado para diseño/copy/producción |

## Skills heredados de `core-mexico`

6 skills compartidos (CFDI, IVA, RFC, WhatsApp Business, LFPDPPP, MXN).

## Commands

- `/agencia:reporte [cliente] [mes]`
- `/agencia:auditoria-cuenta [cliente]`
- `/agencia:copy [tipo-contenido] [contexto]`
- `/agencia:brief [proyecto]`

## Usuario objetivo

- Account manager con 5-20 cuentas activas
- Dueño de agencia que factura $200k - $2M MXN/mes
- Freelancer senior pivotando a agencia

## Filosofía

Liberar **30+ horas/semana** del trabajo administrativo del AM. El AM debe estar en estrategia con el cliente, no armando reportes en Looker Studio.

## Estado

`v0.1.0` — scaffolding inicial, listo para dogfooding.
