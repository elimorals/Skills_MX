---
name: riesgo-carf-2026
description: Evalúa qué tan visibles son para el SAT los saldos y operaciones cripto del usuario hoy (requerimientos a exchanges, avisos de actividades vulnerables, depósitos bancarios de retiros) y cuando entre el CARF de la OCDE (Marco de Reporte de Criptoactivos), al que México se comprometió con intercambio previsto desde 2027. Prioriza qué declarar. Usar cuando el usuario diga CARF, el SAT sabe de mis cripto, Bitso reporta al SAT, reporte del exchange al SAT, intercambio de información cripto, me van a auditar por bitcoin.
allowed-tools: Read, Write
---

# Riesgo CARF 2026

## Estado al 2026-10-15

- **CARF (Crypto-Asset Reporting Framework, OCDE)**: México firmó la declaración conjunta de noviembre de 2023; el primer intercambio entre países se prevé para 2027 (información de 2026). **Verificar**: al texto vigente del CFF (Cámara de Diputados, última reforma DOF 09-04-2026) no se le ha incorporado una obligación CARF; fuentes secundarias no coinciden en la fecha de arranque (confianza media).
- **Lo que ya existe hoy**:
  - Intercambio de activos virtuales es **actividad vulnerable** (Art. 17 fr. XVI LFPIORPI): los exchanges identifican a sus clientes y presentan avisos a la UIF/SAT por operaciones que rebasan el umbral de la ley (umbral exacto: **verificar** en el texto vigente).
  - El SAT puede requerir información a cualquier exchange con operaciones en México (Art. 42 CFF).
  - Los retiros a tu cuenta bancaria son depósitos que el SAT puede cruzar contra tu declaración (discrepancia fiscal, Art. 91 LISR; depósitos en efectivo > $15,000/mes se informan por Art. 55 fr. IV LISR).
  - Exchanges extranjeros: con CARF, su información llegará vía intercambio; mientras tanto, CRS (Art. 32-B Bis CFF) solo cubre cuentas financieras, no necesariamente cripto.

No existe un umbral público tipo "Bitso reporta saldos > $X": no prometas al usuario que debajo de una cifra no hay reporte.

## Riesgo de no declarar

- ISR omitido + actualización + recargos (Arts. 17-A y 21 CFF)
- Multa de 55% a 75% del impuesto omitido (Art. 76 CFF); menor si se autocorrige (Art. 76 CFF)
- Discrepancia fiscal si los retiros a bancos superan lo declarado

## Algoritmo

1. Listar exchanges y wallets (`importar-operaciones-exchange`, `tracking-wallets-self-custody`).
2. Marcar visibilidad: exchange mexicano (alta, hoy), exchange extranjero en jurisdicción CARF (alta desde 2027), self-custody sin rampa fiat (baja, pero trazable al salir a fiat).
3. Sumar retiros a cuentas bancarias del año vs ingresos declarados.
4. Recomendar declarar todas las enajenaciones del ejercicio (`calculadora-isr-cripto-detallada`) y, si hay ejercicios previos omitidos, complementarias con contador antes de un requerimiento.

## Output

```json
{
  "rfc_hash": "...",
  "ejercicio": 2026,
  "exchanges": [
    {"exchange": "bitso", "jurisdiccion": "MX", "visibilidad_sat_hoy": "alta", "saldo_cierre_mxn": "312000.00"},
    {"exchange": "binance", "jurisdiccion": "extranjero", "visibilidad_sat_hoy": "media", "visibilidad_con_carf": "alta (intercambio previsto 2027, verificar)"}
  ],
  "retiros_a_bancos_mxn": "180000.00",
  "riesgo_no_declarar": "ALTO",
  "recomendacion": "Declarar todas las enajenaciones del año en la anual 2026 (vence 30-abr-2027)",
  "vigencia_validada": false
}
```

## ⚠ Compliance

- No es asesoría legal. Validar con contador; en caso de requerimiento del SAT, abogado fiscalista.
- `vigencia_validada: false`.
