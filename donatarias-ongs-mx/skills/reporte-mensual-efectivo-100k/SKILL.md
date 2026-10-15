---
name: reporte-mensual-efectivo-100k
description: Detecta y prepara el informe mensual al SAT de donativos recibidos en efectivo (moneda nacional o extranjera) o en piezas de oro o plata mayores a $100,000, a más tardar el día 17 del mes siguiente (Art. 82 fr. VII LISR), y revisa por separado los umbrales antilavado de la LFPIORPI para donativos (identificación 1,605 UMA, aviso 3,210 UMA). Usar cuando el usuario diga reporte mensual efectivo 100k, reporte_mensual_efectivo_100k, donativo en efectivo, informe de donativos en efectivo, aviso antilavado donataria, actividad vulnerable donativos, ayuda con reporte mensual efectivo 100k.
allowed-tools: Read, Write
---

# Reporte mensual de donativos en efectivo > $100,000

## 1. Obligación fiscal (Art. 82 fr. VII LISR)

- Qué: donativos recibidos **en efectivo** (MXN o divisa) o en **piezas de oro o plata** cuyo monto sea **superior a $100,000**.
- Cuándo: a más tardar el **día 17 del mes inmediato posterior** a la operación.
- Cómo: por el medio y formato que señale el SAT en la RMF 2026 (ficha de trámite del Anexo 2; la numeración cambió en 2026: verificar ficha vigente).
- Omitirlo es incumplimiento de requisito de la autorización: puede llevar a revocación o no renovación (Art. 82 penúltimo párrafo LISR).

Criterio prudente: evalúa cada donativo y también la suma por donante en el mes; documenta el criterio que usas y confírmalo con el contador.

## 2. Prevención de lavado (LFPIORPI) — obligación distinta

Recibir donativos es actividad vulnerable (Art. 17 fr. XIII LFPIORPI), sin importar la forma de pago:

| Umbral | UMA | Monto 2026 (UMA $117.31) | Obligación |
|---|---|---|---|
| Identificación | 1,605 | $188,282.55 | Integrar expediente del donante |
| Aviso a la UIF/SAT | 3,210 | $376,565.10 | Aviso en el portal del SAT antilavado a más tardar el día 17 del mes siguiente |

Los montos se acumulan por donante en 6 meses (verificar regla de acumulación en el Reglamento LFPIORPI). Recuerda que enero usa la UMA 2025 ($113.14).

## Algoritmo

```python
def revisar_mes(donativos: list[dict]) -> dict:
    efectivo = [d for d in donativos if d["forma"] in ("efectivo", "divisa", "oro", "plata") and d["monto"] > 100_000]
    pld_ident = [d for d in donativos if d["monto_acum_6m_donante"] >= 1605 * UMA]
    pld_aviso = [d for d in donativos if d["monto_acum_6m_donante"] >= 3210 * UMA]
    return {"informe_sat_82_vii": efectivo, "pld_identificacion": pld_ident, "pld_aviso": pld_aviso}
```

## Output esperado

```json
{
  "operation": "reporte-mensual-efectivo-100k",
  "data": {
    "periodo": "2026-09",
    "donativos_efectivo_mayores_100k": 1,
    "deadline_informe_sat": "2026-10-19",
    "pld_identificacion_requerida": 1,
    "pld_aviso_requerido": 0
  },
  "vigencia_validada": false
}
```

El 17-oct-2026 cae en sábado: el plazo se corre al siguiente día hábil, lunes 19 (Art. 12 CFF).

## Casos edge

- Donativo en efectivo sin identificar al donante: no expidas CFDI nominativo sin datos; integra expediente antes.
- Datos incompletos → solicitar al usuario. Modo mock por default si no hay credenciales.

## Dependencias

- `core-mexico` (CFDI, RFC, mxn-formato)
- Tracker local de donativos

Valida con el contador y el oficial de cumplimiento de la donataria.
