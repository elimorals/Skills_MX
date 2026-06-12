---
name: programacion-pagos-batch
description: Prepara batch de pagos del mes (CFE + agua + predial + gas) para que el usuario pague todo en una sesión bancaria. Genera lista de líneas de captura, monto, fecha vence. NO ejecuta el pago (usuario paga desde su banca). Usar cuando el usuario diga pagar servicios del mes, batch pagos, todo junto.
allowed-tools: Read, Write
---

# Programación pagos batch

## Output

```
💳 BATCH PAGOS — Mes Junio 2026

| Servicio    | Monto    | Vence       | Línea captura  |
|-------------|----------|-------------|----------------|
| CFE         | $4,250   | 2026-06-18  | ...            |
| Agua        | $  850   | 2026-06-25  | ...            |
| Gas natural | $  620   | 2026-06-15  | ...            |
| Predial     | Pagado   | -           | -              |
|             |          |             |                |
| TOTAL       | $5,720   |             |                |

→ Abre tu banca electrónica y paga en secuencia (deadline más próximo primero)
→ Confirmar todos antes de cerrar este mes
```
