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

Como parte del marketplace `plugins-mx`:
```
/plugin marketplace add elias/plugins-mx
/plugin install core-mexico
```

## Para desarrolladores

Los skills en `skills/` se sincronizan desde `_shared/` en la raíz del monorepo. **No editar directamente** — modificar en `_shared/<skill>/` y correr `scripts/sync-shared.sh` para propagar.

## Integraciones (mockeables)

El plugin no asume credenciales reales. Cada skill define una interfaz que puede implementarse contra:
- Mock (default) — outputs simulados para iteración
- Sandbox del proveedor (Facturama, Gupshup, Stripe MX, Mercado Pago)
- Producción (con credenciales en `.env` del usuario)

Ver `docs/arquitectura.md` para el contrato de integración.
