---
name: catalogo-tigie-busqueda
description: Ayuda a ubicar la fracción arancelaria TIGIE (8 dígitos + NICO de 2) de un producto por su descripción, y a consultar arancel, regulaciones no arancelarias y cupos en fuentes oficiales. Usar cuando el usuario diga catalogo tigie busqueda, fracción arancelaria de un producto, clasificar mercancía, qué arancel paga, código NICO, partida arancelaria, HS code México.
allowed-tools: Read, Write
---

# Búsqueda en catálogo TIGIE

La clasificación arancelaria es responsabilidad del importador y su agente aduanal; un error causa multas. Esta skill propone candidatas, no clasifica en firme.

## Cómo trabajar

1. Pide descripción técnica: material, función, uso, composición (%), presentación. Con eso razona con las Reglas Generales de Interpretación de la TIGIE (capítulo → partida → subpartida).
2. Propón 1-3 fracciones candidatas de 8 dígitos con su NICO (2 dígitos adicionales, vigente desde 28-dic-2020) y explica la regla que lleva a cada una.
3. Remite a consultar en fuente oficial: SNICE (snice.gob.mx) o SIICEX, y las Notas Explicativas de la TIGIE (DOF). No hay catálogo precargado en el plugin ni MCP de aduanas.
4. Para cada candidata, revisa: IGI vigente según origen (con o sin tratado), regulaciones no arancelarias (NOM, permisos SE/COFEPRIS/SENASICA/SEDENA), padrón sectorial (Anexo 10 RGCE) y cuotas compensatorias.
5. Si hay duda real, recomienda dictamen del agente aduanal o consulta de clasificación ante la ANAM/SAT.

## Aviso 2026

El decreto DOF 29-dic-2025 (vigente 01-ene-2026) subió el IGI de ~1,463 fracciones a 5%-50% para orígenes sin tratado, y el DOF 23-abr-2026 volvió a ajustar la TIGIE. Tasas de memoria pueden estar desactualizadas: confirma siempre en SNICE (confianza media en el conteo de fracciones; fuente: resúmenes de despachos, no texto DOF íntegro).

## Output esperado

```json
{
  "operation": "catalogo-tigie-busqueda",
  "data": {"candidatas": [{"fraccion": "", "nico": "", "descripcion": "", "razon_rgi": "", "igi_sin_tratado": null, "rrna": []}]},
  "vigencia_validada": false
}
```

## Casos edge

- Kits, juegos o partes → aplicar RGI 3 y 2a; avisarlo.
- Producto descrito solo por marca o nombre comercial → pedir ficha técnica.
- Fracción cambió por enmienda → no reutilizar códigos de años anteriores sin verificar.

## Dependencias

- `cotizador-pre-importacion` para el costo una vez definida la fracción
