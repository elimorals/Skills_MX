---
name: calendario-fiscal-clientes
description: Calendario consolidado de obligaciones fiscales y de seguridad social de TODOS los clientes del despacho - pagos provisionales ISR/IVA (día 17), DIOT, contabilidad electrónica (balanza día 3 PM / día 5 PF del segundo mes), cuotas IMSS mensuales y bimestrales con INFONAVIT, CFDI de nómina, declaraciones anuales (PM 31 marzo, PF 30 abril) y donatarias. Vista diaria/semanal por cliente para no perder ningún plazo. Usar cuando el usuario diga calendario fiscal, obligaciones de clientes, deadlines del mes, vencimientos SAT, qué vence esta semana, agenda fiscal del despacho.
allowed-tools: Read, Write
---

# Calendario fiscal clientes

## Plazos base 2026 (verifica cada RMF)

| Obligación | Plazo | Fundamento |
|---|---|---|
| Pago provisional ISR / IVA mensual, retenciones | Día 17 del mes siguiente (PF: +1 a 5 días hábiles según 6.º dígito del RFC, decreto de beneficios; verificar) | Arts. 14 y 106 LISR, 5-D LIVA |
| DIOT | Último día del mes siguiente (facilidad de la RMF; la LIVA dice día 17) | Art. 32 fr. VIII LIVA + RMF |
| Contabilidad electrónica: balanza mensual | PM: día 3 del 2.º mes siguiente; PF: día 5 del 2.º mes siguiente | Art. 28 CFF, Anexo 24 y regla 2.8.1.x RMF 2026 (fuente secundaria: Siempre al Día 2026, IDC; confianza media en el número de regla) |
| Catálogo de cuentas | Con la primera balanza y cuando se modifique al nivel requerido | ídem |
| Balanza de cierre (ajustada) | PM: 20 de abril; PF: 22 de mayo | ídem |
| Cuotas IMSS (EyM, IV, RT, GPS) | Día 17 del mes siguiente | Art. 39 LSS |
| RCV + INFONAVIT | Día 17 del mes siguiente al bimestre (ene, mar, may, jul, sep, nov) | Art. 39 LSS, Art. 35 LINFONAVIT |
| Prima de riesgo de trabajo | Declaración anual a más tardar el último día hábil de febrero | Art. 74 LSS |
| CFDI de nómina | Al pagar (plazo exacto en la regla de nómina de la RMF 2026; verificar) | Art. 99 fr. III LISR |
| Anual PM | 31 de marzo | Art. 76 fr. V LISR |
| Anual PF | 30 de abril | Art. 150 LISR |
| PTU | PM 30 de mayo; PF 29 de junio | Art. 122 LFT |
| Donatarias: declaración anual informativa | 15 de febrero | Art. 86 LISR |
| Donatarias: informe de transparencia | Mayo (a más tardar 31) | Art. 82 fr. VI LISR + RMF |

Notas:
- RESICO PF no envía contabilidad electrónica; para RESICO PM y PF con ingresos bajos, **verifica la facilidad vigente** antes de marcar la obligación.
- Si el plazo cae en inhábil, se corre al siguiente día hábil (Art. 12 CFF).
- Para el detalle por régimen puede usarse `sat_calendario_fiscal_por_regimen` (MCP `mp_sat_portal`) e `imss_calendario_obligaciones` (`mp_imss_patronal`, sin verificar); contrasta con esta tabla.

## Output mensual

```
📅 JUNIO 2026 — Obligaciones fiscales clientes

Día 3 (mié):
  • Balanza de abril — 5 PM
Día 5 (vie):
  • Balanza de abril — 9 PF con actividad
Día 17 (mié):
  • Pago provisional ISR/IVA de mayo: 35 clientes
  • Cuotas IMSS mensuales de mayo: 15 patrones
Día 29 (lun):
  • PTU — clientes PF con trabajadores
Día 30 (mar):
  • DIOT de mayo: 28 clientes

Total tareas mes: 84
Completadas: 22 (26%)
En riesgo (plazo < 3 días): 8 ⚠
```

El bimestre mar-abr se paga el 17 de mayo; en junio se paga solo el mensual. Ajusta según el mes: los bimestrales caen en ene, mar, may, jul, sep y nov.

## Schema obligación

```python
class ObligacionFiscal(BaseModel):
    cliente_id: str
    cliente_rfc_hash: str
    tipo_obligacion: Literal["isr_iva_prov", "anual_pf", "anual_pm", "diot", "imss_mensual",
                             "rcv_infonavit_bimestral", "cfdi_nomina", "contabilidad_electronica",
                             "ptu", "donataria_transparencia"]
    periodo: str  # "2026-05"
    deadline: date
    estado: Literal["pendiente", "en_proceso", "completada", "vencida"]
    responsable_despacho: str
    importe_a_pagar_estimado_mxn: Decimal | None
```

Valida los plazos especiales de cada cliente con el contador responsable.
