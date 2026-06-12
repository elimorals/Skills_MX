---
description: Due-diligence completa de cliente nuevo (B2B o PF significativo). Valida RFC, SAT padrón, 69-B EFOS, 69 incumplidos, Buró opcional. Genera score 0-100 + decisión.
argument-hint: "[nombre y RFC del cliente + monto operación]"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /core:due-diligence

Due-diligence cliente: $ARGUMENTS

## Lo que hace

Despacha `workflow-due-diligence-cliente` (en core-mexico/agents/) que coordina:
1. Validación local RFC
2. SAT padrón + 69-B + 69 (paralelo)
3. CSF (si tienes credenciales)
4. Buró de Crédito (si autorizado por cliente)
5. Validación de dirección
6. Score final 0-100 + categoría riesgo + decisión

## Output esperado

```
✓ Due-diligence — Cliente Demo SA de CV

Score:          78 / 100
Categoría:      RIESGO MEDIO
Decisión:       ACEPTAR CON CONDICIONES

Fases:
  ✓ RFC válido
  ✓ Padrón SAT: ACTIVO
  ✓ 69-B EFOS: NO aparece
  ✓ 69 Incumplidos: NO aparece
  ✓ CSF descargada
  ✓ Buró: 685 (bueno)
  ✓ Dirección coherente

Condiciones sugeridas:
  • Anticipo 50% antes de servicio
  • Contrato con cláusula cancelación primer impago
  • Revisión semestral status fiscal

⚠ Alertas:
  • Empresa < 2 años de operación — riesgo moderado
  • Obligaciones recientes IVA+ISR al corriente
```

⚠ Para Buró requiere autorización formal del cliente (Art. 32 LFPDPPP + LRSIC).
