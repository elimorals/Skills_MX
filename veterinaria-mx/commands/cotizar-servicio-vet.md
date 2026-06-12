---
description: Cotiza un servicio veterinario (consulta, cirugía, hospitalización, etc.) con desglose de costos directos, margen y recargos aplicables.
argument-hint: "[servicio, peso mascota opcional, urgencia opcional]"
allowed-tools: Read, Write, Edit
---

# /vet:cotizar-servicio-vet

Cotiza servicio veterinario: $ARGUMENTS

## Lo que hace

1. Invoca skill `tarifario-servicios-vet` para precio base.
2. Aplica ajustes por peso (>10kg, >25kg, >40kg) si cirugía.
3. Aplica recargo nocturno / sábado / domingo / urgencia 24h si aplica.
4. Sugiere exámenes preoperatorios cuando corresponda.
5. Desglose: cobrar al tutor + costos directos + margen.

## Output esperado

```
✓ Cotización — Esterilización Luna (28.5 kg)

Servicio base:             $3,500 MXN
Ajuste peso (10-25 kg):    +$700  (+20%)
─────────────────────────────────
Subtotal cirugía:          $4,200 MXN

Exámenes preoperatorios sugeridos:
  • Hemograma completo:       $350
  • Química sanguínea básica: $550
  • Subtotal exámenes:        $900

Total estimado:             $5,100 MXN

Incluye:
  ✓ Cirugía + anestesia
  ✓ Hospitalización 1 día
  ✓ Antibiótico post-op

NO incluye:
  • Collar isabelino:           ~$150
  • Visita retiro puntos:       ~$300

Fecha recomendada: antes del primer celo (8-10 meses)
Ayuno: 12 horas antes
```
