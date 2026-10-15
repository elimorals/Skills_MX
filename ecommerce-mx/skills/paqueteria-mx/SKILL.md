---
name: paqueteria-mx
description: Cotización y selección de paquetería mexicana (Estafeta, DHL MX, FedEx MX, Paquetexpress, agregadores como Skydropx, 99 Minutos) según peso, dimensiones, origen, destino y urgencia. Rangos de precio ilustrativos (no tarifas oficiales), restricciones (pueblos remotos, productos prohibidos), tracking unificado, generación de guía digital, seguro recomendado por valor. Usar cuando el usuario diga cotizar envío, paquetería México, mejor paquetería, envío Estafeta DHL FedEx, cuánto cuesta enviar a [ciudad], comparar paqueterías, guía envío. NO usar para envíos internacionales mayores (ver DHL Express o FedEx International dedicado).
allowed-tools: Read, Write, Edit
---

# Paquetería en México — comparativa y cotización

5 paqueterías principales con cobertura, tarifas y restricciones distintas.

## Comparativa rápida

| Carrier | Cobertura | Tiempo entrega | Peso máx | Precio ilustrativo (3kg, CDMX→GDL) | Tracking |
|---|---|---|---|---|---|
| **Estafeta** | Nacional MX | 2-4 días | 70 kg | $145 MXN | Sí, en tiempo real |
| **DHL MX (terrestre)** | Nacional MX | 1-3 días | 70 kg | $185 MXN | Sí, premium |
| **FedEx MX** | Nacional MX | 1-3 días | 68 kg | $210 MXN | Sí, premium |
| **Agregador (Skydropx, Envia.com)** | Nacional MX (multi-carrier) | 1-5 días | 70 kg | $110-180 MXN | Sí, depende carrier |
| **99 Minutos** | CDMX, GDL, MTY (ciudades) | Same-day o next-day | 25 kg | $99 MXN (CDMX local) | Sí, GPS real-time |
| **DHL Express** | Internacional | 1-3 días | 70 kg | $850 MXN (a USA) | Sí, premium |
| **Correos de México** | Nacional MX | 5-15 días | 20 kg | $80 MXN | Limitado |

⚠ Precios **ilustrativos** (sin fuente oficial; heredados de 2025). No los uses para cotizar a un cliente: cotiza siempre en el sitio del carrier o en un agregador (Skydropx, Envia.com) con CP origen/destino, peso y medidas reales. Pesos máximos y tiempos: **verificar** por servicio.

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
| **Seguro declarado** | Porcentaje del valor declarado (verificar por carrier) |
| **Recolección a domicilio** | Cargo extra frente a entregar en sucursal (verificar) |
| **Guía de retorno** | Cargo extra (verificar) |
| **Fines de semana / festivos** | Algunos servicios no operan o cuestan más |

## Peso volumétrico — cuidado

Las paqueterías cobran el mayor entre peso real y volumétrico:

```
peso_volumetrico_kg = (largo × ancho × alto en cm) / 5000   # divisor más común; algunos servicios usan 4000 o 6000: verificar

Ejemplo: caja 30cm × 30cm × 30cm
peso_volumetrico = (30 × 30 × 30) / 5000 = 5.4 kg

Si la caja realmente pesa 2 kg, te cobran como 5.4 kg.
```

Optimización: empacar lo más compacto posible.

## Productos prohibidos / restringidos

Cada carrier publica su lista de artículos prohibidos y restringidos; revísala antes de enviar. Categorías que casi siempre tienen restricción:

- Baterías de litio (sueltas o dentro del equipo): se envían bajo reglas de mercancías peligrosas (UN3480/UN3481), con empaque y etiqueta.
- Líquidos, aerosoles, inflamables y corrosivos.
- Perecederos y productos que requieren cadena de frío.
- Armas, réplicas y municiones.
- Medicamentos (en especial controlados), que además requieren cumplir con COFEPRIS.
- Alcohol y tabaco.
- Valores (efectivo, joyería fina): solo con servicio y seguro específicos.

## Seguro

Recomendado cuando el valor de la mercancía supera lo que estarías dispuesto a perder. El costo es un porcentaje del valor declarado con un mínimo, y sin seguro la indemnización se limita a lo que diga la guía/contrato del carrier. Porcentajes, mínimos y límites: **verificar** en las condiciones de cada carrier.

Frente al consumidor, el riesgo del envío es tuyo hasta la entrega: si el paquete se pierde, debes reponer o reembolsar (Art. 92 LFPC), tengas o no seguro.

## Tracking y proactividad

Mejor práctica MX:
1. Generar guía + tracking number
2. Mandar tracking por **WhatsApp** o el canal que el cliente prefiera (con su consentimiento; ver `whatsapp-business-mx`)
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
        "seguro": 50.00,
        "total": 215.00,
        "nota": "precio y seguro ilustrativos (2% supuesto); cotizar real",
        "recomendado": true,
        "razon": "Mejor balance precio/tiempo"
      },
      {
        "carrier": "dhl_mx",
        "servicio": "Same-day",
        "tiempo_entrega": "1 día",
        "precio": 285.00,
        "seguro": 38.00,
        "total": 323.00,
        "recomendado": false,
        "razon": "Más caro sin beneficio significativo vs Estafeta para esta ruta"
      },
      {
        "carrier": "99_minutos",
        "servicio": "Next-day intercity",
        "tiempo_entrega": "Next-day",
        "precio": 199.00,
        "seguro": null,
        "total": 199.00,
        "recomendado": "alternativa",
        "razon": "Excelente tracking si urgencia, pero sin seguro"
      }
    ],
    "ahorro_posible": "Empacar más compacto reduce peso volumétrico de 1.8 a ~1.2 kg pero no cambia precio (peso real domina)"
  }
}
```

## Limitaciones

- Ningún MCP del repo cotiza paqueterías: las tarifas salen del cotizador del carrier o de un agregador.
- Tarifas empresariales se negocian por volumen; los rangos de esta skill son solo orientativos.

## Ver también

- `inventario-multicanal`
- `shopify-mx` (configurar paqueterías en Shopify)
- `mercado-libre-listings` (Mercado Envíos como alternativa)
- `mp_shopify_mx` MCP (`shopify_create_fulfillment` para registrar la guía en la orden)
