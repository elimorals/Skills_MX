---
name: complemento-inseduc-cfdi-d10
description: Construye complemento InsEduc (Instituciones Educativas) requerido en CFDI con UsoCFDI D10 para que el padre de familia pueda deducir colegiaturas conforme al Decreto de Facilidades Administrativas en Materia Educativa (DOF). Incluye datos obligatorios: nombre completo del alumno, CURP del alumno validada, nivel educativo (preescolar, primaria, secundaria, profesional técnico, bachillerato), clave del centro de trabajo CCT (SEP federal) o autorización estatal según el caso, periodo del pago (mensual/bimestral/anual), tope vigente del decreto por nivel educativo aplicado, y RFC del padre/tutor responsable receptor del CFDI. Detecta errores comunes que rechazan deducción: pago en efectivo (debe ser electrónico), CFDI a nombre del alumno en vez del padre, CFDI sin complemento, alumno mayor de edad sin probar dependencia económica, escuela sin RVOE federal ni autorización estatal. Genera payload listo para mp_facturama_extendido.timbrar_con_inseduc. Usar cuando el usuario diga "CFDI colegiatura", "factura colegio deducible", "InsEduc D10", "complemento educativo", "factura escuela padre deduce". NO usar para inscripción (no deducible típicamente) ni para universidad (excluida del decreto).
allowed-tools: Read, Write, Edit
---

# Complemento InsEduc para CFDI D10

## Estructura del complemento

```xml
<inseduc:InsEduc Version="1.0"
    NombreAlumno="Sofía Pérez Hernández"
    CURP="PEHS150301HDFRZG02"
    NivelEducativo="Primaria"
    AutRVOE="RVOE-2018-0234"
    RFCPago="PERA850115ABC">
</inseduc:InsEduc>
```

## Niveles educativos válidos del decreto

| Nivel SAT InsEduc | Tope anual MXN | Notas |
|---|---|---|
| Preescolar | $14,200 | Incluye maternal en escuelas con RVOE |
| Primaria | $12,900 | |
| Secundaria | $19,900 | Incluye técnica |
| Profesional Técnico | $17,100 | Bachillerato técnico |
| Bachillerato | $24,500 | General |
| Bachillerato Técnico | $24,500 | Mismo tope |
| Universidad/Posgrado | NO incluido | Excluido del decreto |

## Validaciones críticas pre-timbrado

1. **Nombre alumno**: completo (paterno, materno, nombres)
2. **CURP alumno**: 18 caracteres + validación con mp_curp_renapo
3. **NivelEducativo**: dentro del catálogo SAT InsEduc
4. **CCT o RVOE**: obligatorio uno de los dos
5. **RFCPago**: RFC del padre/tutor (NO del alumno)
6. **UsoCFDI** debe ser D10
7. **FormaPago** debe ser electrónica (03 SPEI / 04 TDC / 05 Monedero / 28 TDD), NO 01 Efectivo
8. **Importe** del concepto ≤ tope del nivel del año

## Casos edge típicos

### Múltiples hijos en mismo colegio
- 1 CFDI por hijo (cada uno con su complemento InsEduc)
- Permite deducir cada uno independientemente al tope

### Padres divorciados — quién deduce
- Solo el padre/tutor que efectivamente PAGUE puede deducir
- Si ambos pagan parcialmente: cada uno por su parte (2 CFDIs con cada RFC)

### Pago en parcialidades
- Opción A: 1 CFDI por parcialidad (más limpio)
- Opción B: 1 CFDI anual al cierre del ciclo (más simple administrativamente)

### Alumno mayor de edad (>18)
- Padre puede deducir si demuestra dependencia económica (sin ingresos propios)
- Skill marca advertencia pero permite emitir

### Inscripción
- Generalmente NO deducible (no está en decreto)
- Algunos tribunales han dado fallos favorables — caso a caso

## Output del skill

```yaml
payload_facturama:
  TipoComprobante: I
  UsoCFDI: D10
  FormaPago: "03"
  MetodoPago: PUE
  Receptor:
    Rfc: PERA850115ABC
    Nombre: PEREZ ALBERTO
    DomicilioFiscalReceptor: "06700"
    RegimenFiscalReceptor: "616"
  Conceptos:
    - ClaveProdServ: "86121601"  # servicios educativos primaria
      Cantidad: 1
      ClaveUnidad: ACT
      Descripcion: "Colegiatura primaria — periodo febrero 2026"
      ValorUnitario: 1075
      Importe: 1075
  Complemento:
    InsEduc:
      Version: "1.0"
      NombreAlumno: "Sofía Pérez Hernández"
      CURP: "PEHS150301HDFRZG02"
      NivelEducativo: "Primaria"
      AutRVOE: "RVOE-2018-0234"
      RFCPago: "PERA850115ABC"
```

## Validación pendiente

⚠ Versión del complemento InsEduc puede actualizarse — confirmar contra anexo 20 SAT.
⚠ Topes del decreto se publican periódicamente — actualizar al detectar nuevo DOF.
