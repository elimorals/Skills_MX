---
name: scoring-inquilinos-ia
description: Genera un score de riesgo de inquilino (1-100) para arrendador residencial combinando señales formales (reporte de buró con autorización expresa del candidato, ingresos comprobables de 3x la renta, estabilidad laboral, referencias de arrendadores previos verificadas, CFDI si es freelancer) y señales heurísticas revisadas con prudencia (estado del inmueble actual, información pública, estados de cuenta entregados por el candidato, entrevista escrita). Categoriza en VERDE (80-100), AMARILLO (60-79), NARANJA (40-59) y ROJO (<40). Excluye variables discriminatorias (género, edad, estado civil, origen, religión, orientación). Usar cuando el usuario diga "score inquilino", "evaluar candidato renta", "validar inquilino", "screening renta IA". NO usar para evaluación crediticia formal (eso es buró) ni para empleados.
allowed-tools: Read, Write, Edit
---

# Scoring de inquilinos con IA

## Señales del score

### Señales formales (peso 60% del score)

| Señal | Validación | Peso |
|---|---|---|
| Buró de crédito | Reporte de crédito con autorización expresa (Art. 28 LRSIC); `mp_buro_credito_personal` es mock | 20% |
| Ingresos 3x renta | Recibos nómina o estado cuenta | 15% |
| Estabilidad laboral | Mínimo 1 año en empleo | 10% |
| Referencia arrendador anterior | Llamada verificada | 10% |
| Antecedentes penales | Constancia no antecedentes | 5% |

### Señales heurísticas (peso 40%)

| Señal | Cómo se mide | Peso |
|---|---|---|
| Cuidado del inmueble previo | Foto de dónde vive ahora | 10% |
| Redes sociales público | Solo lo público, LFPDPPP | 10% |
| Patrón de pago bancario | Estados de cuenta entregados por el candidato (`mp_bancos_mx` es esqueleto) | 10% |
| Entrevista escrita | Análisis de red flags | 10% |

## Categorías y recomendaciones

| Score | Color | Recomendación arrendador |
|---|---|---|
| 80-100 | VERDE | Aceptar con depósito 1 mes |
| 60-79 | AMARILLO | Requiere aval con propiedad o depósito 2 meses + co-firmante |
| 40-59 | NARANJA | Solo con seguro de renta + aval + depósito 3 meses |
| 0-39 | ROJO | NO recomendar aceptar |

## Variables que NO se usan (anti-discriminación)

🚫 Género, edad, estado civil, raza, religión, orientación sexual, lugar de origen, nacionalidad (salvo trámite migratorio), embarazo, discapacidad no relacionada con vivienda.

## Output

```yaml
candidato_rfc_hash: ABC...
score_total: 76
categoria: AMARILLO
desglose:
  formales: 45/60
  heuristicas: 31/40
recomendacion: "Aceptar con aval con propiedad O depósito de 2 meses"
red_flags_detectados:
  - "Solo 8 meses en empleo actual"
  - "Buró: 1 atraso 30 días hace 18 meses (resuelto)"
fortalezas:
  - "Ingreso de $45k vs renta $12k = 3.75x"
  - "Referencia anterior arrendador: 'inquilino impecable 3 años'"
```

## Validación pendiente

⚠ Algoritmo IA requiere validación legal LFPDPPP + Ley Federal contra Discriminación.
⚠ Usar solo con autorización expresa del candidato y aviso de privacidad que mencione el análisis automatizado.
⚠ La decisión final es humana: el score es apoyo, no sustituye la revisión.
