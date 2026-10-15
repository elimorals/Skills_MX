---
name: diagnostico-patrimonial-familiar
description: Inventario del patrimonio del titular (inmuebles, acciones de la empresa familiar, cuentas e inversiones, seguros, vehículos, arte) con valuación, costo fiscal, régimen matrimonial, deudas y patrimonio neto; base para planear testamento, donaciones o protocolo familiar. Usar cuando el usuario diga diagnóstico patrimonial familiar, diagnostico_patrimonial_familiar, inventario de bienes, cuánto vale mi patrimonio, patrimonio neto, ayuda con diagnóstico patrimonial familiar.
allowed-tools: Read, Write
---

# Diagnóstico patrimonial familiar

## Qué capturar por activo

| Campo | Por qué importa |
|---|---|
| Tipo y descripción | Inmueble, acciones/partes sociales, cuenta, inversión, seguro, vehículo, arte |
| Titularidad y % | Solo se planea lo que es del titular |
| Régimen matrimonial | Sociedad conyugal: la mitad de los bienes comunes es del cónyuge |
| Valor de mercado | Avalúo (inmuebles), valor contable o avalúo (acciones), estado de cuenta |
| Costo fiscal y fecha de adquisición | Se transmite al heredero/donatario (Art. 124 LISR); define el ISR si luego vende |
| Gravámenes y deudas | Hipotecas, créditos, avales |
| Beneficiarios designados | Seguros, cuentas bancarias, Afore: pasan fuera del testamento |
| Ubicación | Entidad federativa (impuestos locales) o extranjero |

## Cálculo

```python
patrimonio_bruto = sum(a.valor * a.pct_titular for a in activos)
parte_conyuge = sum(a.valor * a.pct_titular * D("0.5") for a in activos if a.bien_comun_sociedad_conyugal)
patrimonio_neto_titular = patrimonio_bruto - parte_conyuge - sum(deudas)
```

Ejemplo: casa $4,000,000 (común, sociedad conyugal) + acciones $6,000,000 (propias, adquiridas antes del matrimonio) − hipoteca $1,000,000 → bruto 10,000,000; parte cónyuge 2,000,000; neto del titular **$7,000,000**.

## Output esperado

```json
{
  "operation": "diagnostico-patrimonial-familiar",
  "data": {
    "patrimonio_bruto_mxn": "10000000.00",
    "parte_conyuge_mxn": "2000000.00",
    "deudas_mxn": "1000000.00",
    "patrimonio_neto_titular_mxn": "7000000.00",
    "activos_sin_costo_fiscal_documentado": 1,
    "activos_con_beneficiario_designado": ["seguro de vida", "Afore"]
  },
  "vigencia_validada": false
}
```

## Casos edge

- Sin escrituras o facturas de adquisición: márcalo; sin costo comprobado el ISR futuro puede ser mayor.
- Acciones sin libro de registro actualizado: alerta legal.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (RFC, mxn-formato); tracker local
- Siguientes pasos: `plan-testamentario-distribucion`, `simulador-donacion-vs-herencia`, `protocolo-familiar-template`

Valuaciones orientativas: confirma con valuador, notario y contador.
