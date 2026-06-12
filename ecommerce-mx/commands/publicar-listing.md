---
description: Publica un producto nuevo en uno o todos los marketplaces (Mercado Libre, Shopify, Amazon MX) con validaciones de atributos obligatorios, foto fondo blanco y categorización correcta.
argument-hint: "[descripción del producto: marca, modelo, características]"
allowed-tools: Read, Write, Edit, Bash
---

# /ecommerce:publicar-listing

Publica producto nuevo en marketplaces: $ARGUMENTS

## Lo que hace

1. Invoca skill `mercado-libre-listings` para construir el listing ML.
2. Invoca skill `shopify-mx` para construir el producto Shopify.
3. Valida en paralelo:
   - Atributos obligatorios por categoría (cada canal tiene reglas distintas)
   - Foto principal: fondo blanco puro
   - Título: longitud, palabras prohibidas
   - Descripción: longitud, no contiene URLs / teléfonos
   - Precio: en rango de la categoría
4. Si hay errores: reporta y NO publica.
5. Si todo OK: publica en los canales especificados (default: todos).

## Cuándo usar

- Nuevo producto agregado al catálogo
- Migración de productos viejos al nuevo formato
- Listing batch (mismo producto en varios canales)

## Output esperado

```
✓ Publicación: "Apple iPhone 15 Pro 256GB"

Validaciones:
  ✓ Categoría ML: Celulares y Telefonía > Smartphones (MLM12345)
  ✓ Atributos obligatorios: 12/12 completos
  ✓ Foto principal: fondo blanco OK
  ✓ Título: 47 chars (OK, ≤60)
  ✓ Descripción: 850 chars (OK)
  ✓ Precio: $24,990 (P50 de mercado)

Publicaciones:
  • ML: MLM4321 (Premium, Envíos Full)  ✓ Publicado
  • Shopify: prod_xyz789  ✓ Publicado
  • Amazon: skipped (no credentials)

Siguientes pasos:
  • Esperar 2-3 hrs para indexación ML
  • Confirmar ranking inicial en 48 hrs
```

## Filtros

```
/ecommerce:publicar-listing iPhone 15 Pro     # publica en todos los canales
/ecommerce:publicar-listing --solo=ml         # solo Mercado Libre
/ecommerce:publicar-listing --dry-run         # valida sin publicar
```
