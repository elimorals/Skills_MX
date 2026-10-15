---
name: cfdi-donativo-d04
description: Prepara el CFDI de donativo que la donataria autorizada (régimen 603) emite al donante, con complemento Donatarias (número y fecha del oficio de autorización y leyenda), uso CFDI D04 cuando el donante es persona física, y calcula el límite de deducción del donante (7% de ingresos acumulables o utilidad fiscal del ejercicio anterior, Arts. 27 fr. I y 151 fr. III LISR). Usar cuando el usuario diga cfdi donativo d04, cfdi_donativo_d04, recibo deducible de donativo, factura de donativo, comprobante de donación, ayuda con cfdi donativo d04, cuánto puede deducir mi donante.
allowed-tools: Read, Write
---

# CFDI de donativo (D04)

## Antes de emitir

1. Confirma que la donataria aparece como autorizada: `donatarias_consultar` (MCP `mp_donatarias_sat`, directorio SAT validado; no incluye revocaciones posteriores a su corte, revisa también el Anexo 14 RMF vigente).
2. Datos del donante: RFC, nombre y CP como en su CSF, régimen fiscal y si es PF o PM.

## Estructura

| Campo | Valor |
|---|---|
| Tipo | I (ingreso) |
| Emisor régimen | 603 Personas morales con fines no lucrativos |
| Receptor uso CFDI | **D04 Donativos** si es PF que lo deducirá en su anual; PM: el uso que indique (comúnmente G03) |
| Concepto | Donativo en dinero o en especie (descripción y valor) |
| Objeto de impuesto | 01 (no objeto) en donativos en dinero |
| Complemento | **Donatarias 1.1**: `noAutorizacion` (número de oficio), `fechaAutorizacion`, `leyenda` ("El donante no recibe bienes o servicios a cambio del donativo otorgado") |
| Donante sin RFC o anónimo | Receptor genérico XAXX010101000 (no deducible para nadie) |

La base de CFDI 4.0 y catálogos: skill `cfdi-emision` de `core-mexico`. Verifica la versión del complemento en el portal del SAT.

## Deducibilidad para el donante

- **PF** (Art. 151 fr. III LISR): hasta **7% de los ingresos acumulables del ejercicio anterior** (antes de deducciones personales). No entra en el tope global de deducciones personales.
- **PM** (Art. 27 fr. I LISR): hasta **7% de la utilidad fiscal del ejercicio anterior**.
- Donativos a Federación, estados, municipios u organismos descentralizados: máximo 4% dentro del mismo 7%.
- PM: un donativo en dinero > $2,000 debe pagarse por transferencia, cheque nominativo, tarjeta o monedero para ser deducible (Art. 27 fr. III LISR). PF: recomienda pago bancarizado; verificar si la RMF vigente lo exige.

Ejemplo: PF con ingresos acumulables 2025 de $600,000 → tope deducible en 2026: 600,000 × 7% = **$42,000**.

## Output esperado

```json
{
  "operation": "cfdi-donativo-d04",
  "data": {
    "donataria_autorizada_verificada": true,
    "receptor_tipo": "PF",
    "uso_cfdi": "D04",
    "monto_donativo_mxn": "10000.00",
    "complemento": "donat:Donatarias 1.1",
    "tope_deducible_donante_mxn": "42000.00"
  },
  "vigencia_validada": false
}
```

## Casos edge

- Donativo en especie: valúa al costo o valor de mercado según el bien; el donante solo deduce si cumple requisitos (bienes de inversión, inventarios, Art. 27 y 31 RLISR — verificar).
- Donativo con contraprestación (rifa, cena con precio): no es donativo deducible en la parte que recibe algo a cambio.
- Donativo en efectivo > $100,000: además, informe al SAT (skill `reporte-mensual-efectivo-100k`).
- Datos incompletos → solicitar al usuario. Sin credenciales del PAC → modo mock: no timbra.

## Dependencias

- `core-mexico` (`cfdi-emision`, `rfc-validacion`, `mxn-formato`)
- MCP `mp_donatarias_sat`; tracker local

Validación profesional: confirma con el contador de la donataria antes de timbrar.
