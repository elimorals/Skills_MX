---
name: receta-electronica-cofepris
description: Generación de receta electrónica con cumplimiento COFEPRIS para consultorio especialista presencial. Incluye datos médico (cédula + e.firma), paciente (nombre + RFC opcional), diagnóstico CIE-10, medicamentos prescritos con genérico + dosis + duración, y bloqueo automático si receta incluye sustancia controlada Grupos I-II (que aún requieren receta física con código de barras). Usar cuando el usuario diga emitir receta, prescribir, receta electronica, receta cofepris.
allowed-tools: Read, Write
---

# Receta electrónica COFEPRIS

## Datos obligatorios

- **Médico**: nombre, cédula profesional federal, cédula especialidad (si aplica), domicilio consultorio, e.firma vigente
- **Paciente**: nombre completo, edad, género, peso (opcional pero recomendado)
- **Diagnóstico**: CIE-10
- **Medicamentos**: nombre genérico, presentación, dosis, vía administración, intervalo, duración
- **Indicaciones no farmacológicas**: dieta, actividad, etc.
- **Firma electrónica del médico**: e.firma SAT o solución reconocida COFEPRIS
- **Fecha emisión**

## Grupos COFEPRIS

| Grupo | Ejemplos | Permite receta digital |
|---|---|---|
| I | Heroína, opioides | ❌ Requiere receta física + código barras |
| II | Morfina, fentanilo, cocaína (uso medicinal) | ❌ Requiere receta física + código barras |
| III | Benzodiacepinas (alprazolam, diazepam) | ✅ Permitida digital (piloto 2026-2027 para generalizar) |
| IV | Antibióticos comunes | ✅ Permitida |
| V | Venta libre con receta | ✅ Permitida |
| VI | Venta libre | NA |

## Algoritmo de bloqueo

```python
def emitir_receta(medicamentos: list[Medicamento]) -> dict:
    grupos = [m.grupo_cofepris for m in medicamentos]
    if 1 in grupos or 2 in grupos:
        return {
            "error": "RECETA_FISICA_REQUERIDA",
            "razon": "Contiene medicamento Grupo I o II — usar recetario físico con código de barras",
            "uuid_emitido": None
        }
    # ... emitir receta digital
```

## Output

```json
{
  "receta_id": "REC-MOCK-001",
  "fecha_emision": "2026-06-12T11:00:00",
  "medico_cedula": "1234567",
  "paciente_rfc_hash": "abc12345",
  "diagnostico_cie10": "I10",
  "medicamentos": [
    {"generico": "Losartán", "presentacion": "50mg tab", "dosis": "1 cada 24h", "duracion_dias": 30}
  ],
  "qr_verificacion": "https://verificar.consultorio.mx/REC-001",
  "firma_medico_aplicada": true,
  "pdf_path": "~/.local/share/plugins-mx/recetas/REC-MOCK-001.pdf",
  "contiene_controlado": false
}
```
