---
name: auditor-fiscal-pyme-mensual
description: Auditoría fiscal mensual automatizada para clientes PyME del despacho contable detectando errores comunes que el SAT puede observar (CFDI tipo I con método PUE pero sin REP cuando fue PPD, retenciones REPSE no acreditadas correctamente, gastos sin CFDI a nombre del cliente, depósitos en efectivo mayores a $15k sin justificación, ingresos cobrados no reportados completos, CFDIs de proveedores en lista 69-B definitiva que NO son deducibles, validación de complemento de pago en tiempo dentro del plazo de 5 días post pago, deducciones improcedentes como gasolina sin desplazamiento documentado o restaurantes excesivos). Genera reporte ejecutivo con riesgo bajo/medio/alto + acciones específicas + estimación de impacto fiscal si SAT lo observa. Diferencia entre errores subsanables (refacturar) y errores que ya causaron contingencia (multas). Cubre PFAE 612, RESICO PF 626, PM 601, RESICO PM. Usar cuando el usuario diga "auditoría fiscal mensual", "revisión SAT preventiva", "auditor contable", "análisis fiscal PyME", "validar declaración". NO usar para declaración anual (usar pf-anual-completa) ni para defensa SAT ya iniciada (eso es auditoría correctiva).
allowed-tools: Read, Write, Edit
---

# Auditoría fiscal mensual preventiva

## Categorías de revisión

### 1. CFDIs emitidos del mes

**Verificaciones**:
- Total emitido = Total reportado
- CFDIs PPD tienen REP correspondiente en plazo (5 días post-pago)
- CFDIs cancelados con motivo correcto (01-04) + sustituto si aplica
- Sin duplicados

**Riesgo si falla**: contingencia con SAT por discrepancia entre lo emitido y lo reportado.

### 2. CFDIs recibidos del mes

**Verificaciones**:
- Cada gasto deducible tiene CFDI a tu RFC
- RFC emisor NO en lista 69-B definitiva (si lo está, EXCLUIR de deducibles)
- Método de pago consistente con forma real
- Plazo de cancelación SAT cumplido (CFDI 4.0 requiere aceptación 72h)

**Riesgo si falla**: gastos no deducibles → mayor base gravable → mayor ISR

### 3. Retenciones

**Verificaciones**:
- REPSE 6% IVA bien aplicado a subcontratistas REPSE
- Honorarios PFAE 10% ISR + 10.67% IVA retenidos
- RESICO PF 1.25% ISR
- Arrendamiento 10% ISR
- CFDI tipo R emitido si tú retuviste

**Riesgo si falla**: SAT puede negar deducibilidad y aplicar multa

### 4. Cruce bancario

**Verificaciones**:
- Depósitos en efectivo > $15,000 MXN/mes (Art. 91 LISR — instituciones reportan)
- Depósitos bancarios totales coherentes con ingresos facturados
- Sin movimientos sospechosos

**Riesgo si falla**: discrepancia que SAT puede determinar como ingreso no declarado

### 5. Pagos provisionales

**Verificaciones**:
- Cálculo correcto según régimen
- Retenciones acreditadas correctamente
- Pagado en plazo (día 17)
- Si extemporáneo: recargos + actualización aplicados

**Riesgo si falla**: SAT cobra diferencias + recargos

## Reporte ejecutivo

```
🔍 AUDITORÍA FISCAL MENSUAL — Cliente: ABC SA de CV
   Periodo: marzo 2026 | Régimen: RESICO PM

RIESGO GLOBAL: 🟡 MEDIO

Hallazgos:
1. ⚠ ALTO: 3 CFDIs de Proveedor X que está en 69-B DEFINITIVO
   - Monto a EXCLUIR de deducibles: $87,500
   - Impacto: +$14,000 en ISR estimado
   - Acción: refacturar con proveedor alternativo si posible
   
2. ⚠ MEDIO: 8 CFDIs tipo I PPD sin REP correspondiente
   - Plazo cumplido en 6, retraso en 2 (15+ días)
   - Acción: emitir REP retrasados YA
   
3. ✅ BAJO: Retenciones REPSE bien aplicadas a 3 subcontratistas
   
4. ✅ BAJO: Sin depósitos en efectivo > $15k

5. ⚠ MEDIO: Pago provisional febrero pagado el día 18 (1 día tarde)
   - Recargo aplicable: $245
   - Acción: pagar diferencia para evitar acumulación
```

## Validación pendiente

⚠ Reglas pueden cambiar con RMF anual. Validar contra portal SAT vigente.
⚠ Lista 69-B se actualiza semanal — usar fuente fresca.
