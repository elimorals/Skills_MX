# Guía de instalación

**Propósito**: instalar los plugins de Skills_MX en Claude Code y usar sus MCPs.

**Audiencia**: usuarios finales. Si vas a modificar el repo, ve a [guia-desarrollo.md](guia-desarrollo.md).

**Pre-lectura**: [README raíz](../../README.md) (lista de plugins y estado de los MCPs).

---

## Requisitos

- **Claude Code** (CLI, desktop o extensión de IDE).
- **[`uv`](https://docs.astral.sh/uv/)**: es el único requisito adicional. Los MCPs se descargan y ejecutan con él la primera vez que se usan. No hace falta clonar el repo ni instalar Python a mano.
- (Opcional) Credenciales de los servicios que quieras usar en real: SAT (e.firma), Banxico (token SIE), Facturama, Mercado Pago, Conekta, etc. Sin ellas, los MCPs responden datos de ejemplo marcados `simulated: true`.

---

## 1. Instalar plugins desde el marketplace

Dentro de Claude Code:

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX      # base de todos los verticales
/plugin install freelancers-mx --marketplace elimorals/Skills_MX   # o cualquier vertical
```

`core-mexico` (CFDI, IVA y retenciones, RFC, MXN, LFPDPPP, WhatsApp) es la dependencia de todos los verticales. La lista completa de los 40 plugins está en el [README raíz](../../README.md#plugins-verticales) y en `.claude-plugin/marketplace.json`.

Para comprobar que cargó, escribe `/help` y busca los comandos del plugin (p. ej. `/freelancers:cotizar`), o pregunta a Claude qué skills tiene cargadas.

### Actualizar y desinstalar

Usa `/plugin` para actualizar el marketplace o desinstalar un plugin. Los MCPs apuntan a la rama `main` del repo. `uv` guarda el paquete en su caché y lo vuelve a resolver cuando cambia.

---

## 2. Usar un MCP suelto

Cada MCP trae un `mcp-servers/mp_*/example.mcp.json` listo para copiar a tu `.mcp.json`. No depende de dónde esté el repo:

```json
{
  "mcpServers": {
    "banxico": {
      "command": "uv",
      "args": ["run", "--no-project", "--quiet", "--with",
               "plugins-mx-mcp-servers @ git+https://github.com/elimorals/Skills_MX@main#subdirectory=mcp-servers",
               "python", "-m", "mp_banxico.server"],
      "env": {
        "BANXICO_TOKEN": "${BANXICO_TOKEN:-}",
        "PLUGINS_MX_MOCK": "${PLUGINS_MX_MOCK:-}"
      }
    }
  }
}
```

Los MCPs con dependencias opcionales llevan extras en el paquete, por ejemplo `plugins-mx-mcp-servers[sat-ws,sat-portal] @ git+…` para el SAT. Copia el `example.mcp.json` de cada MCP en vez de armarlo a mano.

---

## 3. Credenciales

Van en variables de entorno, nunca en el repo. `.env.example` (en la raíz del repo) lista todas. Cada `example.mcp.json` dice cuáles usa su MCP.

| Variable | Uso |
|---|---|
| `SAT_RFC`, `SAT_EFIRMA_CERT`, `SAT_EFIRMA_KEY`, `SAT_EFIRMA_PASSWORD` | e.firma para el SAT (rutas a `.cer` y `.key` fuera del repo) |
| `BANXICO_TOKEN` | SIE de Banxico (token gratuito) |
| `FACTURAMA_USER`, `FACTURAMA_PASSWORD`, `FACTURAMA_ENV` | Timbrado con Facturama (`sandbox` o `production`) |
| `MERCADOPAGO_ACCESS_TOKEN`, `CONEKTA_API_KEY`… | Una por proveedor |
| `PLUGINS_MX_MOCK=1` | Fuerza datos de ejemplo en todos los MCPs |
| `PLUGINS_MX_CAPTCHA_SOLVER=2captcha`, `TWOCAPTCHA_API_KEY` | Solver de CAPTCHA opt-in |

**Cómo se comportan los MCPs:**

- **Sin credenciales**: datos de ejemplo marcados `simulated: true`.
- **Con credenciales**: consulta real. Si el proveedor falla, el error se propaga (`AuthError`, `UpstreamError`…). Nunca hay fallback silencioso a datos de ejemplo.
- **Portales con CAPTCHA o login**: el tool devuelve una entrega a humano (URL, pasos y campos prellenados). Si activas el solver opt-in, intenta resolver el CAPTCHA primero.
- **Sin API pública**: error explícito con la alternativa manual.

El estado de cada MCP está en [`mcp-servers/CATALOGO.md`](../../mcp-servers/CATALOGO.md).

---

## 4. Verificación rápida

En una sesión con `freelancers-mx`:

```
Valida el RFC IBM970131DRA
```
Debe invocar `rfc-validacion`.

```
Calcula el IVA y retenciones para servicios profesionales de 15,000 MXN de PFAE a una persona moral.
```
Debe invocar `iva-retenciones-mx`.

```
¿Cuál es el tipo de cambio DOF de hoy?
```
Usa `mp_banxico`. Sin `BANXICO_TOKEN`, la respuesta viene marcada `simulated: true`.

---

## 5. Skills sueltas en Claude.ai

Las skills son carpetas con `SKILL.md` y `references/`. Para subir una a Claude.ai, comprime su carpeta (p. ej. `_shared/cfdi-emision/`) en `.zip` y súbela desde la configuración de Skills. Las skills que dependen de un MCP pierden esa parte fuera de Claude Code.

---

## Solución de problemas

Ver [troubleshooting.md](../operational/troubleshooting.md).

| Problema | Qué revisar |
|---|---|
| El MCP no arranca | Que `uv` esté en el `PATH` (`uv --version`) y que haya red la primera vez para descargar el paquete |
| Todas las respuestas traen `simulated: true` | Faltan las variables de entorno del MCP, o está puesto `PLUGINS_MX_MOCK=1` |
| Error `AuthError` / `UpstreamError` | Credencial inválida o el proveedor falló. Es intencional: no se oculta con datos de ejemplo |
| La skill no se activa | El `description:` puede no cubrir tu fraseo. Ver [guia-desarrollo.md](guia-desarrollo.md) |

---

## Privacidad y seguridad

Ver [seguridad.md](../architecture/seguridad.md). En resumen:

- Las skills procesan en tu sesión. Los MCPs con credenciales sí envían datos al proveedor correspondiente (SAT, Banxico, PAC, pasarela).
- La bitácora local guarda solo hashes de RFC, CURP y correo.
- Cumplir la LFPDPPP con los datos de tus clientes te corresponde a ti.

---

## Ver también

- [guia-desarrollo.md](guia-desarrollo.md): para extender o modificar
- [integracion-pac.md](../integrations/integracion-pac.md): timbrado de CFDI
- [integracion-whatsapp.md](../integrations/integracion-whatsapp.md): WhatsApp Business
