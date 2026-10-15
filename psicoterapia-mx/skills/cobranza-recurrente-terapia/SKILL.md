---
name: cobranza-recurrente-terapia
description: Cobranza recurrente para pacientes en terapia con plantillas extra-empáticas porque la relación es continua y sensible (un paciente molesto por cobranza agresiva = abandono terapéutico). Recordatorios sutiles, opciones de pago, descuentos por compromiso paquete (10 sesiones), facturación CFDI D01 si pide. Usar cuando el usuario diga cobrar paciente terapia, mensualidad psicologia.
allowed-tools: Read, Write
---

# Cobranza recurrente terapia

## Niveles empáticos

### Nivel 1 — Recordatorio sutil (D-2)
```
Hola [Nombre], pasando a recordarte que el próximo [día] tenemos nuestra sesión.
La inversión es de $[X] que puedes traer al consultorio o transferir antes.
Cualquier cosa avísame. Saludos.
```

### Nivel 2 — Pendiente post-sesión (D+3)
```
Hola [Nombre], quería recordarte sobre el pago de nuestra sesión del [fecha].
Si ya lo hiciste, perdón por molestar — confírmame por aquí.
```

### Nivel 3 — Atención respetuosa (D+7)
```
[Nombre], espero te encuentres bien.
Aún no he recibido el pago de la sesión del [fecha]. ¿Pasa algo en lo que pueda apoyarte?
Si hay dificultad económica podemos revisar opciones.
```

⚠ Más de 2 sesiones pendientes: conversación en sesión, no cobranza por mensaje.

## Modelos típicos

- **Por sesión**: rango de mercado orientativo $400-$1,500 MXN (sin fuente oficial; ajustar a tu ciudad)
- **Paquete 10 sesiones**: 10-15% descuento
- **Mensualidad fija** (4 sesiones/mes): pago inicio de mes
- **Sliding scale**: descuento por nivel socioeconómico (compromiso social)

## IVA y factura (validar con contador)

| Quién cobra | IVA | Fundamento |
|---|---|---|
| Psicólogo persona física | **16%** | La exención del Art. 15 fr. XIV LIVA exige título de médico; el RLIVA (Art. 41) la limita a médicos, veterinarios y dentistas. Confianza media (análisis de despachos; no hay criterio SAT localizado). Hay iniciativas 2025-2026 para exentar psicología, sin aprobar a oct-2026 |
| Psiquiatra (médico) persona física | Exento | Art. 15 fr. XIV LIVA |
| Centro de terapia persona moral | 16% | La exención es solo para PF o sociedades civiles de médicos |

Ejemplo psicólogo: sesión de $800 + IVA 16% $128 = **$928**. Si el precio pactado ya "incluye IVA": $928 / 1.16 = $800 de base.

- **Deducible para el paciente**: sí, con CFDI uso **D01** y pago no efectivo; el Art. 151 fr. I LISR incluye expresamente servicios de psicología prestados por profesionista con título registrado.
- Si paga una persona moral (empresa, EAP): retiene ISR 10% (régimen 612) o 1.25% (RESICO) y, por estar gravado, IVA 2/3 = 10.6667% del subtotal. Detalle: skill compartida `iva-retenciones-mx`.
- Emisión del CFDI: skill compartida `cfdi-emision`.
