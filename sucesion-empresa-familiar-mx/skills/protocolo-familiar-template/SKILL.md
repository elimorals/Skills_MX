---
name: protocolo-familiar-template
description: Genera un template editable de protocolo familiar para empresa familiar mexicana - órganos de gobierno (asamblea familiar, consejo de familia, consejo de administración), reglas de entrada de familiares a trabajar, sucesión en la dirección, transmisión de acciones (derecho de preferencia, cláusulas de admisión), dividendos, resolución de conflictos y su vínculo con los estatutos de la sociedad (LGSM). Usar cuando el usuario diga protocolo familiar template, protocolo_familiar_template, gobierno de empresa familiar, reglas para la familia en la empresa, sucesión en la dirección, consejo de familia, ayuda con protocolo familiar template.
allowed-tools: Read, Write
---

# Protocolo familiar (template)

El protocolo familiar es un acuerdo entre familiares; **por sí solo no obliga a la sociedad ni a terceros**. Lo que deba ser exigible (transmisión de acciones, quórums, consejo) debe trasladarse a los **estatutos** y, en su caso, a convenios entre accionistas (LGSM; en S.A.P.I., Ley del Mercado de Valores Art. 13 permite pactos más amplios) y protocolizarse ante notario.

## Secciones del template

1. **Valores y propósito** de la familia empresaria.
2. **Órganos**: asamblea familiar (todos), consejo de familia (representantes), consejo de administración (empresa, con consejeros independientes recomendados).
3. **Empleo de familiares**: requisitos (estudios, experiencia externa mínima), proceso de selección, sueldos de mercado, evaluación.
4. **Sucesión en la dirección**: criterios, plan de desarrollo, plazos, papel del fundador después del relevo.
5. **Propiedad**: quién puede ser accionista (solo descendientes en línea recta, cónyuges no), **derecho de preferencia** y cláusula de admisión (Art. 130 LGSM), valuación para compras entre familiares, qué pasa en divorcio o fallecimiento.
6. **Dividendos y liquidez**: política de reparto, fondo de liquidez para salida de socios.
7. **Conflictos**: mediación, arbitraje.
8. **Revisión**: cada cuánto se actualiza.

## Output esperado

```json
{
  "operation": "protocolo-familiar-template",
  "data": {
    "archivo_template": "protocolo-familiar-<familia>.md",
    "secciones": 8,
    "clausulas_a_trasladar_a_estatutos": ["derecho de preferencia", "cláusula de admisión", "integración del consejo"]
  },
  "vigencia_validada": false
}
```

## Casos edge

- Empresa constituida como S.A. de C.V. con estatutos antiguos: revisar si permiten las restricciones antes de prometerlas en el protocolo.
- Familias con miembros fuera de México: ley aplicable y fiscalidad internacional, derivar.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (RFC, mxn-formato); skills `diagnostico-patrimonial-familiar`, `plan-testamentario-distribucion`

⚠ Template orientativo: revisar con abogado corporativo y notario antes de firmar.
