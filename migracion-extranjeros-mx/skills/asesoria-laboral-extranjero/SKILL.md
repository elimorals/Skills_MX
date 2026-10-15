---
name: asesoria-laboral-extranjero
description: Guía sobre permisos para trabajar y obligaciones fiscales de extranjeros en México. Cubre permiso para trabajar del residente temporal con oferta de empleo (empleador con Constancia de Inscripción de Empleador), residente permanente (puede trabajar), visitante con permiso para actividades remuneradas, aviso de cambio de empleador al INM (90 días), residencia fiscal (Art. 9 CFF: casa habitación y centro de intereses vitales, no la regla de 183 días), RFC y e.firma, retenciones de empleador mexicano vs trabajo remoto para empresa extranjera y nómadas digitales (sin condición migratoria específica en 2026). Usar cuando el usuario diga trabajar en México siendo extranjero, permiso de trabajo, RFC extranjero, nómada digital impuestos, residencia fiscal México, doble tributación.
allowed-tools: Read, Write
---

# Asesoría laboral para extranjeros

## Permisos para trabajar (Ley de Migración)

### A. Residente temporal con oferta de empleo
- El empleador debe tener Constancia de Inscripción de Empleador (CIE) ante el INM (derecho $391.10, Art. 13 fr. V LFD 2026).
- Desde el extranjero: el empleador tramita la oferta, el INM autoriza y el consulado expide la visa de residente con permiso para trabajar.
- Si ya es residente temporal: solicita permiso para trabajar ($4,340.77, Art. 13 fr. III LFD).
- Cambio de empleador o lugar de trabajo: avisar al INM dentro de 90 días (Art. 63 LM); si no, multa 20-100 UMA (Art. 158 LM).

### B. Residente permanente
- Permiso para trabajar incluido (Art. 52 fr. IX LM).

### C. Visitante con permiso para actividades remuneradas
- Hasta 180 días con oferta o invitación específica (Art. 52 fr. II LM); cuota $4,340.77.

### D. Nómada digital
- Sin condición migratoria específica a 2026. Hay una iniciativa en la Cámara de Diputados (Gaceta 14-09-2026) para crear un "residente temporal nómada digital"; no está vigente.
- El visitante sin permiso no puede recibir remuneración en México; trabajar en remoto para un empleador extranjero como turista es zona gris: no lo recomiendes.
- Ruta usual: residente temporal por solvencia económica (montos en los Lineamientos del INM, verificar vigentes).

## Obligaciones fiscales

| Situación | Tratamiento |
|---|---|
| Residente fiscal en México (Art. 9 fr. I CFF) | Tributa en México por ingresos de todo el mundo |
| No residente fiscal | Solo por ingresos de fuente mexicana (Título V LISR) |
| Trabajo remoto para empresa de EUA u otro país con tratado | Revisar el convenio para evitar doble tributación y el desempate de residencia |

**Residencia fiscal**: una persona física es residente en México si aquí tiene su casa habitación; si también tiene casa en otro país, si su centro de intereses vitales está en México (más de 50% de sus ingresos de fuente mexicana o su actividad profesional principal aquí). La regla de 183 días no está en el CFF; aparece en los tratados y en otras disposiciones. Tener tarjeta de residente migratorio no equivale a ser residente fiscal.

**Régimen**: empleado de empresa mexicana → sueldos y salarios (605); servicios independientes → actividad profesional (612) o RESICO (626) si cumple requisitos. Ver `iva-retenciones-mx` para retenciones.

## Output

```json
{
  "condicion_estancia": "residente_temporal",
  "tiene_permiso_trabajo": true,
  "empleador_con_cie": "ACME S.A. de C.V.",
  "residencia_fiscal_mx": "probable — casa habitación en México",
  "regimen_recomendado": "Sueldos 605 (si empleo formal) o 612/626 (si servicios)",
  "rfc_solicitado": true,
  "advertencias": [
    "Si trabajas para empresa extranjera: revisar el tratado para evitar doble tributación",
    "Cambio de empleador: avisar al INM dentro de 90 días"
  ],
  "vigencia_validada": true
}
```

> No es asesoría fiscal ni legal: confirma residencia fiscal y régimen con un contador.
