---
name: cfdi-publico-global
description: Emisión de CFDI público global consolidado para ventas B2C de restaurantes mexicanos donde el cliente NO proporciona RFC (mayoría de casos en restaurante). El SAT obliga a emitir un CFDI consolidado mensual a "Público en general" con RFC genérico XAXX010101000. Calcula cómo distribuir las ventas del mes, qué método pago usar (efectivo, TDC, mixto), formato del CFDI con leyenda obligatoria. Usar cuando el usuario diga CFDI público general, factura sin RFC, cliente no pidió factura, cierre mensual ventas. NO usar para CFDI individual al cliente (cfdi-emision) ni para B2B.
allowed-tools: Read, Write, Edit
---

# CFDI Público Global — restaurantes

## ¿Qué es y por qué emitirlo?

México requiere CFDI por **TODA** venta (Art. 29 CFF). Cuando el cliente no pide factura individual:
- El restaurante debe emitir un **CFDI consolidado mensual** "a público en general"
- RFC del receptor: `XAXX010101000` (genérico)
- Razón social: "PUBLICO EN GENERAL"
- Importe: suma de ventas del periodo sin factura individual

## Cuándo emitir

- **1 CFDI mensual** consolidado (el más común)
- Algunos optan por **CFDI diario** (más operativo pero más trabajo)
- **NO se puede acumular más de 1 mes** (regla SAT)

## Estructura del CFDI consolidado

```json
{
  "tipo_comprobante": "I",
  "fecha": "2026-03-31T23:59:59",
  "subtotal": 145000.00,
  "moneda": "MXN",
  "metodo_pago": "PUE",
  "forma_pago": "01",  // efectivo (el más común para restaurantes)
  "uso_cfdi": "S01",  // Sin efectos fiscales (XAXX no acumula)
  "exportacion": "01",  // No es operación de exportación

  "emisor": {
    "rfc": "MAJG800101XYZ",
    "nombre": "Restaurante Demo SA de CV",
    "regimen_fiscal": "601",
    "cp_lugar_expedicion": "06700"
  },

  "receptor": {
    "rfc": "XAXX010101000",
    "nombre": "PUBLICO EN GENERAL",
    "regimen_fiscal": "616",  // Sin obligaciones fiscales
    "cp_domicilio_fiscal": "06700",
    "uso_cfdi": "S01"
  },

  "conceptos": [
    {
      "clave_prod_serv": "90101501",
      "cantidad": 1,
      "clave_unidad": "ACT",
      "descripcion": "VENTAS EN GENERAL CORRESPONDIENTES A MARZO 2026 — ALIMENTOS Y BEBIDAS PREPARADOS",
      "valor_unitario": 145000.00,
      "importe": 145000.00,
      "objeto_imp": "02"
    }
  ],

  "impuestos_trasladados": [
    {
      "tipo": "IVA",
      "tasa": 0.16,
      "importe": 23200.00
    }
  ],

  "total": 168200.00,

  "leyenda_publico_general": "FACTURA GLOBAL CORRESPONDIENTE A VENTAS DE PÚBLICO EN GENERAL DEL 01 DE MARZO AL 31 DE MARZO DE 2026",

  "periodicidad": "30",  // Mensual
  "meses_aplicables": "03",
  "año": "2026"
}
```

## Mezcla de formas de pago

Si el mes hubo ventas en efectivo + tarjeta + transferencia:
- Si > 80% efectivo: usar `forma_pago: "01"` (efectivo)
- Si > 80% tarjeta: usar `forma_pago: "04"` (tarjeta de crédito) o `"28"` (débito)
- Si mixto: 1 CFDI por cada forma de pago o usar `"99"` (por definir, raro)

⚠ Mejor práctica: **1 CFDI por forma de pago** para auditoria limpia.

## Cómo calcular cuánto ir al CFDI consolidado

```
ventas_totales_mes = ventas_directas + ventas_aggregators_b2c + ventas_efectivo
ventas_con_cfdi_individual = ventas_b2b + ventas_con_rfc_solicitado

ventas_publico_global = ventas_totales_mes - ventas_con_cfdi_individual
```

Ejemplo restaurante medio (200 mesas/mes):
- Ventas totales mes: $480,000 MXN
- Clientes que pidieron factura: 24 (12% — restaurante MX típico)
- Ventas con CFDI individual: $48,000
- **Ventas a Público en General**: $432,000 → 1 CFDI consolidado

## Implicaciones para el restaurante

### Acumulable para ISR
- SÍ, ingreso del restaurante incluye TODAS las ventas (con o sin factura individual)
- El CFDI consolidado certifica el monto ante SAT

### IVA trasladado
- Sí, IVA 16% sobre ventas (excepto frontera 8%)
- Reportado en CFDI consolidado

### IVA acreditable
- Sí, IVA pagado en gastos
- Documentado con CFDIs recibidos (proveedores)

### Estado financiero
- El CFDI consolidado entra como "Ingreso por ventas" del mes
- Conciliable con depósitos bancarios + efectivo en caja

## Casos edge

### Cliente pide factura el siguiente mes
- Si fue cancelada y emite individual: descontar del consolidado
- Si NO fue cancelada: emisión individual + el monto ya está en consolidado del mes anterior (riesgo de doble facturación)

**Mejor práctica**: si cliente pide factura post-evento, hacer cancelación del consolidado + emisión individual.

### Aggregators (Rappi, UberEats, etc.)
- Aggregator factura al cliente final
- Restaurante factura al aggregator (NO al cliente final)
- En el CFDI consolidado del restaurante NO incluir ventas via aggregator
- Estas se facturan al aggregator con su RFC específico

### Empleados que comen en el restaurante
- Costo del comedor = costo, no venta
- No emite CFDI a empleado
- No entra en consolidado

### Ventas a cuenta de gastos (corporate)
- Cliente paga con TDC corporativa pero NO pide factura
- En MX, esto es ilegal porque la empresa debería pedir factura para deducir
- Si igualmente no la pidió, entra en consolidado

## Output estructurado

```json
{
  "cfdi_publico_global": {
    "periodo": "2026-03",
    "ventas_totales_mxn": 480000.00,
    "ventas_con_cfdi_individual_mxn": 48000.00,
    "ventas_via_aggregators_mxn": 65000.00,
    "ventas_consolidado_mxn": 367000.00,
    "cfdi_emitido": {
      "uuid": "ABCD-1234-...",
      "fecha_emision": "2026-03-31T23:59:59",
      "subtotal_mxn": 316379.31,
      "iva_mxn": 50620.69,
      "total_mxn": 367000.00,
      "forma_pago_predominante": "01_efectivo",
      "leyenda": "FACTURA GLOBAL CORRESPONDIENTE A VENTAS DE PÚBLICO EN GENERAL DEL 01 DE MARZO AL 31 DE MARZO DE 2026"
    },
    "cfdis_aggregators_pendientes": [
      {"aggregator": "rappi", "ingreso_neto_mxn": 28000, "cfdi_pendiente": true},
      {"aggregator": "ubereats", "ingreso_neto_mxn": 14500, "cfdi_pendiente": true}
    ],
    "siguientes_pasos": [
      "Emitir CFDI a Rappi (RFC REP170913U41) por $28,000",
      "Emitir CFDI a UberEats por $14,500",
      "Conciliar con depósitos bancarios + efectivo en caja"
    ]
  }
}
```

## Validación pendiente

- Leyenda obligatoria CFDI Público en General 2026 (formato exacto SAT)
- Reglas específicas RMF 2026 sobre periodicidad
- Casos en que SAT pide aclaración (alta diferencia entre consolidado y depósitos)
- Diferencias por régimen (PM general, PFAE, RESICO PM)
