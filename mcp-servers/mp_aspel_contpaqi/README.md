# mp_aspel_contpaqi — MCP para Aspel COI / ContPAQi

Integración contable con los dos ERPs más usados en México:
- **Aspel COI** (SQL Server local)
- **ContPAQi** (.NET COM, solo Windows)

## Reto técnico

Ninguno de los dos ERPs ofrece API REST pública. La integración requiere uno de:
1. **Exports CSV** generados por el ERP (recomendado — soportado aquí)
2. Conexión ODBC al SQL Server de Aspel (requiere agente local)
3. API ADD .NET COM de ContPAQi (solo Windows + ContPAQi instalado)

Este MCP soporta el **camino 1** (parser de CSV) y mock-first cuando no hay exports disponibles.

## Tools (9)

| Tool | Propósito | Mock |
|---|---|---|
| `aspel_listar_polizas` | Pólizas del periodo + filtro por tipo | Sí |
| `aspel_get_poliza` | Detalle por número de póliza | Sí |
| `aspel_obtener_balanza` | Balanza de comprobación | Sí |
| `aspel_obtener_catalogo_cuentas` | Plan de cuentas con código SAT | Sí |
| `aspel_obtener_estado_resultados` | P&L calculado | Sí |
| `aspel_obtener_balance_general` | Balance General | Sí |
| `aspel_parsear_export_csv` | Parser inline (sin red) | Local |
| `aspel_obtener_instrucciones_configuracion` | Pasos para configurar Aspel/ContPAQi | Local |
| `aspel_listar_catalogos` | Tipos póliza, código SAT, conceptos | Local |

## Configuración

| Variable | Propósito |
|---|---|
| `ASPEL_EXPORTS_DIR` | Directorio con CSVs exportados (ej. `~/exports`) |
| `CONTPAQI_AGENT_URL` | (Futuro) URL del agente local que expone API ContPAQi |
| `PLUGINS_MX_MOCK=1` | Forzar mock |

Sin variables → modo mock con datos demo plausibles.

## Convención de archivos de export

Cuando `ASPEL_EXPORTS_DIR` está configurado, este MCP busca:

```
$ASPEL_EXPORTS_DIR/
├── polizas_YYYYMM.csv       # un archivo por periodo
├── balanza_YYYYMM.csv
└── catalogo_cuentas.csv     # un solo archivo, todo el catálogo
```

Formato CSV soportado (Aspel y ContPAQi exportan estructuras similares):

**polizas_*.csv**:
```csv
Numero,Fecha,Tipo,Concepto,Cuenta,Debe,Haber
D-001,2026-03-15,DIARIO,Renta oficina,601-001,30000.00,0.00
D-001,2026-03-15,DIARIO,Renta oficina,102-001,0.00,30000.00
```

**balanza_*.csv**:
```csv
Cuenta,Nombre,Saldo Inicial,Cargos,Abonos,Saldo Final
102-001,Bancos BBVA,350000.00,58000.00,34800.00,373200.00
```

**catalogo_cuentas.csv**:
```csv
Cuenta,Nombre,Codigo SAT,Naturaleza,Nivel
102-001,Bancos BBVA,102,DEUDORA,3
```

El parser tolera:
- Delimitadores: `,`, `;`, `\t`, `|` (auto-detecta)
- BOM UTF-8 al inicio
- Acentos en headers
- Columnas extra (se ignoran)
- Separador decimal con coma o punto

## Cómo configurar el ERP para exportar

Usa el tool `aspel_obtener_instrucciones_configuracion` con `erp="aspel_coi"` o `erp="contpaqi"` y recibirás los pasos exactos paso a paso.

Para automatizar (recomendado en producción):
- **Aspel**: macro de COI o script con `pyodbc` conectado al SQL Server
- **ContPAQi**: app .NET usando la API ADD COM

## Casos de uso típicos

### 1. Auditor fiscal mensual
```python
balanza = aspel_obtener_balanza(ejercicio=2026, mes=3)
estado = aspel_obtener_estado_resultados(ejercicio=2026, mes=3)
# → Detecta utilidad/pérdida sin tocar el ERP en vivo
```

### 2. Cruce CFDI vs póliza
```python
polizas = aspel_listar_polizas(ejercicio=2026, mes=3, tipo="INGRESOS")
# Cruzar contra CFDIs emitidos del mes (mp_facturama_extendido o mp_sat_portal)
# Detecta CFDIs sin asiento contable o asientos sin CFDI
```

### 3. Verificación ecuación contable
```python
balance = aspel_obtener_balance_general(ejercicio=2026, mes=3)
assert balance["ecuacion_contable_cuadra"] is True
```

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_aspel_contpaqi/tests/ -q
```
