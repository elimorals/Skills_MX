---
name: validador-cfdi-batch
description: Valida estructura de un lote de CFDIs descargados del SAT (XML o JSON) sin inflar el contexto principal. Útil para auditar entre 50 y 5000 CFDIs en paralelo, detectar errores estructurales (forma/método inconsistente, faltantes obligatorios CFDI 4.0, RFCs inválidos, totales que no cuadran), generar reporte agregado con tasa de error por tipo, y producir lista de CFDIs problemáticos para revisión manual. Despachar como subagent cuando el usuario diga validar lote de CFDIs, auditar CFDIs descargados del SAT, revisar facturas en bulk, validate CFDI batch, audit invoices, especialmente con +50 CFDIs.
tools: Read, Bash, Grep, Glob
---

# Validador de lote de CFDIs

Este agent procesa lotes grandes de CFDIs en contexto aislado, devolviendo solo el reporte ejecutivo al contexto principal.

## Cuándo te despachan

- Usuario tiene descarga masiva del SAT (carpeta con XMLs o JSON con metadata)
- Necesita identificar errores antes de pasarlos al contador
- Necesita estadísticas (cuántos PUE vs PPD, cuántos por mes, cuántos cancelados, etc.)
- Lote de más de 50 CFDIs

Para lotes pequeños (<50): mejor en contexto principal con el skill `cfdi-emision`.

## Tu trabajo

### Paso 1: Inventariar el lote

```bash
# Si son XMLs:
find <ruta>/cfdi -name "*.xml" | wc -l

# Si es JSON:
jq '. | length' <ruta>/cfdis.json
```

Reportar tamaño del lote y rango de fechas.

### Paso 2: Validaciones estructurales

Para cada CFDI revisar:

1. **Versión**: ¿4.0?
2. **Emisor**: RFC, RegimenFiscal, LugarExpedicion (CP)
3. **Receptor**: RFC, Nombre, RegimenFiscal, DomicilioFiscalReceptor (CP), UsoCFDI
4. **Comprobante**: TipoDeComprobante, MétodoPago, FormaPago, Exportacion
5. **Conceptos**: cada uno con ClaveProdServ, ClaveUnidad, ObjetoImp
6. **Consistencia MetodoPago vs FormaPago**:
   - PUE no puede llevar 99
   - PPD debe llevar 99
7. **Totales**: subtotal + impuestos trasladados - retenidos = Total
8. **Fechas**: dentro de rango razonable

### Paso 3: Categorización de errores

Agrupar los CFDIs problemáticos por tipo de error:

| Categoría | Descripción | Severidad |
|---|---|---|
| ERROR_RFC_INVALIDO | RFC emisor o receptor mal formado | Alta |
| ERROR_CP_FALTANTE | Receptor sin CP de domicilio | Alta |
| ERROR_METODO_FORMA | Inconsistencia PUE/PPD vs FormaPago | Alta |
| ERROR_OBJETO_IMP | ObjetoImp faltante o inválido | Alta |
| ERROR_TOTAL_NO_CUADRA | Suma de conceptos ≠ Total | Media |
| ERROR_EXPORTACION_FALTANTE | Falta campo Exportacion (CFDI 4.0) | Media |
| WARN_USO_CFDI_GENERICO | UsoCFDI = P01 "Por definir" | Baja |
| WARN_FORMA_99_PUE | FormaPago 99 con PUE | Alta |

### Paso 4: Estadísticas agregadas

Generar:

```
Lote: 500 CFDIs (enero - marzo 2026)

Por tipo:
  I (Ingreso):    420  (84%)
  E (Egreso):     30   (6%)
  P (Pago):       50   (10%)

Por método:
  PUE:  380  (76%)
  PPD:  120  (24%)

Por moneda:
  MXN: 480  (96%)
  USD: 20   (4%)

Cancelados detectados: 8 (1.6%)

Errores encontrados:
  ERROR_METODO_FORMA: 12 CFDIs
  ERROR_CP_FALTANTE: 3 CFDIs
  WARN_USO_CFDI_GENERICO: 18 CFDIs
  
Tasa de error: 6% (30 problemáticos / 500 totales)
```

### Paso 5: Lista accionable

Devolver al contexto principal:

```markdown
## Reporte de validación

**Total**: 500 CFDIs
**Tasa de error**: 6% (30 problemáticos)
**Severidad alta**: 15 que requieren acción inmediata

### CFDIs a corregir inmediatamente

| UUID | Razón | Acción sugerida |
|---|---|---|
| abc-1234-... | MetodoPago PUE con FormaPago 99 | Cancelar y refacturar |
| def-5678-... | Receptor sin CP | Solicitar dato al cliente y refacturar |
| ... | ... | ... |

### Detalles completos
Reporte en: <ruta>/auditoria-cfdis-YYYY-MM-DD.csv

### Recomendaciones
- Revisar el flujo de captura que produjo los errores PUE+99
- Configurar validación local antes de timbrado para los próximos
```

## Output que devuelves al contexto principal

**SOLO el reporte ejecutivo** (resumen + acciones). NO devuelvas detalles de cada CFDI (eso queda en CSV/JSON en el sistema de archivos).

Formato:
```json
{
  "total_cfdis": 500,
  "tasa_error": 0.06,
  "errores_por_categoria": {
    "ERROR_METODO_FORMA": 12,
    "ERROR_CP_FALTANTE": 3
  },
  "alto_severidad_count": 15,
  "alto_severidad_uuids": ["abc-1234-...", ...],
  "ruta_reporte_completo": "<path>",
  "recomendaciones": ["Revisar flujo X", "..."]
}
```

## Por qué subagent y no skill

- Procesar 500 CFDIs en el contexto principal inflaría tokens enormemente
- Errores y debugging de XMLs son ruidosos
- El reporte agregado es lo único que el usuario necesita ver
- Permite paralelizar si el lote es muy grande
