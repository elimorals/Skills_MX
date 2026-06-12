# Brief para abogado mercantilista — validación de contratos comerciales

**Fecha**: 2026-06-12
**Esfuerzo estimado**: 4-6 horas de consultoría ($5-12k MXN).
**Entregables**: revisión de 3 plantillas de contrato + recomendaciones de cláusulas + redacción correctiva.

---

## 0. Contexto en 2 párrafos

Plugins-mx es un monorepo de software para automatizar operación de PyMEs y freelancers en México. Generamos templates de contratos comerciales que **se exponen al usuario final** y que pueden tener consecuencias legales reales si están mal redactados.

Necesitamos validación de un abogado mercantilista vigente CDMX (o tu jurisdicción) que firme que estos templates están bien antes de exponerlos a clientes externos.

---

## 1. Archivos a revisar (paths exactos)

| Archivo | Vertical |
|---|---|
| `freelancers-mx/skills/cliente-onboarding/SKILL.md` | Contrato marco freelancer-cliente |
| `freelancers-mx/skills/propuesta-comercial/SKILL.md` | T&Cs en propuesta + cláusulas IP/responsabilidad |
| `freelancers-mx/skills/cobranza-seguimiento/SKILL.md` | Carta formal de requerimiento (prueba juicio mercantil) |
| `despacho-legal-mx/skills/contrato-prestacion-servicios-legales/SKILL.md` | Cuota litis + jurisdicción |
| `constructora-mx/skills/contrato-obra-precio-alzado/SKILL.md` | Lump sum + penalización + vicios ocultos |
| `arrendador-residencial-mx/skills/contrato-arrendamiento-mx/SKILL.md` (si existe) | Arrendamiento por estado |

---

## 2. Preguntas específicas (las "killer questions")

### 2.1 Contrato marco freelancer-cliente

1. **Propiedad intelectual**: cláusula estándar para SaaS / consultoría. Usamos:
   > "Los entregables del proyecto serán propiedad exclusiva del CLIENTE una vez pagado el monto total. EL PROVEEDOR se reserva el uso de elementos genéricos (componentes reutilizables, frameworks, libraries) que precedieron al proyecto."
   - ¿Está bien redactado para protegerlo en disputa? ¿Falta algo crítico?

2. **Limitación de responsabilidad**:
   > "La responsabilidad máxima del PROVEEDOR está limitada al monto total pagado por el CLIENTE bajo este contrato."
   - ¿Es ejecutable en MX? ¿En qué supuestos NO aplicaría (dolo, mala fe)?

3. **Jurisdicción**: usamos CDMX por defecto. ¿Recomendaciones para freelancer en GDL o MTY?

4. **Cláusula no-solicitation**: 12 meses post-término. ¿Tiempo razonable? ¿Riesgo de declararse abusiva?

### 2.2 Carta formal de requerimiento

5. La carta de cobranza etapa 4 (D+30/D+45) — ¿cumple requisitos para servir como prueba en juicio mercantil ejecutivo (Art. 1391-1414 CCom)?

6. ¿Falta algún elemento como interpelación judicial, plazo claro de pago, mora, intereses moratorios calculados?

7. Tasa moratoria que usamos: **6% anual mercantil** (Art. 362 CCom) o **9% civil** (Art. 2395 CCDF) según caso. ¿Vigentes? ¿Variable según acuerdo?

### 2.3 Cuota litis (despacho-legal)

8. La cláusula de cuota litis (% del beneficio obtenido al éxito):
   > "EL CLIENTE pagará a EL DESPACHO el [X]% del beneficio económico neto obtenido, una vez deducidas costas y gastos."
   - ¿Es válida en CDMX? ¿Hay tope legal del porcentaje?
   - ¿Qué pasa si el cliente despide al despacho antes de obtener éxito? ¿Honorarios devengados, ¿cómo se calculan?

### 2.4 Contrato de obra a precio alzado (constructora)

9. Penalización por demora típica 0.5% por día con tope. ¿Aceptado en jurisprudencia o se considera abusivo?

10. Plazo de vicios ocultos:
    > "EL CONTRATISTA responderá por vicios ocultos en la obra durante 1 año a partir de la entrega-recepción."
    - ¿Es lo mínimo legal (Art. 2154 CCFm) o se puede extender? ¿Vicio aparente vs oculto, definición clara?

11. Cláusula de fuerza mayor — ¿excluir explícitamente lluvia normal y problemas de proveedor es ejecutable?

### 2.5 LFPDPPP en contratos

12. Aviso de privacidad firmado y aceptado por escrito como **anexo al contrato**: ¿es suficiente para cumplir con INAI?

13. Para datos sensibles (legal, salud): ¿se requiere **consentimiento expreso adicional** separado del aviso?

---

## 3. Formato de respuesta esperado

Idealmente:
- **Anotaciones en línea** sobre los SKILL.md que te enviaré como PDF
- **Tabla resumen**: pregunta # → ✅ correcto / ⚠ matiz / ❌ corregir + redacción sugerida
- **Cláusulas adicionales** que recomiendes incluir (que no contemplamos)

---

## 4. Honorarios y entrega

- **Honorarios estimados**: $5,000-$12,000 MXN según tu tarifa
- **Entrega**: PDF anotado o documento Word con sugerencias
- **Plazo solicitado**: 3 semanas (antes de fin de Sem 5 del plan = 2026-07-17)

---

## 5. Qué sigue después de tu validación

1. Aplico tus correcciones a los SKILL.md (estimo 1-2 días)
2. Marco vigencia validada con fecha + tu firma digital en frontmatter del skill
3. Genero fixtures de prueba con tus casos (cláusulas correctamente redactadas)
4. Te invitamos a revisión anual del skill (servicio recurrente $X si te interesa)

---

## 6. Datos del proyecto

- **Repositorio**: `/Users/elias/Documents/Trabajo/skills/`
- **Contacto**: Elías Rashid Morales Mendoza — elias@cipreholding.com
