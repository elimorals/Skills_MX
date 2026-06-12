# mp_buro_credito_personal — MCP para Buró de Crédito

## 🚨 ADVERTENCIA LEGAL

Consultar el Buró de Crédito de **OTRA persona sin autorización formal** constituye **DELITO**:
- Multa $50,000 - $5,000,000 MXN
- Responsabilidad penal por violación de datos personales
- Marco legal: Art. 32 LFPDPPP + Art. 28 LRSIC

**Cada tool exige `autorizacion_token` (mínimo 16 chars) que debe provenir de:**
1. Firma digital del titular (e.firma, Mifiel)
2. Click-wrap agreement con timestamp + IP + RFC
3. Carta firmada digitalizada con OCR validado

Sin este token, las tools fallan automáticamente con `BuroAutorizacionError`.

## Tools (4)

| Tool | Auth | Mock | Compliance |
|---|---|---|---|
| `buro_consultar_score` | Token autorización | Sí | RFC + token se hashean en bitácora |
| `buro_descargar_reporte_completo` | Token autorización | Sí | Hash de todo |
| `buro_monitorear_alertas` | Token autorización | Sí | Hash de todo |
| `buro_listar_catalogos` | — | Local | Incluye marco legal completo |

## Casos de uso legítimos

- **Autoconsulta del usuario** (siempre autorizado por sí mismo)
- **Pre-aprobación de crédito** con click-wrap timestamped
- **Inquilino** con autorización firmada en contrato
- **Score periódico** para finanzas personales propias

## Casos PROHIBIDOS

- Consultar buró de un familiar sin su autorización
- Consultar buró de un empleado sin autorización formal
- Vender datos del reporte a terceros
- Compartir el reporte sin autorización
- Persistir el reporte en logs/CRM sin política de retención clara

## Compliance integrada

- RFC se hashea (SHA-256 trunca) antes de escribir bitácora
- Token de autorización se hashea (nunca en claro)
- Bitácora `audit-log/buro_credito_mcp/YYYY-MM.jsonl` con timestamp + operación
- Cada tool registra fecha de consulta + hash del token (auditoría legal)

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_buro_credito_personal/tests/ -q
```
