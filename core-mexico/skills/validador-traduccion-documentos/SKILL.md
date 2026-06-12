---
name: validador-traduccion-documentos
description: Valida que documentos traducidos para uso oficial en México cumplan los requisitos de Perito Traductor Autorizado. Aplicable a actas extranjeras (nacimiento, matrimonio, divorcio, defunción), títulos académicos, certificados, contratos. Verifica que el traductor esté en lista oficial del TSJCDMX o equivalente estatal, que la traducción tenga sello del perito, y que documento original esté apostillado (Haya 1961) o legalizado consular si país no Haya. Usar cuando el usuario diga validar traducción, traductor certificado, traducir documento extranjero, perito traductor.
allowed-tools: Read, Write
---

# Validador traducciones — México

## Aplicabilidad

Documentos extranjeros que deben surtir efecto legal en México:
- Actas civiles (nacimiento, matrimonio, divorcio)
- Títulos académicos para revalidación SEP
- Contratos internacionales para registro
- Documentos para naturalización / residencia

## Requisitos para traducción válida

1. **Perito Traductor Autorizado** registrado en:
   - TSJCDMX (https://www.poderjudicialcdmx.gob.mx) si CDMX
   - Tribunal Superior de Justicia del estado correspondiente
2. **Sello del perito** en cada hoja de la traducción
3. **Firma autógrafa** del perito
4. **Hoja membreteada** con datos del perito + número de registro

## Requisitos del documento original

- **Apostilla de La Haya** si país emisor es parte del Convenio (122 países)
- **Legalización consular** si país NO es parte (ej. China, EAU)

## Algoritmo de validación

```python
def validar_traduccion(perito_data, doc_origen_data) -> dict:
    errores = []

    # 1. Perito registrado
    if not perito_data.get("registrado_tsj"):
        errores.append("Perito NO está en lista oficial del TSJ")

    # 2. Vigencia del registro
    if perito_data.get("registro_vencido"):
        errores.append("Registro del perito vencido (renovación anual)")

    # 3. Documento original certificado
    if not (doc_origen_data.get("apostillado") or doc_origen_data.get("legalizado_consular")):
        errores.append("Documento original sin apostilla ni legalización consular")

    # 4. Idiomas autorizados
    if not perito_data.get("autoriza_idioma", "").lower() in [doc_origen_data["idioma"].lower()]:
        errores.append("Perito no autorizado para este idioma")

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }
```

## Output

```json
{
  "tipo_documento": "acta_nacimiento_extranjera",
  "idioma_origen": "inglés",
  "perito": {
    "nombre_hash": "...",
    "numero_registro": "TSJCDMX-1234",
    "tsj_estado": "cdmx",
    "registrado": true,
    "registro_vigente": true,
    "idiomas_autorizados": ["inglés", "francés"]
  },
  "documento_original": {
    "pais_emisor": "USA",
    "apostillado": true,
    "fecha_apostilla": "2026-05-10"
  },
  "valido": true,
  "errores": [],
  "siguiente_paso": "Presentar para registro civil mexicano"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Perito autorizado en estado distinto al de uso | Generalmente sí aplica (validar caso) |
| Traducción simple por traductor no perito | NO válida para fines oficiales |
| Documento de país NO Haya | Legalización consular en consulado mexicano del país emisor |
| Documento militar / clasificado | Procedimientos especiales |

## ⚠ Compliance

- Listas de peritos del TSJCDMX cambian; validar contra portal vigente
- Si el documento se presenta en CDMX pero el perito es de otro estado: confirmar aceptación
