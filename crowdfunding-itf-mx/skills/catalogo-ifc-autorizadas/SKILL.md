---
name: catalogo-ifc-autorizadas
description: Consulta el padrón oficial de la CNBV de instituciones de financiamiento colectivo (IFC, crowdfunding) autorizadas bajo la Ley Fintech, verifica si una plataforma está autorizada antes de invertir o pedir financiamiento y arma una ficha con tipo de operación (deuda personal, empresarial, inmobiliaria, capital, copropiedad o regalías). Usar cuando el usuario diga catálogo ifc autorizadas, catalogo_ifc_autorizadas, ¿esta plataforma de crowdfunding está autorizada?, lista de IFC CNBV, fintech autorizadas, ayuda con catálogo ifc autorizadas.
allowed-tools: Read, Write
---

# Catálogo de IFC autorizadas

## Fuente

- Padrón de la CNBV (Ley para Regular las Instituciones de Tecnología Financiera, DOF 09-03-2018). No fijes un número de IFC: cambia con autorizaciones y revocaciones; consúltalo cada vez.
- MCP `mp_cnbv_fintech` (validado en vivo contra el padrón de la CNBV; no publica RFC):
  - `cnbv_fintech_listar_ifc` — lista de IFC.
  - `cnbv_fintech_consultar_itf` — detalle de una ITF.
  - `cnbv_fintech_verificar_contraparte` — ¿la plataforma X está autorizada?
- Quejas y comportamiento: CONDUSEF (SIPRES, Buró de Entidades Financieras) — `mp_condusef_sipres` si está disponible.

## Flujo

1. Recibe nombre comercial o razón social.
2. `cnbv_fintech_verificar_contraparte`; si no aparece, búscala por razón social con `cnbv_fintech_listar_ifc`.
3. Si no está autorizada: **alerta** — operar captación de público sin autorización es ilegal; no recomiendes invertir.
4. Ficha: razón social, tipo de operaciones autorizadas, fecha de autorización (si el padrón la trae), y lo que el usuario aporte de la plataforma (tasas, plazos, comisiones). **Tasas y condiciones no vienen del padrón**: márcalas como "dato de la plataforma, no verificado".

## Output esperado

```json
{
  "operation": "catalogo-ifc-autorizadas",
  "data": {
    "consulta": "<nombre plataforma>",
    "autorizada_cnbv": true,
    "razon_social": "<del padrón>",
    "tipo_ifc": "deuda empresarial",
    "condiciones_comerciales": {"tasa_anual": null, "fuente": "usuario/plataforma, no verificado"},
    "fecha_consulta": "2026-10-15"
  },
  "vigencia_validada": true
}
```

## Casos edge

- Plataformas que operaban antes de la Ley Fintech sin haber obtenido autorización: no están autorizadas.
- Modelos novedosos (sandbox, `cnbv_fintech_listar_modelos_novedosos`): el MCP indica que no hay fuente; dilo así.
- Si el MCP falla: remite al padrón en el portal de la CNBV y pide al usuario confirmar.

## Dependencias

- `core-mexico` (RFC, mxn-formato); MCP `mp_cnbv_fintech`

No es recomendación de inversión.
