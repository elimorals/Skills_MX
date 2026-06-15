# Estado real vs producción — auditoría honesta

**Fecha de auditoría**: 2026-06-11
**Auditor**: el mismo Claude que escribió los skills (autocrítica obligada).
**Propósito**: separar **lo que está hecho** de **lo que parece hecho pero no lo está**, sin maquillar.

---

## TL;DR

Los 54 skills lint-passing son **scaffolding denso**, NO producción. Cada vertical necesita 6-10 semanas adicionales de afinación con disciplina antes de exponer a cliente final. Este documento es el mapa exacto de qué falta por skill.

---

## Checklist de 9 puntos para producción (de `docs/arquitectura.md`)

1. Triggering: 30+ prompts variados probados con tasa correcta ≥85%
2. Cobertura de dominio: reglas oficiales con vigencia verificada contra fuente
3. Casos edge documentados: ≥5 con cómo manejarlos
4. Validaciones críticas: chequeos que evitan errores fiscales/legales silenciosos
5. Salida estructurada: JSON intermedio + presentación legible al usuario
6. Tono apropiado: matiz técnico vs no-técnico
7. Integración mockeable: funciona sin credenciales, marca mock claramente
8. Lint passing
9. Validación con experto del dominio: al menos un revisor del sector confirmó outputs reales

Para cada skill se reporta **X/9 puntos cumplidos** con detalle.

---

## Auditoría por skill

### `_shared/cfdi-emision`

| # | Punto | Estado | Nota |
|---|---|---|---|
| 1 | Triggering 30+ prompts | ❌ 0% | Description escrito con criterio propio, sin evals corridas |
| 2 | Vigencia oficial | ⚠ 60% | Cubre 4.0 actual; los catálogos son aproximados a mi training, no verificados contra portal SAT 2026 |
| 3 | Casos edge | ✅ 90% | `casos-edge-cfdi.md` cubre 10 casos (anticipos, exportación, factura global, refacturación, REP, médicos deducibles, sustitución, nota de crédito, redondeo). Faltan: complementos específicos por industria (Carta Porte, INE, Comercio Exterior, etc.) |
| 4 | Validaciones críticas | ✅ 80% | 7 validaciones listadas. Faltan: validación de catálogos contra última versión publicada SAT, validación de complementos por giro |
| 5 | Salida estructurada | ✅ 100% | JSON intermedio + presentación |
| 6 | Tono apropiado | ✅ 100% | Matiz técnico/no-técnico al final |
| 7 | Integración mockeable | ⚠ 50% | Mencionado pero no construido el mock concreto (no hay `references/mock-pac-response.json`) |
| 8 | Lint passing | ✅ | |
| 9 | Validación experta | ❌ 0% | Ningún contador revisó esto |

**Score: 5.6/9** — el más maduro del lote por la inversión que le metí.

**Lo que requiere verificación vigente urgente**:
- Catálogo `c_UsoCFDI`: el SAT pudo agregar o retirar claves
- Catálogo `c_RegimenFiscal`: revisar si se agregaron regímenes después de RESICO
- ClaveProdServ patrones por giro: parcialmente al ojo, no exhaustivo
- Reglas de cancelación (motivos 01-04, plazos): pueden tener actualización en RMF 2026
- Reglas de complemento de pago (REP) versión y campos: la versión Pagos cambia ocasionalmente

---

### `_shared/iva-retenciones-mx`

| # | Punto | Estado | Nota |
|---|---|---|---|
| 1 | Triggering | ❌ 0% | |
| 2 | Vigencia | ⚠ 60% | Tasas vigentes a mi training. RESICO PF tasas (1.0, 1.1, 1.5, 2.0, 2.5%) pueden haber sido ajustadas en RMF 2025/2026 |
| 3 | Casos edge | ✅ 70% | Matriz cubre 10 escenarios. Faltan combinatorias raras (RESICO con autotransporte, frontera con extranjero, etc.) |
| 4 | Validaciones críticas | ⚠ 60% | Reglas de oro listadas, pero no hay calculadora ejecutable |
| 5 | Salida estructurada | ✅ 100% | |
| 6 | Tono | ✅ 100% | |
| 7 | Integración mockeable | ✅ 100% | No requiere integración externa |
| 8 | Lint | ✅ | |
| 9 | Validación experta | ❌ 0% | |

**Score: 5.0/9**

**Verificación vigente urgente**:
- Tarifa progresiva Art. 96 LISR: se actualiza cada año por inflación
- Tasas RESICO PF (1-2.5%): confirmar vigentes
- Tasas RESICO PM: no las cité pero deben validarse
- Retención REPSE 6% IVA: revisar si cambió post-reforma
- Decreto región fronteriza: vigencia, lista de municipios actualizada

---

### `_shared/rfc-validacion`

| # | Punto | Estado | Nota |
|---|---|---|---|
| 1 | Triggering | ❌ 0% | |
| 2 | Vigencia | ✅ 90% | Las reglas de estructura RFC son estables hace décadas |
| 3 | Casos edge | ✅ 70% | Cubre genéricos, palabras inconvenientes, separadores |
| 4 | Validaciones | ✅ 80% | 7 validaciones. Falta: integración real con API SAT validación masiva, 69-B EFOS |
| 5 | Salida estructurada | ✅ 100% | |
| 6 | Tono | ✅ 100% | |
| 7 | Integración mockeable | ⚠ 50% | API SAT mencionada pero no implementada |
| 8 | Lint | ✅ | |
| 9 | Validación experta | ❌ 0% | |

**Score: 6.0/9** — el más sólido en términos absolutos por dominio estable.

**Verificación**:
- Listado de palabras inconvenientes: puede haber adiciones del SAT
- Estructura de algoritmo de homoclave: estable pero el skill no la calcula matemáticamente

---

### `_shared/whatsapp-business-mx`

| # | Punto | Estado | Nota |
|---|---|---|---|
| 1 | Triggering | ❌ 0% | |
| 2 | Vigencia | ⚠ 60% | Reglas y tarifas Meta cambian frecuentemente; mis precios ($0.03-0.09 USD) son aproximados |
| 3 | Casos edge | ⚠ 60% | Cubre tipos UTILITY/MARKETING/AUTH. Falta: manejo de calidad de cuenta degradada, recategorización automática Meta, recientes cambios en política regional |
| 4 | Validaciones | ⚠ 50% | Reglas generales pero no validador automático de templates |
| 5 | Salida estructurada | ✅ 100% | |
| 6 | Tono | ✅ 100% | |
| 7 | Integración mockeable | ⚠ 50% | Templates listados pero no hay mock de respuesta de Meta API |
| 8 | Lint | ✅ | |
| 9 | Validación experta | ❌ 0% | Ningún CM senior revisó los templates |

**Score: 4.7/9**

**Verificación urgente**:
- Tarifas Meta por categoría México: validar contra pricing.meta.com vigente
- Reglas de aprobación 2026: Meta actualizó políticas recientemente
- Templates sugeridos: pasarlos por aprobación real en una cuenta sandbox

---

### `_shared/compliance-lfpdppp`

| # | Punto | Estado | Nota |
|---|---|---|---|
| 1 | Triggering | ❌ 0% | |
| 2 | Vigencia | ⚠ 70% | LFPDPPP estable desde 2010 con reformas. Las reformas más recientes (2017+) están parcialmente cubiertas |
| 3 | Casos edge | ⚠ 60% | Cubre 6 sectores, falta: tratamiento de datos transfronterizos detallado, vulneraciones con notificación INAI, casos de empresas IT |
| 4 | Validaciones | ⚠ 60% | Checklist operativo presente, no hay validador automático de avisos |
| 5 | Salida estructurada | ✅ 100% | Plantillas completas |
| 6 | Tono | ✅ 90% | Apto para audiencia no-jurídica |
| 7 | Integración mockeable | ✅ 100% | No requiere |
| 8 | Lint | ✅ | |
| 9 | Validación experta | ❌ 0% | Ningún abogado de protección de datos revisó esto |

**Score: 5.3/9**

**Verificación**:
- Reformas LFPDPPP post-2022: mi training puede no cubrir todas
- Multas vigentes INAI: rangos pueden haber cambiado
- Plantillas por sector: revisar con abogado especializado

---

### `_shared/mxn-formato`

| # | Punto | Estado | Nota |
|---|---|---|---|
| 1 | Triggering | ❌ 0% | |
| 2 | Vigencia | ✅ 90% | Convenciones de formato monetario son estables |
| 3 | Casos edge | ✅ 80% | Cubre cero, negativos, otras monedas, decimales no estándar |
| 4 | Validaciones | ✅ 70% | Reglas claras |
| 5 | Salida estructurada | ✅ 100% | |
| 6 | Tono | ✅ 100% | |
| 7 | Integración mockeable | ✅ 80% | Banxico para TC mencionado pero no implementado |
| 8 | Lint | ✅ | |
| 9 | Validación experta | ❌ 0% | |

**Score: 6.2/9** — el más sólido por dominio simple y estable.

---

### `freelancers-mx/skills/cotizacion-mxn`

| Punto | Estado | Nota |
|---|---|---|
| 1 Triggering | ❌ 0% | |
| 2 Vigencia | ⚠ 70% | Plantilla y cálculos son representativos pero usan tarifas/retenciones que deben verificarse |
| 3 Casos edge | ✅ 60% | 4 casos cubiertos (PFAE→PM, RESICO PF, PF→PF, exportación). Faltan: cliente moroso histórico con anticipo, cotización multi-moneda, cotización con escalación de precio anual |
| 4 Validaciones | ⚠ 50% | Reglas mencionadas pero no implementadas |
| 5 Salida estructurada | ✅ 100% | |
| 6 Tono | ✅ 90% | |
| 7 Integración mockeable | ✅ 100% | |
| 8 Lint | ✅ | |
| 9 Validación experta | ❌ 0% | |

**Score: 4.9/9**

---

### `freelancers-mx/skills/propuesta-comercial`

| Punto | Estado | Nota |
|---|---|---|
| 1-8 | Similar a cotizacion-mxn | |
| 9 Validación experta | ❌ 0% | El contrato marco NO revisado por abogado mercantil. Cláusulas como "limitación de responsabilidad", "no-solicitation", "jurisdicción CDMX" tienen forma típica pero requieren validación |

**Score: 4.5/9**

**Verificación URGENTE**:
- Cláusula de propiedad intelectual: la redacción típica que escribí puede no proteger al freelancer en casos específicos (ej. componentes reutilizados que generaron IP del cliente)
- Cláusula de limitación de responsabilidad: el monto máximo (=monto pagado) es la convención, pero hay sectores donde se exige más
- Jurisdicción CDMX: asume que el freelancer está en CDMX. Si es Guadalajara o Monterrey, ajustar

---

### `freelancers-mx/skills/cobranza-seguimiento`

| Punto | Estado | Nota |
|---|---|---|
| 1-8 | Similar | |
| 9 Validación experta | ❌ 0% | Carta formal de requerimiento no revisada por abogado |

**Verificación**:
- Carta formal: validar que cumple requisitos para servir como prueba en juicio mercantil ejecutivo
- Tasa moratoria 6% mercantil / 9% civil: vigente Art. 362 CCom / 2395 CCDF — confirmar
- Procedimiento extrajudicial: validar opciones reales con despacho

**Score: 4.7/9**

---

### `freelancers-mx/skills/cliente-onboarding`

| Punto | Estado | Nota |
|---|---|---|
| 1-8 | Similar | |
| 9 Validación experta | ❌ 0% | Contrato marco no revisado por abogado |

**Score: 4.5/9**

---

### `freelancers-mx/skills/freelance-tax-mx`

**Este es el skill con MAYOR riesgo regulatorio.**

| Punto | Estado | Nota |
|---|---|---|
| 1 Triggering | ❌ 0% | |
| 2 Vigencia | ❌ 40% | **Tarifa Art. 96 LISR de mi training** — las cifras de los rangos ($8,952.49, $75,984.55, $133,536.07, etc.) **pueden estar desactualizadas**. SAT actualiza por inflación anualmente |
| 3 Casos edge | ⚠ 60% | Cubre RESICO PF, PFAE. Falta: PFAE con sueldos asimilados, RESICO PM, situaciones mixtas |
| 4 Validaciones | ⚠ 60% | Alertas listadas, no implementadas como código |
| 5 Salida estructurada | ✅ 100% | |
| 6 Tono | ✅ 90% | |
| 7 Integración mockeable | ✅ 100% | |
| 8 Lint | ✅ | |
| 9 Validación experta | ❌ 0% | **Crítico — un contador DEBE revisar antes de uso real** |

**Score: 4.4/9**

**🚨 Aviso de riesgo**: si alguien usa este skill para calcular un pago provisional y los datos de tarifa están desactualizados, el cálculo será incorrecto. El SAT puede generar diferencias y multas. **NO USAR EN PRODUCCIÓN SIN VALIDACIÓN DE CONTADOR.**

---

### `agencia-marketing-mx/skills/*`

| Skill | Score honesto | Riesgo |
|---|---|---|
| reporte-mensual-cliente | 4.5/9 | Bajo (no toca datos fiscales/regulatorios; impacto = mal reporte) |
| meta-ads-optimization | 4.7/9 | Bajo-medio (consejos pueden estar desactualizados según Meta 2026) |
| copy-mexicano | 4.8/9 | Bajo (subjetivo, fácil iterar) |
| community-management-mx | 4.5/9 | Bajo-medio (templates pueden necesitar ajuste según red social actual) |
| briefing-creativo | 4.5/9 | Bajo |

Promedio: **4.6/9**. Los más bajos en validación experta pero el daño potencial es contenido (no hay regulación fiscal involucrada).

---

### `colegios-mx/skills/*`

| Skill | Score honesto | Riesgo |
|---|---|---|
| cobranza-colegiaturas | 4.3/9 | **Alto** — políticas de retención académica son legalmente sensibles |
| comunicacion-padres-wa | 4.5/9 | Medio |
| constancias-academicas | 4.0/9 | **Alto** — CCT/RVOE específicos por estado, formato puede no cumplir requisito SEP local |
| cfdi-colegiaturas-deducibles | 4.0/9 | **Muy alto** — topes de deducción listados pueden estar desactualizados; complemento InsEduc puede tener versión nueva |

Promedio: **4.2/9**. Vertical con riesgo regulatorio alto. **No usar sin partner del sector.**

---

### `talleres-mx/skills/*`

| Skill | Score honesto | Riesgo |
|---|---|---|
| diagnostico-cotizacion | 4.5/9 | Bajo (proceso operativo, no regulatorio) |
| autorizacion-cliente-wa | 4.5/9 | Medio (defensa PROFECO depende de calidad de bitácora) |
| garantia-servicio | 4.3/9 | **Medio-alto** — plazos PROFECO citados de memoria; NMX-D-003-IMNC no verificada |
| orden-trabajo | 4.5/9 | Medio |

Promedio: **4.4/9**.

---

## Resumen ejecutivo

### Score promedio del monorepo: **4.7/9** (todos los skills)

### Distribución por riesgo regulatorio

| Nivel de riesgo | Verticales/skills | Acción mínima antes de producción |
|---|---|---|
| **Bajo** | mxn-formato, rfc-validacion, copy-mexicano, briefing-creativo | Iterar con dogfooding; partner opcional |
| **Medio** | cotizacion-mxn, propuesta-comercial, reporte-mensual, comunicacion-padres-wa, diagnostico-cotizacion, orden-trabajo | Revisión legal de contratos; dogfooding |
| **Alto** | cfdi-emision, iva-retenciones-mx, cobranza-colegiaturas, constancias-academicas, garantia-servicio | **Partner del sector obligatorio + validación de fuentes vigentes** |
| **🚨 Muy alto** | freelance-tax-mx, cfdi-colegiaturas-deducibles | **Contador certificado + sandbox PAC real + casos de prueba auditados ANTES de cualquier uso** |

### Lo que NO puedo hacer desde mi rol

- Verificar contra portal SAT 2026 actual (requiere navegación web actualizada o partner contador)
- Correr evals reales contra el sistema de calibración de descriptions (`skill-creator` workflow requiere `claude -p` con prompts en loop, no factible en una sesión)
- Conectar a Facturama sandbox real (requiere credenciales)
- Validar templates WhatsApp contra aprobación real Meta (requiere cuenta Business activa)
- Revisar contratos con abogado mercantil
- Obtener firma de experto del dominio en cada vertical

### Lo que SÍ puedo hacer y voy a hacer ahora

1. ✅ **Este documento** (estado-real.md) — ya escrito
2. 🔄 **Calibration prompts** ejecutables por vertical (próximo paso)
3. 🔄 **Banderas in-skill** marcando exactamente qué requiere verificación vigente
4. 🔄 **Fixtures de prueba** para los skills con cálculo determinístico (CFDI, IVA, freelance-tax)
5. 🔄 **Plan de afinación** semana a semana por vertical

---

## Métrica de honestidad

Si la diferencia entre **scaffolding** y **producción** se cuantifica en horas-hombre:

- **Tengo: ~30 horas de scaffolding denso** (lo que invertí en esta sesión)
- **Falta: ~240-400 horas por vertical** para producción (1 mes calendario por vertical con dogfooding + 2-4 semanas de validación experta)

Por **los 4 verticales**: **1,000-1,600 horas** adicionales calendario para llegar a producción-grade los cuatro. Realista: 6-12 meses si trabajas solo + partners. Más rápido con un equipo dedicado.

---

## Recomendación

**No expongas estos plugins a clientes pagando todavía.** El scaffolding está bien para:
- Continuar iterando contigo en dogfooding
- Mostrarlos como prototipo a posibles partners (no como producto)
- Construir tracción interna y aprendizaje

**Antes de cobrar a un cliente externo por implementación**, el skill que toque ese cliente debe llegar a 7-8/9 puntos del checklist. Lo que ahora está en 4.5/9 promedio.

La buena noticia: la arquitectura sí está bien fundada. La afinación es trabajo lineal y predecible una vez que se reconoce la magnitud real.
