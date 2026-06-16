# mp_imss_patronal — activación del path Playwright real

> Spec opt-in para clientes B2B con NPIE/e.firma propia. Sin credenciales reales
> el cliente sigue funcionando en modo mock — todas las respuestas marcadas
> `simulated: true` con shape plausible.

## Resumen ejecutivo

Este MCP cubre **IDSE** (IMSS Desde Su Empresa). El portal requiere autenticación
con tarjeta NPIE física + PIN o e.firma vigente. Por seguridad y costo de
mantenimiento, el path Playwright real está **bloqueado por default**.

Para activarlo, el cliente debe:

1. Tener una NPIE vigente o e.firma del registro patronal.
2. Generar la sesión IDSE inicial fuera-de-banda (con su tarjeta física).
3. Setear las variables de entorno descritas abajo.
4. Setear `PLUGINS_MX_PLAYWRIGHT_REAL=1`.

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `IMSS_RFC_PATRONAL` | RFC del registro patronal | `EMPR010101AAA` |
| `IMSS_NPIE_PATH` | Ruta al archivo NPIE (.cer/.key/.csv según el formato del IMSS) | `/secrets/npie.cer` |
| `IMSS_NPIE_PIN` | PIN de la NPIE (8 dígitos típicamente) | `12345678` |
| `IMSS_EFIRMA_CERT` | Alternativa a NPIE: ruta del .cer e.firma | `/secrets/efirma.cer` |
| `IMSS_EFIRMA_KEY` | Ruta del .key e.firma | `/secrets/efirma.key` |
| `IMSS_EFIRMA_PASS` | Contraseña del .key e.firma | `passw0rd` |
| `PLUGINS_MX_PLAYWRIGHT_REAL` | Flag de opt-in (debe ser `"1"`) | `1` |

## Tools afectados por path real

Cuando el modo es `real`, los siguientes tools intentan scraping en vivo:

- `imss_consultar_avisos_pendientes` → portal IDSE
- `imss_enviar_movimiento_afiliatorio` → 6 tipos de movimiento (alta, baja, modif, reingreso)
- `imss_descargar_cedula_autodeterminacion` → cédula bimestral
- `imss_consultar_emcr` → cédula mensual reposicionada
- `imss_consultar_sbc` → salario diario integrado por NSS
- `imss_consultar_padron_trabajadores` → padrón del registro patronal

Los 5 tools Sprint F (`imss_sbc_calcular`, `imss_ema_vs_eba_diferencias`,
`imss_calendario_obligaciones`, `imss_simulador_costo_patronal`,
`imss_riesgo_trabajo_prima_cambio`) son **locales** y NO requieren credenciales —
son calculadoras + lógica determinística.

## Estado del código

| Componente | Estado | Notas |
|---|---|---|
| Stub `playwright_stub.py` compartido | ✅ | Decide mock/blocked/real desde env vars |
| Detector vencimiento e.firma | ⚠ pendiente | Reusar `efirma_loader.py` de `mp_sat_portal` |
| Login NPIE | ⏳ requiere humano + portal vigente | IDSE cambió UI en 2025 |
| Login e.firma (alternativa) | ⏳ requiere humano | Patrón similar a SAT |
| Registry selectores IDSE | ❌ no creado | Pendiente discovery Playwright |
| Captura HTML failure artifacts | ⏳ implementar como en SAT | `dump_failure_artifacts()` |
| Bitácora hasheada (NSS, RP) | ✅ | Ya en client.py L41-47 |

## Riesgos conocidos

1. **IDSE bloquea sesiones concurrentes**: si el operador humano está logueado
   con la misma NPIE en otra computadora, la sesión Playwright fallará.
   Mitigación: el cliente debe dedicar la NPIE a la automatización durante
   ventanas operativas.

2. **Tarjeta NPIE física vence**: vigencia 4 años. El path real no puede
   renovarla — debe el cliente.

3. **IMSS aplica throttling**: más de ~30 consultas/minuto generan CAPTCHA.
   El cliente debe configurar `PLUGINS_MX_IMSS_THROTTLE_MS=2000` (default).

4. **Movimientos afiliatorios son destructivos**: `imss_enviar_movimiento_afiliatorio`
   modifica el padrón del trabajador. **NO se ejecuta path real** sin
   `PLUGINS_MX_IMSS_PERMITIR_ESCRITURA=1` (default off por seguridad).

## Roadmap de activación (cuando un cliente lo solicite)

1. **Discovery vivo**: agendar 2h con Playwright MCP para mapear los selectores
   actuales del portal IDSE. Resultado: `selectors_v1.py`.
2. **Login implementation**: ~16h (NPIE o e.firma según preferencia cliente).
3. **6 tools de lectura**: ~6h cada uno (~36h total).
4. **1 tool de escritura** (`imss_enviar_movimiento_afiliatorio`): ~12h
   con doble confirmación + sandbox.
5. **Tests E2E** con sesión real del cliente: ~8h.
6. **Documentación operativa**: runbook + recovery from CAPTCHA + monitoring.

**Total estimado**: ~80h (= ~2 semanas full-time). Cotización: $65,000 MXN
para Producción Anual, incluido sin cargo en Empresarial.

## Patrón de uso (ejemplo)

```python
import os

# Solo el cliente setea esto en su servidor — nunca en mi infraestructura
os.environ["IMSS_RFC_PATRONAL"] = "EMPR010101AAA"
os.environ["IMSS_EFIRMA_CERT"] = "/secrets/efirma.cer"
os.environ["IMSS_EFIRMA_KEY"] = "/secrets/efirma.key"
os.environ["IMSS_EFIRMA_PASS"] = os.environ["IMSS_EFIRMA_PASS_FROM_VAULT"]
os.environ["PLUGINS_MX_PLAYWRIGHT_REAL"] = "1"

from mp_imss_patronal.client import ImssPatronalClient

c = ImssPatronalClient()
# Modo será "real" — intenta scraping en vivo
r = c.consultar_padron_trabajadores("Y123456789")
```

Sin las variables de entorno, el mismo código retorna mock con flag explícito:

```python
{
  "simulated": True,
  "simulation_note": "IMSS IDSE requiere NPIE o e.firma — datos simulados.",
  ...
}
```

## Contacto para activación

Para activar el path real en tu Producción Anual o Empresarial, escríbeme a
`elimoralsmendox@gmail.com` con asunto **"Activar path real IMSS"** y la
información del cliente:
- Razón social + RFC patronal
- Vertical donde se usará
- Volumen estimado de consultas/mes
- Ventana operativa preferida (horarios)
