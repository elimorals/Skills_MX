---
name: comparador-incoterms
description: Compara costos y riesgos por INCOTERM 2020 (EXW, FCA, FOB, CFR, CIF, CPT, CIP, DAP, DPU, DDP) para una importación a México - quién paga flete, seguro, despacho e impuestos, y cómo cambia el valor en aduana. Usar cuando el usuario diga comparador incoterms, FOB vs CIF, conviene EXW o DDP, quién paga el flete, términos de compra internacional, incoterm.
allowed-tools: Read, Write
---

# Comparador INCOTERMS

Versión vigente: **INCOTERMS 2020** (ICC). Si el contrato cita otra versión, se aplica la que diga el contrato.

## Reglas clave

| Incoterm | Vendedor entrega | Riesgo pasa al comprador | Flete principal | Seguro | Despacho importación MX |
|---|---|---|---|---|---|
| EXW | En su planta | En su planta | Comprador | Comprador | Comprador |
| FCA | Al transportista del comprador | En la entrega | Comprador | Comprador | Comprador |
| FOB (solo marítimo) | A bordo en puerto de origen | A bordo | Comprador | Comprador | Comprador |
| CFR (solo marítimo) | A bordo | A bordo | Vendedor | Comprador | Comprador |
| CIF (solo marítimo) | A bordo | A bordo | Vendedor | Vendedor (cobertura mínima) | Comprador |
| CPT / CIP | Al primer transportista | En la entrega | Vendedor | CIP: vendedor (cobertura amplia) | Comprador |
| DAP / DPU | En destino (DPU: descargado) | En destino | Vendedor | Vendedor (de facto) | Comprador |
| DDP | En destino, despachado | En destino | Vendedor | Vendedor | Vendedor |

## Implicaciones en México

- El valor en aduana incluye flete y seguro hasta el lugar de entrada a México (Art. 65 Ley Aduanera): con EXW/FCA/FOB súmalos; con CIF/CFR ya vienen en el precio.
- **DDP**: el vendedor extranjero necesitaría importar a su nombre (padrón de importadores, RFC); en la práctica suele hacerlo vía un tercero, y el comprador no puede acreditar ese IVA. Advertirlo.
- EXW obliga al comprador a exportar desde origen: útil solo con agente de carga en origen.
- Usa `cotizador-pre-importacion` para el landed cost con cada opción.

## Output esperado

```json
{
  "operation": "comparador-incoterms",
  "data": {"opciones": [{"incoterm": "", "precio": 0, "flete": 0, "seguro": 0, "valor_aduana": 0, "landed_cost": 0, "riesgo_comprador": ""}]},
  "vigencia_validada": false
}
```

## Casos edge

- Carga aérea o contenedor multimodal con FOB/CIF → recomendar FCA/CIP (FOB/CIF son solo marítimos).
- Faltan cotizaciones de flete → pedirlas; no inventar montos.

## Dependencias

- `core-mexico` (mxn-formato, tipo de cambio Banxico)
