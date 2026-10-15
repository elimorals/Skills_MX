---
name: mercado-libre-listings
description: Gestión de publicaciones en Mercado Libre México con criterio MX real (publicación en catálogo vs publicación propia, tipo Clásica vs Premium, envío gratis, garantía conforme a LFPC, información comercial NOM-050, atributos obligatorios por categoría como GTIN/SKU/dimensiones, prevención de pausas automáticas por reputación). Optimiza títulos, descripciones, fotos y atributos para ranking ML. Usar cuando el usuario diga publicar en ML, listing mercado libre, optimizar listado ML, atributos ML, fotos ML, ranking ML, mercado libre catálogo, mejorar listing. NO usar para pricing (otro skill mercado-libre-pricing), ni para mensajes de compradores (eso es el MCP directo).
allowed-tools: Read, Write, Edit
---

# Mercado Libre — Gestión de listings (México)

Mercado Libre es el marketplace más grande de México. Sus reglas cambian varias veces al año: trata lo de abajo como guía y confirma lo crítico en el panel del vendedor o en la ayuda oficial.

## Tipos de publicación

| Tipo | Qué ofrece al comprador | Cargo por venta | Cuándo usarla |
|---|---|---|---|
| **Clásica** | Exposición estándar | Menor | Margen ajustado, producto sin necesidad de MSI |
| **Premium** | Más exposición y meses sin intereses | Mayor | Ticket alto donde los MSI convierten |

- El cargo por venta depende de categoría y tipo, y hay cargo fijo por unidad en productos de bajo precio. **No** uses porcentajes memorizados: cálculo en `mercado-libre-pricing`.
- El envío gratis lo determina el **precio** del producto (umbral vigente en la ayuda de ML), no el tipo de publicación. **Verificar** umbral actual.

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

⚠ Atributos obligatorios faltantes impiden publicar o bajan la calidad de la publicación. El MCP `mp_mercado_libre` no tiene tool de atributos: consulta el formulario de publicación del panel, o la API pública de ML `GET /categories/{category_id}/attributes` (atributos con tag `required`). Para revisar una publicación existente usa `mercadolibre_get_item`.

### Información comercial obligatoria (NOM-050-SCFI-2004)
Productos que se venden en México deben informar en español: nombre/denominación genérica, cantidad, nombre y domicilio del fabricante o importador, país de origen, instrucciones y advertencias cuando apliquen, y garantía si se ofrece. Alimentos y bebidas preenvasados además deben cumplir NOM-051-SCFI/SSA1-2010 (sellos de advertencia y leyendas; las fotos de la etiqueta deben mostrarlos). Productos eléctricos/electrónicos pueden requerir certificado NOM (p. ej. NOM-001-SCFI, NOM-019-SCFI) que ML puede pedir. **Verificar** qué NOM aplica por producto con el proveedor o un organismo de certificación.

### Descripción
- 500-3000 caracteres
- Empezar con beneficios (no specs)
- Bullet points con ✓ (ML los renderiza)
- Incluir: garantía (plazo, qué cubre y cómo hacerla válida — Art. 77-78 LFPC), contenido del paquete
- Devoluciones: en ventas a distancia el consumidor puede revocar la compra dentro de 5 días hábiles desde que recibe el bien (Art. 56 LFPC; flete a su cargo). ML aplica además su propia política de devoluciones, que suele ser más amplia: **verificar** la vigente
- NO incluir: precio (cambia), teléfono (prohibido), email (prohibido), URLs externas

## Tipos de publicación

### Publicación en catálogo
- Varias ofertas compiten por una ficha única de producto de ML (gana la "buy box")
- Mejor ranking si compites por precio + reputación
- Foto y descripción provienen del catálogo central, no las tuyas
- Para productos commodity (Apple, Samsung, Sony)

### Publicación propia (fuera de catálogo)
- Tu listing único con tus fotos y descripción
- Mejor para producto único o marca propia
- Compite por algoritmo de búsqueda ML

## Reputación del vendedor

ML mide y muestra públicamente un termómetro con tres métricas principales: **reclamos**, **cancelaciones por el vendedor** y **despachos con demora**, sobre una ventana móvil. Los umbrales por color y por nivel MercadoLíder cambian: consúltalos con `mercadolibre_get_seller_reputation` (devuelve `seller_reputation`, nivel y métricas) y en la ayuda oficial. Una reputación baja reduce exposición; ML no publica un porcentaje, no lo inventes.

## Mercado Envíos

| Tipo | Cuándo usar | Pros | Contras |
|---|---|---|---|
| **Mercado Envíos Full** | Volumen alto | Almacenamiento ML, entrega rápida, badge "Full" | Cargos de almacenamiento y operación propios (verificar tarifas) |
| **Mercado Envíos Flex** | Mediano volumen | Recoge ML en tu domicilio | Restringido por zona |
| **Mercado Envíos (colecta / drop-off en agencia)** | Bajo-mediano volumen | ML recoge o llevas a punto de entrega | Menor velocidad que Full |
| **A coordinar** | Esporádico | Mayor control | Sin badge ML, ranking bajo |

## Pausas automáticas y cómo evitarlas

| Causa | Cómo prevenir |
|---|---|
| Atributo obligatorio faltante | Revisar el formulario del panel o `GET /categories/{id}/attributes` antes de publicar |
| Categoría incorrecta | Usar el predictor de categoría del panel o `GET /sites/MLM/domain_discovery/search?q=<título>` |
| Foto con texto/marca de agua | Revisar fotos antes de publicar |
| Producto prohibido o que requiere permiso (COFEPRIS, NOM) | Revisar políticas de artículos prohibidos de ML |
| Stock 0 | Reponer con `mercadolibre_update_stock` o pausar con `mercadolibre_pause_item` |
| Preguntas sin responder | `mercadolibre_list_questions` / `mercadolibre_answer_question` |

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

## Limitaciones

- El MCP `mp_mercado_libre` está "real sin validar (requiere credenciales OAuth)": sin app de ML configurada, trabaja con datos que pegue el usuario.
- Cargos, umbral de envío gratis y niveles de reputación: verificar en la ayuda oficial de ML al momento de publicar.

## Ver también

- `mercado-libre-pricing` — calcular precio óptimo
- `inventario-multicanal` — sincronizar stock entre canales
- `mp_mercado_libre` MCP — tools `mercadolibre_*`
