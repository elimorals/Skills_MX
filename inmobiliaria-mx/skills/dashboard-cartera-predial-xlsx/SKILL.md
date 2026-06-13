---
name: dashboard-cartera-predial-xlsx
description: Genera dashboard XLSX consolidado con la cartera predial de N propiedades en distintos municipios. Toma lista de cuentas catastrales → invoca workflow cartera-predial-multi-municipio → produce XLSX listo para Excel/Sheets con: adeudo por propiedad, días vencido, recargos, descuentos pronto pago, ranking de prioridad. Para arrendadores, despachos contables, inmobiliarias y administradores de propiedades. Usar cuando el usuario diga "cartera predial", "dashboard predial", "predial múltiples propiedades", "reporte predial Excel", "lista propiedades", "adeudos predial cartera", "predial portfolio", "consolidado predial".
allowed-tools: Read, Write, Bash
---

# Dashboard XLSX cartera predial multi-municipio

## Para quién es

| Perfil | Caso de uso típico |
|---|---|
| **Arrendador residencial** | 5-20 inmuebles en distintos municipios → ver cuáles tienen adeudo + cuándo aplicar pronto pago |
| **Despacho contable** | 50+ clientes con propiedades → consolidar para asesoría |
| **Inmobiliaria/property manager** | 100+ inmuebles administrados → priorizar pagos para no afectar rentas |
| **Due diligence pre-compra** | Validar adeudos antes de cerrar transacción inmobiliaria |
| **Constructora con reserva territorial** | Lotes en varios municipios → reporte trimestral |

## Inputs requeridos

El usuario debe proveer una lista de propiedades en formato JSON o CSV. Formato mínimo:

```json
[
  {"id": "casa-coyoacan", "estado": "cdmx", "municipio": "ciudad_de_mexico", "cuenta_predial": "022123456789", "alias": "Casa Coyoacán"},
  {"id": "depa-zapopan", "estado": "jal", "municipio": "guadalajara", "cuenta_predial": "U-12345678", "alias": "Depa Chapultepec"},
  {"id": "rancho-mich", "estado": "mich", "municipio": "ciudad_hidalgo", "cuenta_predial": "123456", "tipo": "rustico", "alias": "Rancho Tio Pepe"}
]
```

Campos:
- `id` (req): identificador interno
- `estado` (req): clave 2-5 letras (ver `shared/catalogo_municipios_mx.py`)
- `municipio` (req): clave del catálogo
- `cuenta_predial` (req): clave catastral municipal
- `tipo` (opcional): "urbano" | "rustico" (requerido solo para SACPI Michoacán)
- `direccion` (opcional): requerido para Mérida (busca por dirección)
- `alias` (opcional): nombre amigable
- `monto_renta_mensual` (opcional): para análisis de impacto

## Flujo del skill

1. **Leer input**: JSON/CSV con N propiedades
2. **Validar contra catálogo**: cuáles tienen MCP soportado, cuáles no
3. **Invocar workflow** `cartera-predial-multi-municipio.workflow.js` con la lista
4. **Recibir resultado consolidado**: adeudos + alertas + recomendaciones
5. **Generar XLSX** con hojas:
   - `Resumen` — totales + KPIs
   - `Cartera completa` — una fila por propiedad
   - `Acción urgente` — top 10 a pagar primero
   - `Pendientes humano` — Puebla CAPTCHA con URLs pre-llenadas
   - `No soportados` — propiedades que requieren consulta manual

## Estructura del XLSX generado

### Hoja "Resumen"
| Métrica | Valor |
|---|---|
| Propiedades totales | N |
| Propiedades consultadas OK | N - X |
| Propiedades con adeudo | M |
| **Adeudo total cartera** | **$XXX,XXX MXN** |
| Descuento pronto pago disponible | $X,XXX MXN |
| Ahorro neto si pagas en enero | $X,XXX MXN |
| Propiedades pendientes humano (Puebla) | K |

### Hoja "Cartera completa"
Columnas:
- `id` | `alias` | `estado` | `municipio` | `cuenta_predial`
- `adeudo_total_mxn` | `bimestres_pendientes` | `dias_vencido`
- `recargo_estimado_mxn` | `descuento_pronto_pago_mxn`
- `alerta` (critico/advertencia/ok) | `url_pago_directo`

Formato condicional:
- Filas con `alerta=critico` → fondo rojo
- Filas con `alerta=advertencia` → fondo amarillo
- Filas `ok` → fondo verde claro

### Hoja "Acción urgente"
Top 10 priorizado por:
1. Días vencido descendente
2. Monto descendente
3. Disponibilidad de descuento por pronto pago

Cada fila incluye **link directo al portal** para pago.

## Implementación

```python
import json
from pathlib import Path

def generar_dashboard_xlsx(propiedades: list[dict], cliente_rfc: str | None = None) -> str:
    """
    1. Invoca el workflow cartera-predial-multi-municipio
    2. Toma el JSON resultado + CSV generado
    3. Genera XLSX con openpyxl o xlsxwriter

    Returns: path al XLSX generado
    """
    # 1. Invocar workflow (asume runtime Workflow disponible)
    resultado_workflow = invoke_workflow(
        "inmobiliaria-mx/workflows/cartera-predial-multi-municipio.workflow.js",
        args={
            "cliente_rfc": cliente_rfc,
            "propiedades": propiedades,
            "incluir_recomendaciones": True,
        }
    )

    # 2. Leer CSV generado por el workflow
    csv_path = resultado_workflow["artefactos"]["csv"]
    import csv as csv_mod
    with open(csv_path) as f:
        cartera_rows = list(csv_mod.DictReader(f))

    # 3. Generar XLSX
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()

    # Hoja 1: Resumen
    ws_resumen = wb.active
    ws_resumen.title = "Resumen"
    ws_resumen["A1"] = "Métrica"
    ws_resumen["B1"] = "Valor"
    ws_resumen["A1"].font = Font(bold=True)
    ws_resumen["B1"].font = Font(bold=True)

    metricas = [
        ("Propiedades totales", resultado_workflow["propiedades_total"]),
        ("Consultadas OK", resultado_workflow["propiedades_consultadas_ok"]),
        ("Pendientes humano (Puebla)", resultado_workflow["propiedades_pendientes_humano"]),
        ("No soportadas", resultado_workflow["propiedades_no_soportadas"]),
        ("Adeudo total cartera (MXN)", resultado_workflow["adeudo_total_cartera_mxn"]),
        ("Ahorro potencial pronto pago (MXN)", resultado_workflow["ahorro_potencial_pronto_pago_mxn"]),
    ]
    for i, (m, v) in enumerate(metricas, start=2):
        ws_resumen[f"A{i}"] = m
        ws_resumen[f"B{i}"] = v

    # Hoja 2: Cartera completa
    ws_cartera = wb.create_sheet("Cartera completa")
    if cartera_rows:
        headers = list(cartera_rows[0].keys())
        for col, h in enumerate(headers, start=1):
            ws_cartera.cell(row=1, column=col, value=h).font = Font(bold=True)
        for row_idx, row_data in enumerate(cartera_rows, start=2):
            for col, h in enumerate(headers, start=1):
                ws_cartera.cell(row=row_idx, column=col, value=row_data.get(h))
            # Formato condicional por alerta
            alerta = row_data.get("alerta", "")
            fill = None
            if alerta == "critico":
                fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
            elif alerta == "advertencia":
                fill = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")
            elif alerta == "ok":
                fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
            if fill:
                for col in range(1, len(headers) + 1):
                    ws_cartera.cell(row=row_idx, column=col).fill = fill

    # Hoja 3: Acción urgente (top 10 por adeudo)
    ws_urgente = wb.create_sheet("Acción urgente")
    criticos = sorted(
        [r for r in cartera_rows if r.get("alerta") == "critico"],
        key=lambda r: float(r.get("adeudo_total_mxn", 0) or 0),
        reverse=True,
    )[:10]
    if criticos:
        headers = ["id", "alias", "estado", "municipio", "adeudo_total_mxn",
                   "dias_vencido", "url_pago"]
        for col, h in enumerate(headers, start=1):
            ws_urgente.cell(row=1, column=col, value=h).font = Font(bold=True)
        for row_idx, r in enumerate(criticos, start=2):
            for col, h in enumerate(headers, start=1):
                ws_urgente.cell(row=row_idx, column=col, value=r.get(h))

    # Ajustar anchos
    for ws in [ws_resumen, ws_cartera, ws_urgente]:
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            max_len = max(
                (len(str(c.value)) if c.value else 0)
                for c in ws[col_letter]
            )
            ws.column_dimensions[col_letter].width = min(max_len + 2, 50)

    out_path = f"cartera-predial/{cliente_rfc or 'cliente'}/dashboard-{Path(csv_path).stem}.xlsx"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return out_path
```

## Casos edge

| Caso | Manejo |
|---|---|
| Propiedad sin URL en catálogo | Aparece en hoja "No soportados" con instrucciones de consulta manual |
| Propiedad con Mérida + sin dirección | Pide al usuario completar campo `direccion` antes de procesar |
| Propiedad con Puebla (CAPTCHA) | Aparece en hoja "Pendientes humano" con URL pre-llenada |
| Cuenta predial inválida (< 5 chars) | Pre-validación rechaza con mensaje claro |
| Workflow timeout (> 5 min consulta) | Reintenta 1 vez, luego marca como "consulta_timeout" |
| Adeudo > $1M | Flag adicional "auditoría_recomendada" — montos altos requieren validación contador |

## Output esperado

Tras invocar:
- `cartera-predial/{cliente}/{fecha}.xlsx` (típicamente 50-500KB)
- Si `enviar_alerta_whatsapp=true`: notificación al cliente con resumen ejecutivo

## Producto vendible

Este skill cierra un caso de negocio claro para PYMEs:
- **Arrendador con 5 propiedades**: paga $0 — usa el plugin como cliente individual
- **Despacho contable con 50 clientes × 3 propiedades**: $500-1,500 MXN/mes por automatizar lo que toma 8h/bimestre manual
- **Inmobiliaria con cartera de 100 inmuebles**: $5,000+ MXN/mes — ROI evidente

Mercado MX: ~50,000 inmobiliarias + ~10,000 despachos contables + ~3M arrendadores residenciales.

## Cuándo NO usar este skill

- **1 sola propiedad**: usar directamente el MCP municipal o `/inmobiliaria:predial-individual`.
- **Sin cuentas catastrales del cliente**: este skill asume input estructurado. Si solo tienes direcciones, primero corre skill `identificar-cuenta-predial-por-direccion`.
- **Cobranza activa de inquilinos morosos**: usar `cobranza-renta-mensual.workflow.js` que es complementario pero distinto.
