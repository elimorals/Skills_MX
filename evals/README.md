# Evals de skills

Dos tipos de eval viven aquí:

1. **Triggering** (`<plugin>/*.eval.json`): ¿se activa el skill correcto? (abajo).
2. **Salida** (`golden/`, `promptfoo/`): ¿la respuesta es correcta?
   - `golden/*.golden.json` — casos deterministas (IVA/retenciones, RFC, MXN) contra
     los scripts de `scripts/`. Sin API key: `python3 scripts/eval-golden.py`.
   - `promptfoo/` — el `SKILL.md` como system prompt de `claude-sonnet-5-5`, con asserts
     regex + rúbrica LLM-judge. Requiere `ANTHROPIC_API_KEY`:
     `npx promptfoo@0.124.1 eval -c evals/promptfoo/promptfooconfig.yaml`
     (en CI solo vía `workflow_dispatch` de `skills-quality.yml`).

Cada caso cita su fuente (LISR, LIVA, Anexo 20, LFPDPPP 2025…). Si una ley cambia,
actualiza primero el caso golden y después el `SKILL.md` en `_shared/` + `scripts/sync-shared.sh`.

## Calibration prompts — evals para triggering de skills

Aquí viven los prompts de evaluación para calibrar el `description:` de cada skill.

## Cómo usarlos

### Manual (más simple)

1. Toma uno de los archivos `<skill>.eval.json`.
2. Para cada `prompt` con `should_trigger: true`: en una sesión de Claude Code con el plugin cargado, pega el prompt y observa si Claude invoca el skill correcto.
3. Para cada `prompt` con `should_trigger: false`: confirma que Claude NO invoque ese skill (puede invocar otro o ninguno).
4. Anota fallos: prompts donde debió triggear y no triggeó (false negatives) o donde no debió y sí (false positives).
5. Cuando ≥85% de prompts tengan resultado correcto, el `description:` está calibrado.

### Automatizado (con `skill-creator`)

El skill `skill-creator` ya cargado en tu Claude Code tiene un workflow de loop optimization que toma estos JSON y propone mejoras al `description:` iterativamente:

```bash
# desde el directorio del skill-creator
python -m scripts.run_loop \
  --eval-set ../skills/evals/freelancers-mx/cotizacion-mxn.eval.json \
  --skill-path ../skills/freelancers-mx/skills/cotizacion-mxn \
  --model claude-opus-4-7 \
  --max-iterations 5 \
  --verbose
```

Resultado: un description optimizado seleccionado por test-set score (no train), evitando overfit.

## Estructura de los archivos

```json
[
  {
    "query": "prompt realista que un usuario diría",
    "should_trigger": true,
    "rationale": "por qué este prompt debería triggear el skill"
  },
  ...
]
```

Cada archivo tiene **10-12 should_trigger + 10-12 should_not_trigger = 20-24 prompts**.

## Filosofía de prompts

- **Realistas, no abstractos**: como hablaría el usuario real, con contexto, errores, abreviaciones.
- **Near-misses en negativos**: prompts que comparten keywords con el skill pero no deben triggear (son los más valiosos para evitar over-triggering).
- **Variedad de fraseo**: formal, informal, en español, parcialmente en inglés, con acentos, con typos ocasionales.

## Estado de calibración

Ningún skill ha sido calibrado todavía. Los archivos aquí son los prompts iniciales que YO consideré realistas pero **no han sido validados con ejecución**. Cuando los corras, anota resultados en `evals/results/<fecha>.md`.
