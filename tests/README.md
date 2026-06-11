# Tests de regresión

Fixtures de input + expected output para skills con cálculo determinístico. Permiten regresión cuando ajustes el skill.

## Estructura

```
tests/fixtures/<skill>/
  case-<n>-<descripcion>.json
```

Cada caso tiene:
```json
{
  "name": "descripción del caso",
  "input": { ... datos que el skill consume ... },
  "expected_output": { ... resultado correcto ... },
  "vigencia_validada": "YYYY-MM-DD",
  "fuente_verificacion": "URL o referencia donde validaste el expected",
  "notas": "cualquier consideración relevante"
}
```

## Cómo correrlos manualmente

1. Lee el caso de fixture.
2. En sesión Claude Code con el plugin cargado, pega el `input` como prompt formateado.
3. Compara la salida de Claude contra `expected_output`.
4. Si no coincide: o el skill cambió legítimamente (actualiza el expected), o regresión (ajusta el skill).

## Cómo correrlos automatizado

Cuando exista un test runner del monorepo:
```bash
./scripts/run-fixtures.sh
```

(Aún no implementado. Por ahora ejecución manual o vía evals/_runner.py custom.)

## Importante: estos fixtures son seed, no exhaustivos

Cada skill necesita 20-50 casos para cobertura razonable. Estos archivos son **3-5 casos por skill** como semilla. Conforme uses los skills, agrega casos reales (anonimizados) que hayas verificado.

## Estado de verificación

**Los `expected_output` de estos fixtures están basados en mi training data.** Para usarlos como verdad, hay que:
1. Validar manualmente que el expected es correcto contra fuente vigente.
2. Anotar `vigencia_validada` con la fecha.
3. Anotar `fuente_verificacion`.

Por ahora `vigencia_validada: null` en todos los archivos — significa "no verificado contra fuente vigente".
