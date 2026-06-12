---
name: mercado-libre-listings
description: Gestión de listings en Mercado Libre México con criterio MX real (categorización correcta CBT vs Classic, políticas de envío gratis, garantías SAT-friendly, atributos obligatorios por categoría como GTIN/SKU/dimensiones, prevención de pausas automáticas por reputación). Optimiza títulos, descripciones, fotos y atributos para ranking ML. Usar cuando el usuario diga publicar en ML, listing mercado libre, optimizar listado ML, atributos ML, fotos ML, ranking ML, mercado libre catálogo, mejorar listing. NO usar para pricing (otro skill mercado-libre-pricing), ni para mensajes de compradores (eso es el MCP directo).
allowed-tools: Read, Write, Edit
---

# Mercado Libre — Gestión de listings (México)

Mercado Libre es el marketplace dominante en México (~50% market share del ecommerce). Las reglas son específicas y cambian periódicamente.

## Modalidades de venta

| Modalidad | Comisión | Envío gratis obligatorio | Cuándo usarla |
|---|---|---|---|
| **Clásica** | 13% (categoría general) | No | Productos < $299 MXN o catálogo nuevo |
| **Premium** | 17% (categoría general) | Sí (envío gratis por ML) | Productos > $299 MXN para ranking mejor |

⚠ Las comisiones varían por categoría. Verificar `mp_mercado_libre.get_category_attributes(category_id)` para conocer comisión real.

## Anatomía de un listing ganador

### Título (máx 60 caracteres)
- Marca + Modelo + Característica clave + Color/Talla
- Sin signos de puntuación al inicio
- Sin "OFERTA", "PROMOCIÓN" (ML lo penaliza)
- Ejemplo: `Apple iPhone 15 Pro 256GB Titanio Natural Liberado`

### Fotos (mínimo 3, máximo 12)
- **Primera foto**: producto solo, fondo blanco puro (#FFFFFF), centrado, sin texto
- Resolución mínima: 1200×1200 px
- Formato: JPG o PNG sin compresión agresiva
- Sin marcas de agua, logos del seller, ni teléfonos
- Mostrar producto en uso/escala en fotos 2-3

### Atributos obligatorios

Los atributos varían por categoría. Categorías comunes:

**Celulares**:
- Marca, Modelo, Color, Capacidad GB, Estado (Nuevo/Usado), GTIN/EAN, Liberado (Sí/No), Año del modelo, Tipo de pantalla

**Ropa**:
- Marca, Talla, Color, Material, Género, Temporada, Estilo, Tipo de manga

**Hogar**:
- Marca, Modelo, Dimensiones, Color, Material, Garantía del fabricante

⚠ **Atributo faltante = listing pausado por ML automáticamente**. Validar con `mp_mercado_libre.get_category_attributes(category_id)` antes de publicar.

### Descripción
- 500-3000 caracteres
- Empezar con beneficios (no specs)
- Bullet points con ✓ (ML los renderiza)
- Incluir: garantía, política de devolución, contenido del paquete
- NO incluir: precio (cambia), teléfono (prohibido), email (prohibido), URLs externas

## Tipos de publicación

### Catálogo (CBT — Comprar y Vender)
- Listings competing por un catálogo único de ML
- Mejor ranking si compites por precio + reputación
- Foto y descripción provienen del catálogo central, no las tuyas
- Para productos commodity (Apple, Samsung, Sony)

### Listing propio (Classic)
- Tu listing único con tus fotos y descripción
- Mejor para producto único o marca propia
- Compite por algoritmo de búsqueda ML

## Reputación del vendedor

ML mide y muestra públicamente:

| Métrica | Threshold mínimo |
|---|---|
| Ventas concluidas | > 90% |
| Reclamos | < 3% últimos 60 días |
| Tiempo de despacho | < 24 hrs (Mercado Envíos Full) |
| Cancelaciones del vendedor | < 2% |
| Calificación promedio | > 4.5 estrellas |

Caer de "MercadoLíder Platinum" → "Estándar" reduce visibilidad ~40%.

## Mercado Envíos

| Tipo | Cuándo usar | Pros | Contras |
|---|---|---|---|
| **Mercado Envíos Full** | Volumen alto | Almacenamiento ML, envío 24h, badge "Full" | Comisión adicional 5% |
| **Mercado Envíos Flex** | Mediano volumen | Recoge ML en tu domicilio | Restringido por zona |
| **Mercado Envíos Place** | Bajo volumen | Llevas tú al centro logístico | Más barato |
| **A coordinar** | Esporádico | Mayor control | Sin badge ML, ranking bajo |

## Pausas automáticas y cómo evitarlas

| Causa | Cómo prevenir |
|---|---|
| Atributo crítico faltante | Validar con `get_category_attributes` antes de publicar |
| Categoría incorrecta | Usar `predict_category(title, description)` |
| Foto con texto/marca de agua | Pasar fotos por OCR previo a publicar |
| Precio fuera de rango categoría | Revisar `category.price_range` |
| Stock 0 por > 7 días | Activar reposición automática |
| 3+ reclamos no resueltos | Atender mensajes < 8 hrs |

## Output estructurado

```json
{
  "listing": {
    "id": "MLM1234567890",
    "title": "...",
    "category_id": "MLM12345",
    "modalidad": "premium",
    "precio": 599.00,
    "stock": 25,
    "envio": "full",
    "atributos_completos": true,
    "fotos_count": 5,
    "validaciones": {
      "titulo_ok": true,
      "fotos_fondo_blanco": true,
      "atributos_obligatorios": "all_present",
      "descripcion_caracteres": 850,
      "prohibidos_detectados": []
    },
    "ranking_estimado": "alto"
  },
  "advertencias": [],
  "siguientes_pasos": [
    "Activar 'Mercado Envíos Full' para badge"
  ]
}
```

## Validación pendiente para producción

- Comisiones 2026 actualizadas por categoría
- Políticas Mercado Líder vigentes
- Reglas de envío gratis 2026
- Lista de palabras prohibidas en título/descripción
- Validación con seller MX real (al menos 1 mes operando)

## Ver también

- `mercado-libre-pricing` — calcular precio óptimo
- `inventario-multicanal` — sincronizar stock entre canales
- `mp_mercado_libre` MCP — API directa
