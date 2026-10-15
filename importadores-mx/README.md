# importadores-mx

Plugin para PYMES importadoras: cotizador pre-importación (IGI + IVA + DTA + prevalidación), catálogo TIGIE, comparador INCOTERMS, tracking pedimentos, acreditación IVA, compliance padrón importadores, IMMEX básico. Score 7.5/10. Mercado: 50k importadores.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install importadores-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `cotizador-pre-importacion`
2. `catalogo-tigie-busqueda`
3. `comparador-incoterms`
4. `pedimento-tracker`
5. `acreditacion-iva-importacion`

## Comandos

- `/importadores:cotizador`
- `/importadores:catalogo`
- `/importadores:comparador`
- `/importadores:pedimento`
