---
name: acreditacion-iva-importacion
description: Revisa si el IVA pagado en una importación es acreditable y en qué mes, con base en el pedimento - requisitos del Art. 5 LIVA, IVA virtual de empresas IMMEX con certificación IVA/IEPS (Art. 28-A LIVA) y papeles de soporte. Usar cuando el usuario diga acreditacion iva importacion, acreditar IVA del pedimento, IVA de aduana, recuperar IVA de importación, certificación IVA IEPS, crédito fiscal IMMEX.
allowed-tools: Read, Write
---

# Acreditación de IVA de importación

El IVA de importación no se acredita "en el próximo CFDI": se acredita en la declaración mensual de IVA del mes en que se pagó efectivamente en la aduana. El documento soporte es el **pedimento** (no un CFDI del proveedor extranjero). Orientativo; requiere validación del contador.

## Requisitos a revisar (Art. 5 LIVA)

1. El pedimento está a nombre del contribuyente (RFC del importador) y el IVA consta pagado (forma de pago y fecha en el pedimento).
2. La mercancía es estrictamente indispensable para la actividad y su gasto/inversión es deducible para ISR.
3. Se acredita en el mes del pago; si actividades gravadas y exentas se mezclan, aplica la proporción del Art. 5 fr. V.
4. Los servicios del agente aduanal, flete nacional, maniobras y almacenaje traen su propio CFDI con IVA trasladado: ese IVA se acredita por separado con los requisitos normales.
5. Conservar el expediente electrónico que exige la reforma a la Ley Aduanera vigente desde 01-ene-2026 (CFDI, comprobantes de pago, contratos, manifestación de valor).

## IMMEX y certificación IVA/IEPS

En importación temporal, las empresas con certificación en materia de IVA e IEPS obtienen un crédito fiscal equivalente al 100% del IVA (Art. 28-A LIVA; reglas 7.x RGCE 2026): no hay desembolso. Sin certificación, deben pagar el IVA o garantizarlo (fianza/carta de crédito). Si la mercancía cambia a definitiva (clave F4/F5) o se vence el plazo de retorno, el IVA se causa.

## Output esperado

```json
{
  "operation": "acreditacion-iva-importacion",
  "data": {"pedimento": "", "fecha_pago": "", "iva_pagado": 0, "mes_acreditamiento": "", "requisitos_faltantes": []},
  "vigencia_validada": false
}
```

## Casos edge

- Pedimento a nombre de un tercero (comercializadora, courier) → el IVA no es acreditable para el usuario; lo acredita el importador de registro.
- Pagos de IVA con crédito fiscal (IMMEX certificada) → no hay IVA acreditable en efectivo; no lo dupliques.
- Importaciones por paquetería con pedimento simplificado → revisar que salga a nombre del usuario.
- Datos incompletos → solicitar el pedimento (número de 15 dígitos, aduana, patente).

## Dependencias

- `core-mexico` (iva-retenciones-mx, mxn-formato)
