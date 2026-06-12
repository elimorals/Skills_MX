---
name: workflow-validacion-cfdis-historico
description: Workflow batch reactivo que revisa todos los CFDIs históricos de un período (ej. último año) y valida: UUIDs aún vigentes en SAT, RFCs emisores no en 69-B definitivo, montos coinciden con captura, no hay duplicados. Útil pre-auditoría SAT o cuando se compra un negocio (due diligence histórico). Usar cuando el usuario diga validar cfdis historico, revisar cfdis año, auditoria pre-sat.
allowed-tools: Read, Write
---

# Workflow validación CFDIs histórico

## Fases

### 1. Cargar CFDIs del período
- `mp_sat_portal.sat_descargar_cfdi_masivo` (emitidos + recibidos)
- Parsear XMLs

### 2. Validar UUID c/u
- `mp_sat_portal.verificar_cfdi_uuid` (consulta pública SAT)
- Si cancelado: registrar
- Si vigente: continuar

### 3. Validar RFC emisor recibidos
- Contra `mp_sat_portal.consultar_69b_efos`
- Si en lista definitiva: marca EXCLUIR + alerta CRÍTICA

### 4. Detectar duplicados
- Mismo UUID 2 veces: error de captura
- Mismo emisor + monto exacto + fecha cercana: probable duplicado

### 5. Conciliar totales
- Sumar CFDIs por mes
- Comparar contra declaración mensual presentada
- Si diferencia > 1%: alerta

### 6. Reporte

```json
{
  "ejercicio": 2025,
  "cfdis_revisados": 245,
  "vigentes": 240,
  "cancelados": 5,
  "rfc_69b_definitivo_detectados": 2,
  "duplicados_potenciales": 1,
  "discrepancias_vs_declaracion_mensual": [],
  "recomendaciones": [
    "Excluir 2 CFDIs con emisor 69-B en próxima complementaria",
    "Revisar 1 duplicado potencial — ajustar si confirmado"
  ]
}
```
