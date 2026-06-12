---
name: asesoria-laboral-extranjero
description: Guía sobre derechos laborales y obligaciones fiscales para extranjeros trabajando en México. Cubre permiso de trabajo (residente temporal con oferta), RFC + e.firma (con doble residencia fiscal), retenciones por empleador mexicano vs trabajo remoto, regulación digital nomad (sin status legal específico aún). Usar cuando el usuario diga trabajar mexico extranjero, permiso trabajo, RFC extranjero, digital nomad fiscal.
allowed-tools: Read, Write
---

# Asesoría laboral extranjero

## Permisos de trabajo

### A. Residente temporal con oferta de empleo
- INM emite oferta de empleo + ANUE (Aviso de Oferta de Empleo)
- Permite trabajar con ese empleador
- Cambio de empleador → notificar INM

### B. Residente permanente
- Sin restricciones, trabaja libremente

### C. Visitante con permiso para realizar actividades remuneradas
- Excepcional, requiere autorización específica

### D. Digital nomad
- ⚠ Sin status legal específico en MX (a 2026)
- Si trabaja para empresa extranjera y < 180 días: visitante sin permiso (zona gris)
- Mejor: aplicar a residente temporal con solvencia económica

## Obligaciones fiscales

| Situación | Régimen MX |
|---|---|
| Residente fiscal MX (> 183 días/año) | Tributa en MX por ingresos mundiales |
| No residente fiscal MX | Solo tributa en MX por ingresos fuente MX |
| Trabajo remoto para empresa USA | Posible doble tributación (convenio US-MX) |

## Output

```json
{
  "tipo_visa": "residente_temporal",
  "tiene_permiso_trabajo": true,
  "empleador_registrado_inm": "ACME S.A. de C.V.",
  "residencia_fiscal_mx": true,
  "dias_en_mexico_anio": 280,
  "regimen_recomendado": "Sueldos 605 (si empleo formal) o 612 PFAE (si servicios)",
  "rfc_solicitado": true,
  "advertencias": [
    "Si trabajas para empresa USA: revisar convenio doble tributación",
    "Cambio de empleador: notificar INM dentro de 30 días"
  ],
  "vigencia_validada": false
}
```
