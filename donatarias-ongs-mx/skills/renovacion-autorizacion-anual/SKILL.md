---
name: renovacion-autorizacion-anual
description: Da seguimiento a la vigencia de la autorización de una donataria para recibir donativos deducibles - la autorización es por ejercicio y se mantiene cumpliendo en tiempo la transparencia de mayo y demás requisitos del Art. 82 LISR; alerta 90 días antes de cada plazo y lista documentos; si fue revocada o no renovada, calcula los 12 meses para recuperarla y la obligación de transmitir el patrimonio. Usar cuando el usuario diga renovación autorización anual, renovacion_autorizacion_anual, vigencia autorización donataria, revocación de donataria, perdí la autorización, ayuda con renovación autorización anual.
allowed-tools: Read, Write
---

# Vigencia y renovación de la autorización

## Cómo funciona (verificar en RMF 2026, capítulo 3.10.1)

- La autorización se publica en el **Anexo 14 de la RMF** y en el directorio del SAT.
- Su vigencia es por **ejercicio fiscal**; se mantiene en el siguiente si la donataria cumple en tiempo sus obligaciones, en especial la **declaración de transparencia de mayo** (Art. 82 fr. VI LISR). No hay un trámite de "renovación" separado en el esquema vigente (fuente: RMF y guías CEMEFI; confianza media: confirma la regla exacta en la RMF 2026, cuya numeración cambió a 3.10.1.x).
- Requisitos que deben seguir cumpliéndose: objeto exclusivo (Art. 79 y 82 fr. I), cláusulas irrevocables de patrimonio y liquidación en estatutos (fr. IV y V), RFC y domicilio actualizados (requisito reforzado en la RMF 2026, regla 3.10.1.1), opinión de cumplimiento positiva.

Consulta el estado con `donatarias_consultar` (MCP `mp_donatarias_sat`; el directorio no refleja revocaciones posteriores a su corte).

## Alertas (90 días antes)

| Fecha | Obligación |
|---|---|
| 15 de febrero | Declaración anual informativa (Art. 86 LISR) |
| Mayo | Declaración de transparencia (Art. 82 fr. VI) |
| Día 17 de cada mes | Informe de donativos en efectivo > $100,000 (Art. 82 fr. VII), si aplica |
| Cuando cambie | Actualización de estatutos, representante legal, domicilio o actividades (avisos en el portal del SAT) |

## Si se revoca o no se renueva

- Plazo de **12 meses** para obtener nuevamente la autorización; si no se obtiene, transmitir **todo el patrimonio** a otra donataria autorizada dentro de los **6 meses** siguientes (Art. 82 fr. V LISR). Mientras tanto tributa en el Título II.
- Si la causa fue no publicar la información de transparencia: cumplir dentro del mes siguiente a la notificación para poder pedir nueva autorización (Art. 82 fr. VI, 2.º párrafo).

## Output esperado

```json
{
  "operation": "renovacion-autorizacion-anual",
  "data": {
    "rfc_hash": "...",
    "aparece_en_directorio_sat": true,
    "fecha_corte": "2026-10-15",
    "proximo_plazo": "declaración anual informativa 2027-02-15",
    "dias_restantes": 123,
    "plazo_transparencia": "mayo 2027 (228 días al 31-may)",
    "documentos_requeridos": ["estados financieros 2026", "relación de donativos", "informe de actividades"],
    "riesgo_revocacion": "bajo"
  },
  "vigencia_validada": false
}
```

## Casos edge

- Donataria con revocación publicada en el DOF: no emitir CFDI de donativo deducible desde la fecha de efectos.
- Datos incompletos → solicitar al usuario. Modo mock por default si no hay credenciales.

## Dependencias

- `core-mexico` (CFDI, RFC, mxn-formato)
- MCP `mp_donatarias_sat`; tracker local

Valida con el contador o abogado de la donataria.
