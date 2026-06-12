---
name: imss-pia-conductor
description: Programa IMSS-PIA (Programa Incorporación Anticipada) — opción voluntaria para conductores de plataforma (y otros trabajadores independientes) de afiliarse al IMSS con tarifa fija mensual. Da acceso a servicios médicos del IMSS + cuenta de retiro AFORE + crédito INFONAVIT (tras antigüedad). Cuota mensual fija independiente del ingreso. Usar cuando el usuario diga IMSS conductor, afiliarme al IMSS, seguro social independiente, IMSS-PIA, jubilación chofer. NO usar para IMSS-patronal (eso es empleados de empresa).
allowed-tools: Read, Write
---

# IMSS-PIA — conductor de plataforma

## Qué es

Modalidad de aseguramiento voluntario al IMSS para trabajadores independientes (incluidos conductores Uber/DiDi/etc.). Establecida en 2021 para cubrir el gap de cobertura social en plataformas digitales.

## Beneficios

- **Salud**: acceso a clínicas + medicamentos IMSS (igual que empleado formal)
- **Maternidad/paternidad**: cobertura completa
- **Riesgos de trabajo**: cobertura si accidente en horario laboral
- **Retiro**: aporte a AFORE
- **INFONAVIT**: tras antigüedad, posibilidad de crédito hipotecario
- **Pensión**: si cotizas 1,250 semanas (~25 años) tienes pensión por edad avanzada

## Cuota mensual (referencia 2026 — VALIDAR vigencia)

**Cuota fija** (no proporcional al ingreso): ~$1,700-$2,200 MXN/mes (varía por reglas IMSS).

Cubre todos los seguros: enfermedades, maternidad, invalidez, vida, retiro, cesantía, vejez.

## Cómo afiliarse (humano)

1. Acudir a una subdelegación del IMSS con:
   - CURP
   - Comprobante de domicilio
   - RFC con homoclave
   - Identificación oficial
2. Llenar solicitud Modalidad 44 (Continuación Voluntaria) o equivalente
3. Cubrir primera mensualidad
4. Recibir NSS (Número de Seguridad Social) si no se tiene

## Output (sugerencia / status)

```json
{
  "rfc_hash": "...",
  "esta_afiliado": false,
  "modalidad_recomendada": "44_continuacion_voluntaria",
  "cuota_mensual_estimada_mxn": "1950.00",
  "beneficios_proyectados": [
    "Atención médica IMSS",
    "Aporte AFORE retiro",
    "Posibilidad crédito INFONAVIT tras 1,030+ semanas",
    "Pensión por edad avanzada tras 1,250+ semanas (~25 años)"
  ],
  "ahorro_vs_gastos_medicos_anuales_mxn": "12000.00",
  "comparativa_seguro_privado": {
    "gmm_basico_anual_mxn": "9000.00",
    "imss_pia_anual_mxn": "23400.00",
    "recomendacion": "GMM básico si solo necesitas salud, IMSS-PIA si quieres retiro + salud"
  },
  "deducible_ISR_si_RESICO": false,
  "deducible_ISR_si_PFAE": true,
  "siguiente_paso": "Agendar cita en https://www.imss.gob.mx/citas",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Conductor que también trabaja como empleado | IMSS ya está incluido vía empleador — no necesita PIA |
| Conductor con servicios médicos privados (Pemex, Sedena) | Evaluar duplicación |
| Conductor < 18 años | No aplica (mayor de edad requerido) |
| Conductor > 60 años | Aplica, pero pensión requiere semanas mínimas |

## ⚠ Compliance

- Cuotas IMSS-PIA cambian anualmente (revisar SBC vigente)
- Programa puede cambiar nombre/estructura — validar contra IMSS vigente
- `vigencia_validada: false` — confirmar antes de afiliarse
