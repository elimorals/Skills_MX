---
name: auditor-fiscal-pyme-mensual
description: Revisión fiscal preventiva mensual de clientes PyME del despacho - CFDI PPD sin complemento de pago (REP) a más tardar el día 5 del mes siguiente, retenciones (REPSE 6%, honorarios, RESICO, arrendamiento), gastos sin CFDI o de proveedores en lista 69-B definitiva, depósitos en efectivo mayores a $15,000 informados por bancos, discrepancia fiscal y pagos provisionales tardíos. Genera reporte con riesgo bajo/medio/alto, acciones y estimación de impacto. Cubre PFAE 612, RESICO 626 (PF y PM) y PM 601. Usar cuando el usuario diga auditoría fiscal mensual, revisión SAT preventiva, auditor contable, análisis fiscal PyME, validar declaración mensual, revisar cliente antes del 17. NO usar para la declaración anual de PF (usar el plugin pf-anual-mx) ni para defensa en una auditoría del SAT ya iniciada.
allowed-tools: Read, Write, Edit
---

# Auditoría fiscal mensual preventiva

## Categorías de revisión

### 1. CFDIs emitidos del mes

**Verificaciones**:
- Total emitido = Total reportado
- CFDIs PPD tienen REP (complemento de pago) emitido a más tardar el **día 5 natural del mes siguiente** al cobro (regla de CFDI de pagos de la RMF 2026; verificar número de regla)
- CFDIs cancelados con motivo correcto (01-04) + sustituto si aplica
- Sin duplicados

**Riesgo si falla**: contingencia con SAT por discrepancia entre lo emitido y lo reportado.

### 2. CFDIs recibidos del mes

**Verificaciones**:
- Cada gasto deducible tiene CFDI a tu RFC
- RFC emisor NO en lista 69-B definitiva (si lo está, EXCLUIR de deducibles e IVA acreditable). Consulta con `sat_consultar_69b_efos` (MCP `mp_sat_portal`, validado en vivo)
- Método de pago consistente con forma real
- Plazo de cancelación SAT cumplido (por regla general requiere aceptación del receptor; sin aceptación solo en supuestos de la regla 2.7.1.35 RMF 2026, p.ej. dentro de 24 h o total ≤ $1,000)

**Riesgo si falla**: gastos no deducibles → mayor base gravable → mayor ISR

### 3. Retenciones

**Verificaciones**:
- REPSE: retención de IVA del 6% del valor de la contraprestación (Art. 1-A fr. IV LIVA)
- Honorarios de PF pagados por PM: 10% ISR + 2/3 del IVA (10.6667%)
- RESICO PF que factura a PM: 1.25% ISR + 2/3 del IVA
- Arrendamiento de PF pagado por PM: 10% ISR + 2/3 del IVA
- CFDI de Retenciones e información de pagos emitido por cada retención (ver skill `iva-retenciones-mx` de `core-mexico`)

**Riesgo si falla**: SAT puede negar deducibilidad y aplicar multa

### 4. Cruce bancario

**Verificaciones**:
- Depósitos en efectivo > $15,000 MXN en el mes: los bancos los informan al SAT (Art. 55 fr. IV LISR)
- Erogaciones mayores a ingresos declarados (PF): riesgo de discrepancia fiscal (Art. 91 LISR)
- Depósitos bancarios totales coherentes con ingresos facturados
- Sin movimientos sospechosos

**Riesgo si falla**: discrepancia que SAT puede determinar como ingreso no declarado

### 5. Pagos provisionales

**Verificaciones**:
- Cálculo correcto según régimen
- Retenciones acreditadas correctamente
- Pagado en plazo (día 17 del mes siguiente; las PF pueden tener 1 a 5 días hábiles adicionales según el sexto dígito numérico de su RFC, por decreto de beneficios fiscales; verificar vigencia)
- Si extemporáneo: actualización + recargos por **mes o fracción** (Art. 21 CFF): un día de atraso ya causa un mes de recargos

**Riesgo si falla**: SAT cobra diferencias + recargos

## Reporte ejecutivo

```
🔍 AUDITORÍA FISCAL MENSUAL — Cliente: ABC SA de CV
   Periodo: marzo 2026 | Régimen: RESICO PM

RIESGO GLOBAL: 🟡 MEDIO

Hallazgos:
1. ⚠ ALTO: 3 CFDIs de Proveedor X que está en 69-B DEFINITIVO
   - Monto a EXCLUIR de deducibles: $87,500 (subtotal)
   - Impacto estimado: +$26,250 ISR (30% PM) y $14,000 de IVA no acreditable (16%)
   - Acción: excluir de la deducción y del IVA acreditable; documentar materialidad si el cliente quiere desvirtuar (Art. 69-B CFF)
   
2. ⚠ MEDIO: 8 CFDIs tipo I PPD sin REP correspondiente
   - Plazo cumplido en 6, retraso en 2 (15+ días)
   - Acción: emitir REP retrasados YA
   
3. ✅ BAJO: Retenciones REPSE bien aplicadas a 3 subcontratistas
   
4. ✅ BAJO: Sin depósitos en efectivo > $15k

5. ⚠ MEDIO: Pago provisional febrero pagado el día 18 (1 día tarde)
   - Recargo aplicable: 1 mes de recargos sobre el impuesto actualizado (tasa mensual de la LIF 2026)
   - Acción: pagar actualización y recargos con declaración complementaria
```

## Validación pendiente

⚠ Reglas pueden cambiar con RMF anual. Validar contra portal SAT vigente.
⚠ La lista 69-B se actualiza periódicamente — consulta la versión del día.
⚠ Es una revisión preventiva, no un dictamen: el contador responsable valida cada hallazgo.
