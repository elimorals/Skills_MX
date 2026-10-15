---
name: dashboard-poliza-gmm
description: Status de la póliza GMM del asegurado. Muestra vigencia, suma asegurada, deducible, coaseguro, antigüedad acumulada (importante para excluyentes), usos del año, próxima renovación. Usar cuando el usuario diga status poliza gmm, mi seguro medico, suma asegurada.
allowed-tools: Read, Write
---

# Dashboard póliza GMM

## Output

```
🏥 PÓLIZA GMM — GNP Especial Plus

Vigencia:           2026-09-01 al 2027-08-31
Días restantes:     320

💰 Coberturas:
  Suma asegurada:   $5,000,000 MXN
  Deducible:        $30,000 MXN
  Coaseguro:        10% (después del deducible)
  Tope coaseguro:   $50,000 MXN

📅 Antigüedad acumulada: 7 años (sin enfermedades excluyentes)

🩺 Usos del año:
  Eventos:          2
  Importe pagado por aseguradora: $185,000 MXN
  Suma asegurada restante:        $4,815,000 MXN (si la póliza la agota por padecimiento, calcular por padecimiento)

⚠ Próximos:
  • Renovación en 320 días — a los 90 días, solicitar cotización paralela
  • Prima deducible en la anual (D07) — guarda el CFDI
```

> Los datos salen de la carátula y condiciones generales que el usuario proporciona; la skill no consulta a la aseguradora.
