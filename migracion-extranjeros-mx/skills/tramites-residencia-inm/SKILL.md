---
name: tramites-residencia-inm
description: Guía de trámites de residencia ante el Instituto Nacional de Migración (INM) México. Cubre residencia temporal (hasta 4 años), residencia permanente (indefinida), canje de visa consular, cambio de condición de estancia (unidad familiar, matrimonio con mexicano), permiso para trabajar con oferta de empleo, requisitos por trámite y derechos 2026 de la Ley Federal de Derechos (residente temporal 1 año $11,140.74; permanente $13,578.96). Usar cuando el usuario diga residencia México, trámite INM, visa de residente, tarjeta de residente, cambiar condición migratoria, cuánto cuesta la residencia, canje de visa. NO sustituye asesoría legal migratoria.
allowed-tools: Read, Write
---

# Trámites de residencia INM

Fuentes: Ley de Migración (última reforma DOF 15-01-2026), Arts. 8o, 9o, 10 y 13 de la Ley Federal de Derechos (cuotas 2026, reforma DOF 07-11-2025, cantidades actualizadas por Anexo 4 RMF DOF 28-12-2025).

## Tipos de residencia

### Residente temporal (Art. 52 fr. VII LM)
- Hasta 4 años en total. La primera tarjeta suele ser de 1 año; las renovaciones pueden ser de 1 a 3 años.
- Trabajar: requiere permiso para trabajar ligado a una oferta de empleo de un empleador con Constancia de Inscripción de Empleador (CIE).
- Familia: puede traer a cónyuge, concubino(a), hijos menores y otros dependientes (unidad familiar).
- Vía normal: visa de residente en un consulado mexicano → entrada con FMM marcada para canje → canje por tarjeta en el INM dentro de los 30 días naturales siguientes a la entrada.
- Un **visitante (turista) NO puede cambiar a residente desde México**, salvo por razones humanitarias o vínculo familiar con mexicano o con residente (Art. 53 LM).

### Residente permanente (Art. 52 fr. IX y 54 LM)
- Indefinida, con permiso para trabajar.
- Supuestos: 4 años como residente temporal; unidad familiar (el cónyuge o concubino de un residente permanente recibe residencia temporal por 2 años y después permanente, Art. 55 fr. II-III; para cónyuge de mexicano la regla equivalente está en los Lineamientos del INM, verificar); jubilado o pensionado con ingreso suficiente; hijos mexicanos por nacimiento; ascendiente o descendiente en línea recta hasta segundo grado de mexicano por nacimiento; asilo, refugio o protección complementaria; sistema de puntos.

### Otros
- Residente temporal estudiante: no paga el derecho del Art. 8o (Art. 11 fr. I LFD).
- Refugio y protección complementaria: trámite ante COMAR, gratuito.
- Visitante sin permiso para actividades remuneradas: hasta 180 días, no puede trabajar ni cobrar en México.

## Derechos 2026 (LFD)

| Concepto | Artículo LFD | Cuota 2026 |
|---|---|---|
| Residente temporal hasta 1 año | 8o fr. VI a) | $11,140.74 |
| Residente temporal 2 años | 8o fr. VI b) | $16,693.36 |
| Residente temporal 3 años | 8o fr. VI c) | $21,142.58 |
| Residente temporal 4 años | 8o fr. VI d) | $25,057.82 |
| Residente permanente | 8o fr. VII | $13,578.96 |
| Visitante sin permiso para actividades remuneradas | 8o fr. I | $983.00 |
| Visitante con permiso para actividades remuneradas | 8o fr. II | $4,340.77 |
| Cambio de condición de estancia (más la cuota de la nueva condición) | 9o | $1,847.13 |
| Regularización (más la cuota de la condición) | 10 | $1,847.13 |
| Permiso para trabajar de residente temporal | 13 fr. III | $4,340.77 |
| Constancia de inscripción de empleador | 13 fr. V | $391.10 |
| Permiso de salida y regreso | 13 fr. II | $591.06 |
| Reposición de tarjeta de residente | 8o | $1,779.93 |

- La renovación paga la misma cuota que la expedición.
- **Descuento 50% (nuevo en 2026)**: residentes temporales y permanentes que acrediten unidad familiar, oferta de empleo de un empleador con CIE vigente o invitación para actividades no remuneradas (Art. 8o último párrafo LFD). El INM aún no publicaba el procedimiento operativo según fuentes secundarias (Clark Hill y EIG, nov-2025): verificar con el INM antes de pagar con descuento.
- Ejemplo: canje inicial a residente temporal 1 año = $11,140.74; con el descuento por oferta de empleo = $5,570.37, más el permiso para trabajar $4,340.77.

## Documentos típicos

- Pasaporte vigente
- Actas apostilladas y traducidas por perito si se acredita vínculo familiar (skill `validador-traduccion-documentos`)
- Solvencia económica (montos mínimos en los Lineamientos del INM, expresados en salarios mínimos o UMA: verificar los vigentes) u oferta de empleo
- Formato de solicitud y comprobante de pago de derechos
- Fotografías con las especificaciones del INM

## Output

```json
{
  "tipo_tramite": "residencia_temporal_canje",
  "via": "visa_consular_y_canje_30_dias",
  "documentos_requeridos": [...],
  "documentos_presentados": [...],
  "completitud_pct": 85,
  "derechos_lfd_2026_mxn": "11140.74",
  "descuento_50_aplicable": false,
  "donde_acudir": "Oficina del INM que corresponda al domicilio — con cita",
  "tiempo_estimado_resolucion": "variable por oficina; verificar",
  "vigencia_validada": true
}
```

> No es asesoría legal: casos con antecedentes, negativas previas o situación irregular deben revisarse con abogado migratorio.
