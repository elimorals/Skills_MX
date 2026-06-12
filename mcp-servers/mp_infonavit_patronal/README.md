# mp_infonavit_patronal — MCP para Portal Empresarial INFONAVIT

⚠ Path Playwright real NO implementado todavía. Mock-first.

## Tools (5)

| Tool | Propósito |
|---|---|
| `infonavit_consultar_creditos_trabajadores` | Lista créditos vigentes por patrón |
| `infonavit_descargar_emis` | Emisión Mensual (total + detalle por trabajador) |
| `infonavit_consultar_descuentos_mensuales` | Detalle por NSS específico |
| `infonavit_consultar_avisos_pendientes` | Altas/bajas/requerimientos |
| `infonavit_listar_catalogos` | Tipos descuento, status crédito, productos |

## Casos de uso

- Cálculo nómina mensual: descuentos automáticos por crédito
- Reconciliación EMIS pagada vs lo cobrado en banco
- Alta de nuevo crédito de trabajador → ajustar nómina
- Audit anual: verificar todos los descuentos del año

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_infonavit_patronal/tests/ -q
```
