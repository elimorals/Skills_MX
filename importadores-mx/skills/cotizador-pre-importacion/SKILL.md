---
name: cotizador-pre-importacion
description: Estima el costo puesto en almacén (landed cost) de una importación definitiva a México por fracción arancelaria TIGIE - valor en aduana, IGI, DTA, IVA de importación, prevalidación, flete, seguro y honorarios del agente aduanal. Usar cuando el usuario diga cotizador pre importacion, cuánto pago de impuestos por importar, costo de importar de China, calcular IGI, landed cost, cuánto me cuesta traer mercancía, arancel de importación 2026.
allowed-tools: Read, Write
---

# Cotizador Pre Importación

Estimación previa al despacho. El cálculo definitivo lo hace el agente aduanal en el pedimento; esto es orientativo y requiere validación profesional.

## Datos que pedir

Fracción arancelaria (8 dígitos + NICO de 2), país de origen y si hay certificado de origen de un tratado (T-MEC, TLCUE, CPTPP, etc.), valor factura y moneda, INCOTERM, flete, seguro, tipo de cambio del DOF del día de pago (no del día de compra).

## Cálculo (importación definitiva, clave A1)

1. **Valor en aduana** = valor de transacción + incrementables (flete y seguro hasta el puerto mexicano, comisiones, embalajes) — Art. 64-65 Ley Aduanera. Con FOB/EXW suma flete y seguro internacionales; con CIF ya vienen.
2. **IGI** = valor en aduana × tasa de la TIGIE vigente para la fracción y el origen. Con certificado de origen válido aplica la preferencia del tratado (a menudo 0%).
3. **DTA** = 8 al millar del valor en aduana (Art. 49 fr. I LFD). Las cuotas fijas o mínimas (tratados con preferencia, temporales) se actualizan cada año en el Anexo 19 de la RMF: **verificar** el monto 2026 ahí antes de usarlo.
4. **IVA de importación** = 16% × (valor en aduana + IGI + DTA + cuotas compensatorias + IEPS, si aplica) — Art. 27 LIVA. El estímulo de región fronteriza no aplica a la importación.
5. **Prevalidación electrónica** (Art. 16-A Ley Aduanera): contraprestación fija por pedimento más IVA; el monto lo publica el SAT, **verificar** el vigente.
6. Suma honorarios del agente aduanal, maniobras y almacenaje (cotización del agente; llevan CFDI propio con IVA).

### Ejemplo (verificado aritméticamente)

Valor en aduana $100,000, fracción sujeta a IGI 35%, origen sin tratado:
IGI $35,000 · DTA $800 · base IVA $135,800 · IVA $21,728 · total contribuciones $57,528 (sin prevalidación ni honorarios).

## Cambios 2026 a revisar siempre

- **Aranceles a países sin tratado**: decreto que modifica la TIGIE (DOF 29-dic-2025, vigente 01-ene-2026) subió el IGI de ~1,463 fracciones (textil, calzado, acero, aluminio, autopartes, plásticos, entre otras) a tasas de 5% a 50%, mayoría 35%. Un decreto posterior (DOF 23-abr-2026) ajustó la TIGIE y el PROSEC. Confianza media (fuentes: resúmenes de EY, Baker McKenzie, Galicia; no se revisó el texto DOF íntegro). Consulta la tasa de cada fracción en el SNICE o el SIICEX antes de cotizar.
- **Textil y confección**: el decreto DOF 19-dic-2024 (35% a 138 fracciones de confección, 15% a 17 textiles, y su exclusión de la importación temporal IMMEX) tenía vigencia hasta abril de 2026; **verificar** qué quedó vigente tras el decreto de abril de 2026.
- **Reforma a la Ley Aduanera** (DOF 19-nov-2025, vigente 01-ene-2026): expediente electrónico obligatorio (CFDI, pagos, contratos, análisis de valor), manifestación de valor electrónica, mayor responsabilidad del agente aduanal y multas más altas.

## Output esperado

```json
{
  "operation": "cotizador-pre-importacion",
  "data": {"valor_aduana": 0, "igi": 0, "dta": 0, "iva": 0, "prevalidacion": null, "otros": 0, "total": 0},
  "fuentes_tasas": ["TIGIE vía SNICE, fecha de consulta"],
  "vigencia_validada": false
}
```

## Casos edge

- Fracción sin NICO o sin origen → pedir al usuario; no supongas la tasa.
- Mercancía con regulaciones no arancelarias (NOM, permisos, cupos, padrón sectorial) → avisa que el despacho puede detenerse aunque el cálculo esté bien.
- Cuotas compensatorias (antidumping, frecuentes en origen China) → revisar resolución vigente de la Secretaría de Economía.
- Este plugin no tiene MCP de aduanas: las tasas las aporta el usuario o se consultan en SNICE; marca `vigencia_validada: false` si no se verificaron.

## Dependencias

- `core-mexico` (mxn-formato, tipo de cambio Banxico)
