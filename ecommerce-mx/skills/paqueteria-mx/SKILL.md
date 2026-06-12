---
name: paqueteria-mx
description: Cotización y selección de paquetería mexicana (Estafeta, DHL MX, FedEx MX, paqueteX/Skydropx, 99 Minutos) según peso, dimensiones, origen, destino y urgencia. Tarifas referenciales 2026, restricciones (pueblos remotos, productos prohibidos), tracking unificado, generación de guía digital, seguro recomendado por valor. Usar cuando el usuario diga cotizar envío, paquetería México, mejor paquetería, envío Estafeta DHL FedEx, cuánto cuesta enviar a [ciudad], comparar paqueterías, guía envío. NO usar para envíos internacionales mayores (ver DHL Express o FedEx International dedicado).
allowed-tools: Read, Write, Edit
---

# Paquetería en México — comparativa y cotización

5 paqueterías principales con cobertura, tarifas y restricciones distintas.

## Comparativa rápida

| Carrier | Cobertura | Tiempo entrega | Peso máx | Precio promedio (3kg, CDMX→GDL) | Tracking |
|---|---|---|---|---|---|
| **Estafeta** | Nacional MX | 2-4 días | 70 kg | $145 MXN | Sí, en tiempo real |
| **DHL MX (terrestre)** | Nacional MX | 1-3 días | 70 kg | $185 MXN | Sí, premium |
| **FedEx MX** | Nacional MX | 1-3 días | 68 kg | $210 MXN | Sí, premium |
| **paqueteX (vía Skydropx)** | Nacional MX (multi-carrier) | 1-5 días | 70 kg | $110-180 MXN | Sí, depende carrier |
| **99 Minutos** | CDMX, GDL, MTY (ciudades) | Same-day o next-day | 25 kg | $99 MXN (CDMX local) | Sí, GPS real-time |
| **DHL Express** | Internacional | 1-3 días | 70 kg | $850 MXN (a USA) | Sí, premium |
| **Correos de México** | Nacional MX | 5-15 días | 20 kg | $80 MXN | Limitado |

⚠ Precios referencial 2025. Para 2026: validar con cotizadores en línea de cada carrier.

## Cuándo usar cada uno

### Estafeta
- Default para nacional
- Buena cobertura en pueblos
- Tarifa balanceada
- Devoluciones automáticas con servicio integrado

### DHL MX (terrestre, no Express)
- Cuando el cliente paga premium por velocidad
- Mejor tracking del mercado MX
- Buen servicio en zonas industriales

### FedEx MX
- Similar a DHL pero más caro
- Mejor para B2B (clientes empresariales)

### Skydropx / Envia.com (multi-carrier)
- Comparador en tiempo real
- Permite elegir el más barato por ruta
- Plataforma única para imprimir guías de todos los carriers
- API friendly para developers

### 99 Minutos
- Same-day delivery en CDMX, GDL, MTY
- Crucial para D2C de alta gama (relojes, joyería)
- Precio bajo en local CDMX ($99 MXN)
- No cubre fuera de áreas metropolitanas

### Correos de México
- Solo para libros o productos baratos no urgentes
- Pueblos remotos donde otras paqueterías no llegan
- Mucho más lento

## Factores que cambian el precio

| Factor | Impacto |
|---|---|
| **Peso volumétrico** vs real | El que sea mayor cuenta. Volumétrico = (L×A×H)/5000 cm³ |
| **Distancia (zona)** | Misma ciudad = barato. Cross-México = caro |
| **Urgencia** | Express duplica el precio |
| **Seguro declarado** | +$5-15 MXN por cada $1k MXN declarado |
| **Recolección a domicilio** | +$30-80 MXN vs llevarlo al centro |
| **Devolución asegurada** | +$50-150 MXN |
| **Fines de semana / festivos** | Algunos no operan; los que sí, +20% |

## Peso volumétrico — cuidado

Las paqueterías cobran el mayor entre peso real y volumétrico:

```
peso_volumetrico_kg = (largo × ancho × alto en cm) / 5000

Ejemplo: caja 30cm × 30cm × 30cm
peso_volumetrico = (30 × 30 × 30) / 5000 = 5.4 kg

Si la caja realmente pesa 2 kg, te cobran como 5.4 kg.
```

Optimización: empacar lo más compacto posible.

## Productos prohibidos / restringidos

| Tipo | Estafeta | DHL | FedEx | 99 Min |
|---|---|---|---|---|
| Líquidos (>250ml) | Con permiso | Restricted | Restricted | OK |
| Baterías litio | Solo con UN3481 | Solo con UN3481 | Solo con UN3481 | OK pequeñas |
| Joyería > $5k MXN | Con seguro obligatorio | OK | OK | Con cuidado |
| Productos perecederos | NO | Solo refrigerados | Solo refrigerados | OK same-day |
| Armas (incluso de juguete) | NO | NO | NO | NO |
| Medicamentos controlados | Solo farmacéuticas | Solo farmacéuticas | Solo farmacéuticas | NO |
| Tabaco / alcohol | NO | Con permiso | Con permiso | NO |

## Seguro

Recomendado para productos > $1,500 MXN:
- Estafeta: 2% del valor declarado (mínimo $20 MXN)
- DHL: 1.5% del valor (mínimo $25 MXN)
- FedEx: 1.5% del valor (mínimo $30 MXN)
- Skydropx: variable según carrier elegido

Sin seguro: pérdida o daño limita reembolso a ~$1,500 MXN máximo.

## Tracking y proactividad

Mejor práctica MX:
1. Generar guía + tracking number
2. Mandar tracking por **WhatsApp** al cliente (mexicanos abren WA, no email)
3. Notificar a las 24h, 48h y al entregar
4. Si pasa 48h sin movimiento → escalar con la paquetería antes que el cliente se queje

## Output estructurado

```json
{
  "cotizacion_envio": {
    "origen": {"cp": "06700", "ciudad": "CDMX"},
    "destino": {"cp": "44100", "ciudad": "GDL"},
    "paquete": {
      "peso_real_kg": 3.0,
      "dimensiones_cm": {"l": 30, "a": 20, "h": 15},
      "peso_volumetrico_kg": 1.8,
      "peso_facturable_kg": 3.0,
      "valor_declarado_mxn": 2500.00
    },
    "opciones": [
      {
        "carrier": "estafeta",
        "servicio": "Día siguiente",
        "tiempo_entrega": "1-2 días",
        "precio": 165.00,
        "seguro_incluido": 50.00,
        "total": 215.00,
        "recomendado": true,
        "razon": "Mejor balance precio/tiempo"
      },
      {
        "carrier": "dhl_mx",
        "servicio": "Same-day",
        "tiempo_entrega": "1 día",
        "precio": 285.00,
        "seguro_incluido": 38.00,
        "total": 323.00,
        "recomendado": false,
        "razon": "Más caro sin beneficio significativo vs Estafeta para esta ruta"
      },
      {
        "carrier": "99_minutos",
        "servicio": "Next-day intercity",
        "tiempo_entrega": "Next-day",
        "precio": 199.00,
        "seguro_incluido": null,
        "total": 199.00,
        "recomendado": "alternativa",
        "razon": "Excelente tracking si urgencia, pero sin seguro"
      }
    ],
    "ahorro_posible": "Empacar más compacto reduce peso volumétrico de 1.8 a ~1.2 kg pero no cambia precio (peso real domina)"
  }
}
```

## Validación pendiente

- Tarifas 2026 vigentes por carrier (cambian trimestralmente)
- Restricciones productos actualizadas
- Cobertura nuevas paqueterías (Cargamos, Mercado Envíos B2C, etc.)
- Tarifas reales empresariales (volúmenes grandes negocian -20% a -40%)

## Ver también

- `inventario-multicanal`
- `shopify-mx` (configurar paqueterías en Shopify)
- `mercado-libre-listings` (Mercado Envíos como alternativa)
- `mp_shopify_mx` MCP
