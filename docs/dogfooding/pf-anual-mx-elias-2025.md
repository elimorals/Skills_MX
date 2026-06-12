# Dogfooding `pf-anual-mx` — declaración personal Elías 2025

**Objetivo**: ser TU PROPIO primer caso real de `pf-anual-mx`. Antes de marzo-abril 2027 (temporada anual oficial), correr el workflow completo con TUS CFDIs reales del ejercicio 2025 y comparar contra cálculo de contador.

**Por qué TÚ eres el caso ideal**:
- Conoces el contexto técnico — detectas errores que un cliente externo no.
- Tu declaración real ya pasa por contador → tienes "ground truth" para comparar.
- Si rompe, rompe contigo y no con un cliente piloto pagando.
- Si funciona, tienes 1 caso de éxito con métrica concreta (horas ahorradas vs proceso manual).

**Duración estimada**: 20-40h distribuidas en 3 semanas (sem 6-8 del plan).

---

## Pre-requisitos

| Item | Tienes? | Cómo obtener si no |
|---|---|---|
| e.firma vigente | ¿? | Cita SAT (4-8 semanas espera) |
| Tu RFC | ✅ | conocido |
| Régimen 2025 (PFAE_612 / RESICO_PF_626 / ASALARIADO_605) | ¿? | CSF actual: `mp_sat_portal.descargar_csf` |
| Contraseña SAT | ✅ | conocida |
| Brief contador respondido | ⏳ | Ver `docs/consultorias/brief-contador-...md` — Sem 2-4 |
| Tarifas 2025 vigentes confirmadas | ⏳ | Sale del brief contador |

---

## Plan Sem 6-8

### Sem 6 — Setup ambiente real

**Día 1-2 (4h)**:
1. Crear `.env` con vars reales (NUNCA commitear):
   ```bash
   SAT_RFC=...
   SAT_EFIRMA_CERT=~/.efirma/cer.cer
   SAT_EFIRMA_KEY=~/.efirma/key.key
   SAT_EFIRMA_PASSWORD='...'
   PLUGINS_MX_PLAYWRIGHT_REAL=1
   ```
2. Verificar e.firma cargada:
   ```bash
   cd mcp-servers
   .venv/bin/python -c "
   from mp_sat_portal.efirma_loader import EfirmaLoader
   l = EfirmaLoader.from_env()
   m = l.metadata()
   print(f'RFC: {m.rfc}')
   print(f'Vigencia: {m.not_after.date()}')
   print(f'Dias para vencer: {m.days_until_expiry}')
   "
   ```
3. Si pasa: continuar. Si falla con cert vencido: agendar cita SAT (HUMANO bloqueador 4-8 sem).

**Día 3-4 (4h)** — validar Playwright contra portal SAT:
1. `pip install playwright && playwright install chromium`
2. Correr `_real_verificar_efirma_vigente` contra portal real:
   ```bash
   .venv/bin/python -c "
   from mp_sat_portal.playwright_client import SatPlaywrightClient
   c = SatPlaywrightClient.from_env(headless=False)  # headless=False para ver el navegador
   r = c.verificar_efirma_vigente('TU_RFC')
   print(r)
   "
   ```
3. Si selectores rompen: actualizar `selectors.py` con los reales del portal (1-3h).
4. Validar que login completa exitoso.

### Sem 7 — Descarga real + revisión

**Día 1-3 (6-10h)** — implementar el `_real_*` que falta:
1. Implementar `_real_descargar_cfdi_masivo` siguiendo el patrón del README.
   - Es el método más complejo: navega a `portalcfdi.facturaelectronica.sat.gob.mx`, llena filtros, hace request masivo, espera (1-4h async), descarga ZIP.
2. Probar con 1 mes pequeño primero (ej. enero 2025).
3. Verificar que el ZIP descargado tiene XMLs válidos.

**Día 4-5 (4h)** — ejecutar workflow:
```bash
# Modo dry-run primero (no envía nada, no toca SAT):
PLUGINS_MX_MOCK=1 \
  workflow pf-anual-mx/workflows/pf-anual-completa.workflow.js \
  --args '{"rfc":"TU_RFC","ejercicio":2025,"regimen":"<TU_REGIMEN>","incluir_bancos":true}'

# Si dry-run corre limpio, modo real:
PLUGINS_MX_MOCK=0 PLUGINS_MX_PLAYWRIGHT_REAL=1 \
  workflow pf-anual-mx/workflows/pf-anual-completa.workflow.js \
  --args '...'
```

Tracker de hitos del run:
- [ ] Fase 0 Validación pasa (e.firma vigente verificada en portal real)
- [ ] Fase 1 CFDIs descarga real completa (puede tomar 1-4h)
- [ ] Fase 2 Deducciones identifica deducciones tuyas reales del ejercicio
- [ ] Fase 3 Bancos cruza vs tus extractos reales (opcional)
- [ ] Fase 4 ISR calcula montos
- [ ] Fase 5 Riesgo no detecta falsos positivos
- [ ] Fase 6 Borrador genera PDF presentable
- [ ] Fase 7 Tracker persiste correctamente
- [ ] Output final coherente

### Sem 8 — Comparativa con contador + ajustes

**Día 1-2 (4h)**:
1. Enviar PDF generado a tu contador.
2. Pedirle que lo coteje contra su cálculo del ejercicio 2025.
3. Recibir feedback (puede tomar 1 semana — agendar early).

**Día 3-5 (4-8h)** — aplicar correcciones:
1. Por cada discrepancia → ajustar skill correspondiente.
2. Anotar en `docs/estado-real.md` los nuevos scores honestos.
3. Documentar las "lecciones del dogfooding" en este mismo archivo (al final).
4. Generar fixture de prueba con TUS datos (anonimizados) para `tests/fixtures/`.

---

## Métricas objetivo

| Métrica | Hipótesis | Medición |
|---|---|---|
| Tiempo total dogfooding | <40h | Cronometrar |
| Tiempo del workflow ejecutándose | <2h end-to-end (excluyendo wait SAT) | Logs |
| Discrepancia ISR vs contador | ≤2% | Comparación numérica |
| Fases que rompen | 0 críticas | Tracker arriba |
| Selectores rotos descubiertos | 0-3 | Updates a `selectors.py` |

## Lecciones aprendidas (rellenar post-dogfooding)

> Al terminar Sem 8, rellenar:
>
> - **Lo que funcionó bien**: ...
> - **Lo que rompió**: ...
> - **Tiempo real**: ... (vs hipótesis 20-40h)
> - **Discrepancia con contador**: ...
> - **Próximos verticales aplicables**: ¿este patrón sirve para `freelance-tax-mx` cierre mensual? ¿Para `arrendador-residencial-mx`?
> - **Score honesto post-validación**: pasar de 4.4/9 actual a X/9 (target 7.5/9)

---

## Smoke test antes del run real

Para verificar que el workflow se carga sin errores antes de gastar 2h en un run real:

```bash
# Desde la raíz del repo
python scripts/smoke_test_workflows.py
```

Ese script (próximo a crearse) carga los 2 workflows y verifica que `meta` esté bien formado, que los schemas sean válidos JSONSchema y que cada `agent()` reciba un prompt no vacío.

---

## Riesgos del dogfooding

| Riesgo | Mitigación |
|---|---|
| Tu e.firma se bloquea por intentos fallidos | Validar localmente PRIMERO con `efirma_loader`. Solo ir al portal cuando esté 100% verificada. |
| Descarga masiva SAT tarda > 4h | Programar overnight, no en sesión activa. |
| PDF generado tiene cifras incorrectas | NO presentar declaración real desde el workflow — usar solo para comparar. Tu contador presenta. |
| Discrepancia grande con contador → rabbit hole | Cap a 3 días de debug. Si excede: documentar, mover a backlog, presentar con cálculo del contador este año. |

---

## Después del dogfooding

Si el resultado es positivo (≤2% discrepancia, ≤40h total):
- Marcar `pf-anual-mx` score honesto en 7.5/9 con fecha + tu firma.
- Documentar caso de éxito en `docs/casos-uso-documentados.md` (anonimizado).
- Plan: 2-3 freelancers de tu red como pilotos pagados marzo 2027.

Si el resultado es regular (3-5% discrepancia, 40-60h):
- Mover a 6.5/9.
- Ajustar 1 iteración más antes de exponer a externos.
- Plan: revisar gaps con contador antes de pilotos.

Si el resultado es negativo (>5% o >60h):
- Mantener en 5.0/9.
- Documentar gaps específicos.
- Reevaluar si vale la pena llevar a producción este año.

---

## Ver también

- `pf-anual-mx/workflows/pf-anual-completa.workflow.js` — el código del workflow
- `pf-anual-mx/agents/workflow-pf-anual-completa.md` — la plantilla declarativa
- `docs/consultorias/brief-contador-...md` — qué validar con contador (Sem 2-4)
- `mcp-servers/mp_sat_portal/SETUP_PLAYWRIGHT_REAL.md` — activación del path real
