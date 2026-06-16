# mp_infonavit_patronal — activación del path Playwright real

> Spec opt-in para clientes B2B. Mock-first es el default — todo corre sin
> credenciales con respuestas marcadas `simulated: true`.

## Resumen

El portal **INFONAVIT Empresarial** (también llamado "Portal Patronal") usa
autenticación con usuario + contraseña del responsable patronal, opcionalmente
con e.firma vigente para operaciones de escritura.

## Variables de entorno

| Variable | Descripción |
|---|---|
| `INFONAVIT_RFC_PATRONAL` | RFC del patrón |
| `INFONAVIT_USUARIO` | Usuario del Portal Empresarial |
| `INFONAVIT_PASSWORD` | Contraseña |
| `INFONAVIT_EFIRMA_CERT` | (opcional) .cer e.firma para operaciones críticas |
| `INFONAVIT_EFIRMA_KEY` | (opcional) .key e.firma |
| `INFONAVIT_EFIRMA_PASS` | (opcional) contraseña .key |
| `PLUGINS_MX_PLAYWRIGHT_REAL` | `"1"` para activar opt-in |

## Tools afectados

Cuando modo = `real`:
- `infonavit_consultar_creditos_trabajadores` → portal Empresarial
- `infonavit_descargar_emis` → EMIS bimestral
- `infonavit_consultar_descuentos_mensuales` → detalle por trabajador
- `infonavit_consultar_avisos_pendientes` → bandeja patronal

Los 4 tools Sprint F (`infonavit_descuento_calcular`, `infonavit_creditos_sin_reporte`,
`infonavit_emis_historico`, `infonavit_conciliacion_nomina`) son **locales o
semi-locales** — no requieren credenciales para devolver valor.

## Estado del código

| Componente | Estado |
|---|---|
| Stub modo mock/real/blocked | ✅ (`playwright_stub.py`) |
| Bitácora hasheada NSS + RP | ✅ |
| Registry selectores | ❌ pendiente discovery |
| Login implementation | ⏳ requiere humano |
| 4 tools de lectura real | ⏳ requiere humano |
| Conciliación nómina cruzada con datos reales | ⏳ requiere humano |

## Particularidades del portal INFONAVIT

1. **MFA por SMS opcional**: si el cliente lo tiene activado, requiere
   intercepción de SMS (no implementado — recomendamos desactivar MFA por SMS
   en cuentas dedicadas a automatización).

2. **Bloqueo por 24h tras 3 intentos fallidos de contraseña**: el cliente debe
   evitar correr tests E2E sin sesión cacheada válida.

3. **Cookies de sesión vigentes 30 minutos**: el path real debe renovar sesión
   antes de cada consulta o cachear el cookie jar.

4. **Algunos avisos requieren e.firma**: avisos de baja con causa "rescisión
   justificada" requieren firma e.firma del representante legal.

## Roadmap de activación

1. **Discovery vivo**: ~3h con Playwright MCP. Resultado: `selectors_v1.py`.
2. **Login + sesión cacheada**: ~10h.
3. **4 tools de lectura**: ~5h cada uno (~20h).
4. **Tests E2E con credenciales reales**: ~6h.
5. **Documentación operativa**: ~3h.

**Total estimado**: ~45h (~1.5 semanas full-time). Cotización: $35,000 MXN
para Producción Anual, incluido en Empresarial.

## Cómo activar (cuando ya esté implementado)

```python
import os

os.environ["INFONAVIT_RFC_PATRONAL"] = "EMPR010101AAA"
os.environ["INFONAVIT_USUARIO"] = "responsable_patronal_user"
os.environ["INFONAVIT_PASSWORD"] = os.environ["INFONAVIT_PASS_FROM_VAULT"]
os.environ["PLUGINS_MX_PLAYWRIGHT_REAL"] = "1"

from mp_infonavit_patronal.client import InfonavitPatronalClient

c = InfonavitPatronalClient()
r = c.consultar_creditos_trabajadores("Y123456789")
# Si modo = "real": scraping vivo
# Si falla login: respuesta con simulated=False + error explícito
# Sin env vars: simulated=True con shape plausible
```

## Contacto

`elimoralsmendox@gmail.com` — asunto: **"Activar path real INFONAVIT"**.
