---
name: plan-testamentario-distribucion
description: Arma una propuesta de distribución de bienes entre herederos y legatarios según los objetivos del titular, bajo el principio de libre testamentación del derecho civil mexicano (sin legítima obligatoria en el Código Civil Federal y la mayoría de los estados) con la obligación de dejar alimentos a quienes tienen derecho, y señala efectos fiscales (herencia exenta de ISR, costo fiscal heredado). Prepara el borrador para revisar con notario. Usar cuando el usuario diga plan testamentario distribución, plan_testamentario_distribucion, hacer mi testamento, repartir mis bienes, a quién le dejo la empresa, legítima, testamento público abierto, ayuda con plan testamentario distribución.
allowed-tools: Read, Write
---

# Plan testamentario de distribución

## Marco civil (verificar código civil de la entidad del titular)

- **Libre testamentación**: el testador puede disponer de sus bienes como quiera; no existe en el Código Civil Federal una "legítima" del 50% para hijos.
- **Límite**: debe dejar **alimentos** a quienes tienen derecho (descendientes menores o incapaces, cónyuge o concubina/o que lo necesite, ascendientes dependientes, etc.; Art. 1368 CCF y equivalentes estatales). Si no lo hace, el testamento es **inoficioso** en esa parte.
- Algunas entidades pueden tener reglas propias: confirma con el notario de la entidad.
- Régimen matrimonial: en **sociedad conyugal**, solo se hereda la parte del titular (normalmente 50% de los bienes comunes); en separación de bienes, lo propio.
- Tipos usuales: **testamento público abierto** ante notario. Septiembre es "mes del testamento" con descuentos en muchas entidades (verificar cada año).
- Sin testamento: sucesión legítima (intestamentaria) conforme al orden legal; más lenta y sin elección del titular.

## Pasos

1. Inventario y valuación (skill `diagnostico-patrimonial-familiar`).
2. Determinar la porción disponible: patrimonio del titular − parte del cónyuge en sociedad conyugal − reserva para alimentos.
3. Objetivos del titular: continuidad de la empresa, equidad entre hijos, protección del cónyuge, beneficencia.
4. Asignar bienes concretos (legados) y remanente (herencia) a cada persona; nombrar albacea y sustitutos.
5. Revisar efectos fiscales: herencia exenta de ISR (Art. 93 fr. XXII LISR); el heredero conserva el costo fiscal del titular (Art. 124); impuestos locales de traslado (verificar). Acciones de la empresa: revisar estatutos (derecho de preferencia, cláusulas de admisión) y protocolo familiar.
6. Seguro de vida con beneficiarios para liquidez de la sucesión.

## Output esperado

```json
{
  "operation": "plan-testamentario-distribucion",
  "data": {
    "regimen_matrimonial": "sociedad_conyugal",
    "patrimonio_titular_mxn": "<de diagnostico>",
    "reserva_alimentos": "<monto o bienes>",
    "asignaciones": [
      {"beneficiario": "hijo_1", "bienes": ["acciones 51% Empresa SA"], "valor_mxn": "<>"},
      {"beneficiario": "hijo_2", "bienes": ["inmueble Querétaro"], "valor_mxn": "<>"}
    ],
    "albacea": "<nombre>",
    "alertas": ["estatutos con derecho de preferencia"]
  },
  "vigencia_validada": false
}
```

## Casos edge

- Hijos menores: nombrar tutor y considerar fideicomiso para administrar sus bienes.
- Bienes en otra entidad o país: el testamento puede requerir trámites adicionales; derivar.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (RFC, mxn-formato); skills `diagnostico-patrimonial-familiar`, `simulador-donacion-vs-herencia`

⚠ Es un borrador de planeación, no un testamento. Debe otorgarse ante notario y revisarse con abogado.
