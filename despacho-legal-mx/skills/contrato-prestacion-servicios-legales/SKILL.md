---
name: contrato-prestacion-servicios-legales
description: Genera contrato de prestación de servicios profesionales jurídicos entre despacho/abogado y cliente con cláusulas mercantiles vigentes en México (Art. 2606-2615 CCFm para mandato y honorarios), incluyendo objeto específico del servicio (asesoría, litigio, gestión, dictamen, opinión), forma de cobro (iguala mensual, honorarios por etapas, cuota litis con desglose porcentual, o esquema mixto), gastos y costas (a cargo de quién según resultado), terminación anticipada con honorarios devengados, confidencialidad reforzada por secreto profesional, jurisdicción CDMX/GDL/MTY por defecto, y aviso ARCO específico para datos sensibles del proceso. Diferencia entre asunto contencioso vs no contencioso para clausulas de cuota litis. Usar cuando el usuario diga "contrato abogado", "honorarios legales", "cuota litis", "iguala mensual despacho", "contrato prestación servicios legales", "engagement letter abogado". NO usar para contrato comercial general ni laboral.
allowed-tools: Read, Write, Edit
---

# Contrato de prestación de servicios profesionales — jurídico

## Cláusulas obligatorias

1. **Identificación**: nombres + RFC + cédula profesional del abogado
2. **Objeto**: específico del asunto (no genérico tipo "asesoría legal")
3. **Honorarios**:
   - Iguala: monto mensual + IVA + retenciones aplicables (si receptor PM: 10% ISR + 10.67% IVA en PFAE)
   - Por etapas: hito → monto, con CFDI por cada etapa
   - Cuota litis: % del beneficio obtenido, mínimo de honorarios garantizados, qué pasa si pierde
4. **Gastos y costas**: a cargo del cliente normalmente; cuota litis puede absorberlos
5. **Terminación anticipada**: honorarios devengados + penalidad si aplica
6. **Confidencialidad**: secreto profesional (Art. 36 LGM y 213 CPDF)
7. **Aviso ARCO**: específico para datos sensibles del proceso
8. **Jurisdicción**: por defecto CDMX salvo sede del despacho

## Cláusula de cuota litis (especial)

> ⚠ Requiere revisión legal previa. Algunos códigos estatales limitan o regulan.
> Pendiente: validación con abogado mercantilista (ver brief).

## Output

```
contratos-legales/<rfc-hash>/<expediente-id>/
  ├── contrato.md   (versión editable)
  └── contrato.pdf  (versión firma)
```
