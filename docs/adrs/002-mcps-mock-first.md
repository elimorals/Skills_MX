# ADR 002 — MCPs mock-first por default

**Status**: ACEPTADO  (2026-04)

## Context

Los MCP servers conectan con servicios externos: SAT, Facturama, Mercado Pago, Conekta, Banxico, Meta WhatsApp Cloud, bancos, portales municipales. Cada uno requiere credenciales reales — algunas son delicadas (e.firma SAT) y algunas requieren contratación con plazos largos.

Si cada test/dogfooding/demo necesita credenciales, el ciclo de desarrollo es lento y arriesgado: timbrar CFDIs reales por error, enviar WhatsApp masivos, etc.

## Decision

**Todo MCP corre en modo mock por default**. Para activar modo real, el operador debe explícitamente:
1. Configurar las variables de entorno correspondientes (`FACTURAMA_API_KEY`, `META_WA_TOKEN`, etc.).
2. Opt-in con flag específico (`PLUGINS_MX_PLAYWRIGHT_REAL=1`, etc.) en MCPs delicados.

En mock, cada respuesta lleva `simulated: true` claramente marcado para que tanto Claude como el usuario sepan que NO es real.

`shared/mock.py` provee `is_mock_mode()` y `mark_simulated()` consistente entre MCPs.

## Alternatives considered

1. **Real por default + flag para mock** — invertir la polaridad. Descartado: muy fácil "olvidar" activar mock en demos y enviar acciones reales.
2. **Sin modo mock — usar siempre sandbox externo** — Facturama sandbox sí permite; portales SAT y Banxico NO tienen sandbox. Inconsistente.
3. **Mock solo en tests** — pero entonces el dogfooding del propio operador necesita credenciales. Descartado.

## Consequences

**Positivas**:
- 92 archivos de test corriendo sin ninguna credencial real.
- Demos seguras: cero riesgo de timbrar CFDI real o enviar WhatsApp masivo accidental.
- Onboarding de nuevos contribuyentes inmediato (no esperar credenciales).
- Workflows ejecutables se prueban en CI sin secretos.

**Negativas**:
- Tests/fixtures de mock pueden divergir de respuesta real. Mitigación: cuando se activa modo real por primera vez, validar respuestas reales vs schema mock.
- Operador puede olvidar activar modo real cuando lo necesita. Mitigación: el output siempre marca `simulated: true` visible.

## Ver también

- `mcp-servers/shared/mock.py`
- ADR 005 (selectores Playwright) extiende este patrón para Playwright stubs vs reales.
