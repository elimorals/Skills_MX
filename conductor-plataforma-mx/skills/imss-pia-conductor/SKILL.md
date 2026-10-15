---
name: imss-pia-conductor
description: Orienta al conductor o repartidor de plataforma sobre su seguridad social IMSS en 2026. Explica el aseguramiento obligatorio a cargo de la plataforma tras la reforma a la LFT de trabajo en plataformas digitales (DOF 24-12-2024; operación con el IMSS desde 01-07-2025) cuando el ingreso neto mensual llega al salario mínimo, y la incorporación voluntaria como trabajador independiente cuando no llega. Usar cuando el usuario diga IMSS conductor, ¿Uber me da seguro social?, afiliarme al IMSS, seguro social repartidor, IMSS plataformas digitales, trabajador independiente IMSS, jubilación chofer, semanas cotizadas. NO usar para IMSS patronal de empleados de empresa.
allowed-tools: Read, Write
---

# IMSS para conductores de plataforma

> El nombre "IMSS-PIA" de versiones anteriores no corresponde a un programa oficial. Esta skill cubre las dos vías reales.

## Vía 1 — Aseguramiento por la plataforma (obligatorio)

- Reforma a la LFT (capítulo de trabajo en plataformas digitales, DOF 24-12-2024): la persona que en el mes obtiene un **ingreso neto** igual o mayor a **1 salario mínimo mensual** por plataforma es trabajadora de esa plataforma para efectos de seguridad social.
- El IMSS arrancó el esquema el **01-07-2025** como prueba piloto obligatoria para las plataformas (cuotas calculadas sobre ingreso neto, pago a más tardar el día 17 del mes siguiente). Fuentes secundarias reportan cierre del piloto al 01-01-2026; **verificar** en imss.gob.mx / DOF las reglas vigentes al momento de la consulta.
- Salario mínimo 2026: $315.04 diario general ($440.87 en la zona libre de la frontera norte). Referencia mensual = salario mínimo × días del mes (mismo criterio de "ingreso neto mensual"; **verificar** la fórmula exacta en las reglas IMSS vigentes).
- Si no alcanza el umbral en un mes, la plataforma igual cubre riesgos de trabajo durante el tiempo conectado.
- Qué hacer: pedir a cada app la constancia de alta / NSS; revisar semanas en "Mi IMSS" o el portal del IMSS.

## Vía 2 — Incorporación voluntaria como trabajador independiente

Para quien no alcanza el umbral en ninguna plataforma o quiere cobertura propia:
- Esquema de personas trabajadoras independientes del IMSS (se conoce como Modalidad 44). El trabajador paga sus cuotas sobre el ingreso que registra (mínimo 1 salario mínimo); **no es cuota fija**. Calcular con el simulador del IMSS.
- Incluye: enfermedades y maternidad, riesgos de trabajo, invalidez y vida, retiro, cesantía y vejez (AFORE). **Vivienda (INFONAVIT) no está incluida** en este esquema — verificar si el usuario lo necesita.
- No confundir con Modalidad 40 (continuación voluntaria para quien ya cotizó como empleado).

## Pensión (Ley 1997)

- Semanas mínimas: 750 en 2021 y +25 cada año → **875 semanas en 2026**, hasta llegar a 1,000 en 2031.
- Edad: 60 cesantía en edad avanzada, 65 vejez.

## Cómo afiliarse (humano)

1. Si trabaja en plataformas: confirmar con cada app que lo dio de alta (vía 1).
2. Si es independiente (vía 2): trámite en línea en imss.gob.mx o en subdelegación con CURP, RFC, comprobante de domicilio, identificación y correo.
3. Pagar la cuota por el periodo que elija (mensual/semestral/anual, según el esquema vigente).

## Output (sugerencia / status)

```json
{
  "rfc_hash": "...",
  "ingreso_neto_mensual_por_plataforma_mxn": {"uber": "12442.20", "didi": "6081.30"},
  "salario_minimo_diario_2026_mxn": "315.04",
  "via_sugerida": "plataforma_obligatoria_verificar_alta",
  "semanas_minimas_pension_2026": 875,
  "incluye_infonavit_via_independiente": false,
  "siguiente_paso": "Pedir a Uber constancia de alta IMSS; consultar semanas en el portal del IMSS",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Conductor que también es empleado formal | Ya cotiza por su patrón; la alta por plataforma puede sumarse |
| Ingreso bajo el umbral en todas las apps | Vía 2 voluntaria o seguro de gastos médicos privado |
| Conductor > 60 años | Revisar semanas cotizadas antes de invertir en cuotas voluntarias |
| Cuotas del propio contribuyente como deducción | Tratamiento fiscal no evidente — **verificar con contador** |

## ⚠ Compliance

- Reglas del IMSS para plataformas en evolución: confianza media (fuentes: boletines IMSS 2025 y prensa). Validar en imss.gob.mx antes de recomendar.
- `vigencia_validada: false`.
