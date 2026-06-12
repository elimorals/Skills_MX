# mp_imss_patronal — MCP para IMSS IDSE

Operaciones de patronal contra IMSS Desde su Empresa.

⚠ Path Playwright real NO implementado. Auth requiere e.firma o NPIE.

## Tools (7)

| Tool | Propósito |
|---|---|
| `imss_consultar_avisos_pendientes` | Notificaciones requerimientos |
| `imss_enviar_movimiento_afiliatorio` | Alta, baja, mod SBC, reingreso |
| `imss_descargar_cedula_autodeterminacion` | Cédula bimestral |
| `imss_consultar_emcr` | Emisión Mensual Cédula Reposicionada |
| `imss_consultar_sbc` | Salario Diario Integrado |
| `imss_consultar_padron_trabajadores` | Listado trabajadores activos |
| `imss_listar_catalogos` | Tipos movimiento, causas baja, riesgo |

## Casos de uso

- Audit nómina mensual: cédula vs lo pagado en banco
- Alta nueva contratación → trigger CFDI tipo N nómina
- Verificar SBC en boletines anuales
- Baja con causa correcta para evitar conflictos LFT

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_imss_patronal/tests/ -q
```
