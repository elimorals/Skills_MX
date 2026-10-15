# core-mexico

Plugin base del monorepo `plugins-mx`. Capa fundacional reutilizada por todos los plugins verticales.

## Skills incluidos

| Skill | Propósito |
|---|---|
| `cfdi-emision` | Emisión de CFDI 4.0 con validaciones SAT, catálogos, manejo de cancelación |
| `iva-retenciones-mx` | Cálculo correcto de IVA (16%, 8% fronterizo, 0%, exento) y retenciones por régimen |
| `rfc-validacion` | Validación estructural de RFC (PF/PM), homoclave, RFCs genéricos |
| `whatsapp-business-mx` | Templates aprobables por Meta, ventanas 24h, tone of voice MX |
| `compliance-lfpdppp` | Aviso de privacidad, derechos ARCO, transferencias, manejo de datos sensibles |
| `mxn-formato` | Formato consistente de moneda MXN, conversión a letra para contratos |

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX
```

`core-mexico` es la dependencia de todos los verticales. Sus MCPs se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez.

## Para desarrolladores

Los skills en `skills/` se sincronizan desde `_shared/` en la raíz del monorepo. **No editar directamente** — modificar en `_shared/<skill>/` y correr `scripts/sync-shared.sh` para propagar.

## MCPs e integraciones

`.mcp.json` declara: `banxico`, `facturama` (`mp_facturama_extendido`), `mercadopago`, `mercadolibre`, `curp_renapo`, `banxico_cep`, `sat_portal`, `conekta`, `aspel_contpaqi`.

- **Sin credenciales**: el MCP responde datos de ejemplo marcados `simulated: true`.
- **Con credenciales**: consulta al proveedor real; cualquier error se propaga como error tipado, nunca hay fallback silencioso a datos de ejemplo.
- `PLUGINS_MX_MOCK=1` fuerza el modo de ejemplo.

Estado de cada MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md). Arquitectura: [`docs/architecture/arquitectura.md`](../docs/architecture/arquitectura.md).
