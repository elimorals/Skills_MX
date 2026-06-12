# arrendador-residencial-mx

Plugin para el arrendador residencial mexicano (PF dueño directo de 1-10 propiedades).

> Spec: `docs/specs/06-vertical-arrendador-residencial-mx.md`
> Score original del research: **9.3/10**
> Mercado: ~2M arrendadores

## Diferencias vs inmobiliaria-mx

| `inmobiliaria-mx` | `arrendador-residencial-mx` |
|---|---|
| Corredor / inmobiliaria | Dueño directo (PF) |
| Conecta dueño+inquilino | Opera su propia propiedad |
| Comisión por servicio | CFDI mensual por renta |
| Relación transaccional | Relación continua (meses-años) |
| Cobranza vía cliente del corredor | Cobranza directa al inquilino |

## Comandos

| Comando | Acción |
|---|---|
| `/arrendador:dashboard` | Status de propiedades (pagadas, vencidas, vacantes) |
| `/arrendador:screening` | Evaluar inquilino candidato (Buró + ingresos + referencias) |
| `/arrendador:contrato` | Generar contrato arrendamiento residencial CCDF/CCF |
| `/arrendador:facturar-mes` | CFDI mensual a todos los inquilinos del mes |
| `/arrendador:cobranza` | Corrida cobranza escalada (D+3 / D+7 / D+15 / D+30) |

## Skills (8)

1. **dashboard-propiedades** — status mensual por propiedad
2. **screening-inquilino-completo** — pipeline con autorización Buró
3. **contrato-arrendamiento-residencial** — CCDF/CCF + adendums
4. **cobranza-mensual-renta** — escalado con tono a relación continua
5. **cfdi-arrendamiento-mensual** — CFDI tipo I uso D04 / G03
6. **actualizacion-renta-anual** — INPC INEGI + notificación
7. **gastos-deducibles-propiedad** — predial, mantenimiento, IVA acreditable
8. **cierre-contrato-checklist** — inspección + depósito + prorroga

## Workflow

`workflow-cobranza-renta-mensual.md` — corrida mensual completa

## Dependencias

- `core-mexico` (cfdi-emision, iva-retenciones-mx, rfc-validacion, mxn-formato, whatsapp-business-mx, compliance-lfpdppp)
- MCPs: `mp_facturama_extendido`, `mp_banxico` (INPC), `mp_buro_credito_personal` (con autorización), `mp_bancos_mx`, `mp_inmuebles24` (comparables), `mp_sat_portal`

## ⚠ Compliance crítico

- **Screening con Buró requiere autorización formal** del inquilino (Art. 32 LFPDPPP + LRSIC). El skill `screening-inquilino-completo` NO consulta sin token de autorización explícito.
- Cláusulas del contrato vigentes en CDMX (CCDF). Para otros estados (CCF + códigos estatales) puede haber variaciones — consultar abogado local.
- Renta incrementada por INPC anual: válido legalmente, pero requiere aviso previo al inquilino.
- Toda comunicación de cobranza respeta dignidad del inquilino (relación continua, no transaccional).

Ver `docs/specs/06-vertical-arrendador-residencial-mx.md` para spec completo.
