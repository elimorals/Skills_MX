# pf-anual-mx

Plugin dedicado al ciclo completo de declaración anual ISR para personas físicas en México.

> Spec: `docs/specs/05-vertical-pf-anual-mx.md`
> Score original del research: **9.5/10** (mayor del proyecto)
> Mercado: ~5M declarantes anuales obligados

## Cobertura

**Regímenes soportados:**
- PFAE — 612 (Personas Físicas con Actividades Empresariales y Profesionales)
- RESICO PF — 626 (Régimen Simplificado de Confianza Persona Física)
- Asalariado + honorarios — 605 + 612 (caso común)

**Out of scope (por ahora):**
- Persona moral (vertical aparte)
- Pensiones/jubilación (caso edge)
- Honorarios asimilados a salarios (caso edge)

## Ciclo del año

```
Ene-Feb : preparación
Mar-Abr : declaración (deadline 30 abril)
May-Jun : seguimiento devolución
Jul-Dic : ahorro fiscal del año en curso
```

## Comandos

| Comando | Cuándo usar |
|---|---|
| `/pf-anual:dashboard` | Ver estado del año fiscal actual |
| `/pf-anual:recopilar` | Descargar todos los CFDIs del año (vía SAT) |
| `/pf-anual:calcular` | Calcular ISR + comparar con provisionales |
| `/pf-anual:borrador` | Generar PDF presentable de la declaración |
| `/pf-anual:status-devolucion` | Tracking si solicitaste devolución |

## Skills (8)

1. **dashboard-anual-fiscal** — status del año fiscal en curso
2. **recopilar-cfdis-anuales** — descarga masiva 12 meses (vía `mp_sat_portal`)
3. **cruzar-bancos-vs-cfdis** — detectar depósitos sin facturar
4. **identificar-deducciones-personales** — salud, hipoteca, donativos, etc.
5. **calculadora-isr-anual** — tarifa Art. 96 LISR + escalas RESICO
6. **generar-borrador-declaracion** — PDF con desglose por capítulo
7. **seguimiento-devolucion-sat** — tracking devolución
8. **alertas-deadline-anual** — calendario fiscal

## Workflow

`workflow-pf-anual-completa.md` — orquestador end-to-end

## Dependencias

- **core-mexico** (cfdi-emision, iva-retenciones-mx, rfc-validacion, mxn-formato, whatsapp-business-mx, compliance-lfpdppp)
- MCPs: `mp_sat_portal`, `mp_banxico`, `mp_facturama_extendido`, `mp_bancos_mx`, `mp_aspel_contpaqi` (opcional)

## ⚠ Limitaciones

- Borrador NO presenta automáticamente al SAT — guía al usuario por DeclaraSAT
- `vigencia_validada: false` por default — recomendado pasar por contador certificado antes de presentar
- Tarifa Art. 96 LISR debe revisarse cada enero (cambia anualmente)

Ver `docs/specs/05-vertical-pf-anual-mx.md` para spec completo.
