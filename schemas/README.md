# JSON Schemas

Validación estructural de inputs y outputs de skills críticos. Cumple [JSON Schema Draft 2020-12](https://json-schema.org/).

## Uso

### Validar un output

```python
import json
import jsonschema

schema = json.load(open("schemas/rfc-validation-output.schema.json"))
output = {...}  # output del skill rfc-validacion

try:
    jsonschema.validate(output, schema)
    print("Output válido")
except jsonschema.ValidationError as e:
    print(f"Inválido: {e.message}")
```

### Validar inputs antes de pasar a un skill

```python
schema = json.load(open("schemas/cfdi-payload.schema.json"))
input_data = {...}
jsonschema.validate(input_data, schema)
```

## Schemas disponibles

| Schema | Para | Usado por |
|---|---|---|
| `rfc-validation-output.schema.json` | Output de validar RFC | rfc-validacion |
| `iva-retenciones-output.schema.json` | Output de cálculo IVA/retenciones | iva-retenciones-mx |
| `cfdi-payload.schema.json` | Input para timbrar CFDI | cfdi-emision |
| `cfdi-stamped-response.schema.json` | Output de timbrado | cfdi-emision |
| `cotizacion-mxn.schema.json` | Output de cotización | cotizacion-mxn |
| `freelance-tax-output.schema.json` | Output de pago provisional | freelance-tax-mx |
| `ficha-cliente.schema.json` | Estructura de ficha de cliente | cliente-onboarding |
| `whatsapp-template.schema.json` | Estructura de template Meta | whatsapp-business-mx |

## Validación en tests/fixtures

Los fixtures de `tests/fixtures/` pueden validarse contra estos schemas para garantizar consistencia:

```bash
for f in tests/fixtures/iva-retenciones-mx/*.json; do
  python -c "
import json, jsonschema
fixture = json.load(open('$f'))
schema = json.load(open('schemas/iva-retenciones-output.schema.json'))
jsonschema.validate(fixture['expected_output'], schema)
print('✓ $f')
"
done
```
