---
name: contrato-boda-pf-pm
description: Contrato de servicios de wedding planning para personas físicas o morales mexicanas. Cláusulas que protegen al planner (cancelación, fuerza mayor, propiedad intelectual de propuestas, exclusividad), al cliente (entregables, calidad, plazos, devolución parcial) y a ambos (compromiso de pagos, jurisdicción). Vigencia, escrow para proveedores cuando aplica, IVA y retenciones. Usar cuando el usuario diga contrato boda, contrato wedding planner, cláusulas evento, formalizar planner. NO usar para cotizaciones (cotizacion-boda-mxn) ni timeline (otro skill).
allowed-tools: Read, Write, Edit
---

# Contrato de servicios wedding planning

⚠ **Validar con abogado mercantilista** antes de uso real con cliente.

## Estructura del contrato

```markdown
CONTRATO DE PRESTACIÓN DE SERVICIOS DE COORDINACIÓN
DE EVENTOS SOCIALES (WEDDING PLANNING)

ENTRE:
{{razon_social_planner}}, con RFC {{rfc_planner}}, representada por
{{representante_legal_planner}}, en lo sucesivo "EL PLANNER"

Y:
{{nombre_cliente}}, con RFC {{rfc_cliente}}, con domicilio en
{{domicilio_cliente}}, en lo sucesivo "EL CLIENTE"

CONJUNTAMENTE "LAS PARTES"

DECLARACIONES Y CLÁUSULAS:

PRIMERA — OBJETO DEL CONTRATO
EL PLANNER se compromete a prestar al CLIENTE servicios de planeación,
coordinación y supervisión del evento {{nombre_evento}} a celebrarse
el día {{fecha}} en {{lugar}} con un número estimado de {{invitados}}
invitados.

SEGUNDA — ALCANCE DE SERVICIOS
El alcance específico se detalla en el Anexo 1 (Brief de Boda) y Anexo 2
(Cotización), que forman parte integrante del presente contrato.

Modalidades aplicables (marcar):
[ ] Full Planning (desde D-365)
[ ] Coordinación parcial (desde D-90)
[ ] Day-of coordination (solo el día del evento)
[ ] Otra: __________

TERCERA — HONORARIOS
Por los servicios descritos, EL CLIENTE pagará a EL PLANNER la cantidad
de ${{monto_total}} MXN (más IVA correspondiente), distribuida en:

| Pago | Monto | Fecha |
|---|---|---|
| Firma del contrato | ${{anticipo}} (30%) | A la firma |
| Hito D-180 | ${{intermedio}} (40%) | {{fecha_intermedio}} |
| Hito D-30 | ${{pago_final}} (30%) | {{fecha_pago_final}} |

Los pagos se realizarán mediante {{transferencia_spei}} a la cuenta
{{cuenta_planner}}. EL PLANNER emitirá CFDI por cada pago.

CUARTA — OBLIGACIONES DEL PLANNER
EL PLANNER se obliga a:
a) Coordinar los proveedores listados en el Anexo 2.
b) Mantener comunicación constante con EL CLIENTE (mínimo 1 update semanal).
c) Estar presente en el evento desde D-1 hasta D+1 (modalidad full/parcial).
d) Llevar registro de gastos contra presupuesto aprobado.
e) Mantener confidencialidad sobre datos personales del CLIENTE (LFPDPPP).

QUINTA — OBLIGACIONES DEL CLIENTE
EL CLIENTE se obliga a:
a) Pagar los honorarios en los plazos pactados.
b) Aprobar o rechazar propuestas de proveedores en máximo 5 días hábiles.
c) Atender a llamadas/mensajes del PLANNER con respuesta máxima 48h.
d) Proveer documentación necesaria (acta nacimiento, identificación, etc.).
e) Coordinarse con familiares para evitar interferencias en la operación
   del PLANNER.

SEXTA — CANCELACIÓN
6.1. Cancelación por EL CLIENTE:
- Hasta D-180: reembolso del 50% del anticipo
- D-180 a D-90: reembolso del 25% del anticipo
- D-90 a D-30: SIN reembolso del anticipo, pero EL PLANNER cancelará
  contratos con proveedores si aún es posible
- D-30 en adelante: pago completo de honorarios + costos no recuperables

6.2. Cancelación por EL PLANNER:
- Si EL CLIENTE incumple obligaciones materialmente, EL PLANNER puede
  rescindir notificando con 30 días.
- EL PLANNER reembolsará la parte proporcional de servicios no prestados.

SÉPTIMA — FUERZA MAYOR
Eventos de fuerza mayor (pandemia, terremoto, guerra, fallecimiento
familiar inmediato del CLIENTE, decreto gubernamental que prohíba el
evento) suspenden las obligaciones de ambas partes. El evento se podrá:
a) Reagendar dentro de 18 meses sin penalización (excepto incrementos
   de proveedores que se cubren proporcionalmente).
b) Cancelar con devolución prorrateada según costos ya incurridos.

OCTAVA — PROPIEDAD INTELECTUAL
Las propuestas creativas, diseño de evento, paleta de colores,
referencias visuales y plan operativo son propiedad intelectual del
PLANNER hasta el pago total del contrato. No pueden ser usados por
EL CLIENTE para contratar otro planner o ejecutar el evento sin
EL PLANNER.

NOVENA — EXCLUSIVIDAD
EL CLIENTE no podrá contratar otro coordinador para el mismo evento.
EL PLANNER puede atender otros eventos en paralelo.

DÉCIMA — RESPONSABILIDAD
La responsabilidad de EL PLANNER se limita al monto pagado por sus
servicios. EL PLANNER no responde por incumplimientos de proveedores
contratados (cuyo contrato es directo entre proveedor y CLIENTE),
excepto por culpa o negligencia del PLANNER en su selección o
supervisión.

DÉCIMA PRIMERA — CONFIDENCIALIDAD Y DATOS PERSONALES
Ambas partes se obligan a mantener confidencialidad de toda información
intercambiada. EL PLANNER cumplirá con la LFPDPPP en el tratamiento
de datos personales del CLIENTE e invitados.

DÉCIMA SEGUNDA — JURISDICCIÓN
LAS PARTES se someten a la jurisdicción de los tribunales competentes
de {{ciudad}}, renunciando a cualquier otra que pudiera corresponderles.

DÉCIMA TERCERA — VIGENCIA
El presente contrato entra en vigor a la firma y termina con la
entrega del álbum final y reporte de cierre (D+60 típico).

FIRMAS:

_______________________          _______________________
EL PLANNER                       EL CLIENTE
{{nombre_planner}}                {{nombre_cliente}}

Lugar y fecha: {{ciudad}}, {{fecha_firma}}
```

## Cláusulas opcionales (anexar según contexto)

### Si hay padrinos / familiares que pagan
- Anexo de partes solidarias responsables

### Si es boda de destino
- Logística de hospedaje del equipo del planner
- Penalizaciones por cambio de destino

### Si hay sponsoring / convenios con marcas
- Cláusula de divulgación + restricciones de publicación

### Si el cliente quiere usar fotos en redes sociales
- Cesión de uso de imagen (cliente y planner)

## Implicaciones fiscales (CFDI + retenciones)

### Si el cliente es persona física (típico)
- CFDI tipo I cada pago
- Sin retenciones (Art. 1-A LIVA)
- MetodoPago: PUE (Pago en Una Sola Exhibición) por cada pago individual

### Si el cliente es persona moral (boda corporativa, evento empresarial)
- CFDI tipo I cada pago
- Si planner es PFAE: retención 10% ISR + 2/3 IVA (Art. 1-A LIVA)
- Si planner es PM SA: sin retención

### IVA
- Servicios sujetos al 16% IVA general
- Si frontera norte: 8% IVA
- Bodas en zona turística: 16% normal

## Output estructurado

```json
{
  "contrato_generado": {
    "tipo": "wedding_planning_full",
    "monto_total_mxn": 250000,
    "anticipo_mxn": 75000,
    "fecha_evento": "2027-04-18",
    "modalidad": "full_planning",
    "clausulas_incluidas": [
      "cancelacion_prorrateada",
      "fuerza_mayor_pandemia",
      "propiedad_intelectual",
      "confidencialidad_lfpdppp",
      "responsabilidad_limitada"
    ],
    "anexos": ["brief_boda", "cotizacion_detallada"],
    "requiere_revisar_abogado_antes_firma": true,
    "estructura_pago": {
      "anticipo": "30% a la firma",
      "intermedio": "40% en D-180",
      "final": "30% en D-30"
    }
  }
}
```

## Validación pendiente

- Revisión por abogado mercantilista (CRÍTICO)
- Casos de jurisprudencia en CDMX por cancelación de bodas
- Casos con proveedores específicos (banquete, locación) y sus T&Cs
- Reglas particulares de Cancún/Tulum/San Miguel (zonas turísticas)
