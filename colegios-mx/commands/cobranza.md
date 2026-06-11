---
description: Siguiente paso de cobranza de colegiatura para una familia específica.
argument-hint: "<familia/matricula>"
allowed-tools: Read, Write, Edit, Bash
---

# /colegios:cobranza

Cobranza para: $ARGUMENTS

1. Invoca `cobranza-colegiaturas`.
2. Lee historial de pagos de la familia.
3. Determina etapa apropiada según mora actual.
4. Genera template específico con datos del alumno, monto, recargo si aplica.
5. Si es etapa 4+, prepara carta formal.
6. Registra el evento en bitácora.
7. Sugiere fecha del siguiente paso si este no funciona.
