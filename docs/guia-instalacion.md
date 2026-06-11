# Guía de instalación

**Propósito**: Cómo instalar y usar los plugins/skills de plugins-mx.

**Audiencia**: usuarios finales (no desarrolladores).

**Pre-lectura**: [INDEX.md](INDEX.md) para entender qué hay disponible.

---

## Requisitos

- **Claude Code instalado** (CLI, desktop, o IDE extension). Si no lo tienes: https://claude.com/code.
- **Cuenta Anthropic activa** con plan que incluya Claude Code.
- **Git** instalado.
- (Opcional) **Cuenta en plataformas externas**: Facturama (CFDI), Gupshup/Twilio (WA Business), Stripe/Mercado Pago (cobros). Solo necesarias si vas a activar integraciones reales.

---

## Opción 1: Instalación como plugins de Claude Code (recomendado)

### 1.1 Clonar el monorepo

```bash
git clone <url-del-repo-plugins-mx> ~/plugins-mx
cd ~/plugins-mx
```

### 1.2 Verificar estructura

```bash
ls -la
# Debes ver: README.md, marketplace.json, core-mexico/, freelancers-mx/, agencia-marketing-mx/, colegios-mx/, talleres-mx/, _shared/, docs/, scripts/, evals/, tests/
```

### 1.3 Cargar un plugin específico

Arranca Claude Code apuntando al directorio del plugin que quieras usar:

```bash
# Solo core-mexico (base mexicana)
claude --plugin-dir ~/plugins-mx/core-mexico

# Vertical específico
claude --plugin-dir ~/plugins-mx/freelancers-mx
claude --plugin-dir ~/plugins-mx/agencia-marketing-mx
claude --plugin-dir ~/plugins-mx/colegios-mx
claude --plugin-dir ~/plugins-mx/talleres-mx
```

Cada plugin incluye los skills de `_shared/` ya sincronizados, así que NO necesitas instalar `core-mexico` aparte cuando cargas un vertical.

### 1.4 Verificar que los skills se cargaron

Dentro de la sesión, escribe:
```
/help
```

Y deberías ver los commands del plugin (ej. `/freelancers:cotizar`).

Puedes también pedir a Claude que liste:
```
¿Qué skills tienes cargados para operación mexicana?
```

### 1.5 Múltiples plugins simultáneos

Para tener varios verticales activos al mismo tiempo, usa `--plugin-dir` múltiple:

```bash
claude --plugin-dir ~/plugins-mx/freelancers-mx --plugin-dir ~/plugins-mx/colegios-mx
```

---

## Opción 2: Instalación como skills standalone

Útil si no usas Claude Code o quieres skills individuales en Claude.ai.

### 2.1 Vía skillkit (CLI)

```bash
npm install -g skillkit

# Instalar un skill compartido
skillkit install file://~/plugins-mx/_shared/cfdi-emision
skillkit install file://~/plugins-mx/_shared/rfc-validacion

# Listar skills instalados
skillkit list
```

### 2.2 Subida manual a Claude.ai

1. Comprime el directorio del skill: `tar -czf cfdi-emision.skill.tar.gz _shared/cfdi-emision/`
2. En Claude.ai → Settings → Skills → Upload Skill.
3. Selecciona el archivo `.tar.gz`.

---

## Configuración de integraciones (opcional)

Por default todos los plugins funcionan con **mocks** — no necesitas credenciales. Si quieres conectar servicios reales:

### Crear archivo `.env`

```bash
cd ~/plugins-mx
cp .env.example .env
nano .env
```

### Variables disponibles

```bash
# PAC para CFDI
FACTURAMA_API_KEY=tu_api_key_aqui
FACTURAMA_ENV=sandbox    # o "production"

# WhatsApp Business
GUPSHUP_API_KEY=tu_api_key
GUPSHUP_APP_NAME=tu_app

# Pagos
STRIPE_API_KEY=sk_test_...
MERCADOPAGO_ACCESS_TOKEN=APP_USR-...

# Notion (opcional, para CRM)
NOTION_TOKEN=secret_...
```

### Activar MCP servers

Edita `<plugin>/.mcp.json` y cambia `"disabled": true` a `"disabled": false` en los servicios que quieres activar.

Ejemplo para activar Facturama en freelancers-mx:
```json
{
  "mcpServers": {
    "facturama": {
      "command": "npx",
      "args": ["-y", "@facturama/mcp-server"],
      "env": {
        "FACTURAMA_API_KEY": "${FACTURAMA_API_KEY}",
        "FACTURAMA_ENV": "${FACTURAMA_ENV}"
      },
      "disabled": false
    }
  }
}
```

Recarga Claude Code con `/reload-plugins`.

---

## Verificación post-instalación

### Test rápido (sin integraciones reales)

En la sesión:

```
Tengo un cliente nuevo: Bimbo SA, RFC IBM970131DRA, régimen 601. Hazme su ficha de onboarding.
```

Si el plugin `freelancers-mx` está bien cargado, Claude debería invocar `cliente-onboarding` y guiarte por el flujo.

```
Valida el RFC IBM970131DRA
```

Debería invocar `rfc-validacion` y devolver estructura.

```
Calcula el IVA y retenciones para servicios profesionales de 15,000 MXN de PFAE a una persona moral.
```

Debería invocar `iva-retenciones-mx`.

### Test de regresión con fixtures

```bash
# (Cuando exista el runner)
~/plugins-mx/scripts/run-fixtures.sh

# Por ahora ejecución manual:
cat ~/plugins-mx/tests/fixtures/iva-retenciones-mx/case-01-pfae-a-pm.json
# Y verifica que el skill produce el output esperado.
```

---

## Updates

### Pull de actualizaciones del monorepo

```bash
cd ~/plugins-mx
git pull
```

### Re-sync de `_shared/` a verticales (después de actualizar)

```bash
./scripts/sync-shared.sh
```

### Validar lint después de cambios

```bash
./scripts/lint-skills.sh
```

---

## Desinstalación

### Plugins de Claude Code

Simplemente borra el directorio:
```bash
rm -rf ~/plugins-mx
```

### Skills standalone

```bash
skillkit uninstall cfdi-emision
skillkit uninstall rfc-validacion
# etc.
```

---

## Solución de problemas comunes

Ver [troubleshooting.md](troubleshooting.md) para más detalle.

| Problema | Solución |
|---|---|
| "Plugin no carga" | Verifica `.claude-plugin/plugin.json` existe; corre `./scripts/lint-skills.sh` |
| "Skill no triggea" | El `description:` puede no captar tu fraseo; ver [guia-desarrollo.md](guia-desarrollo.md) para calibrar |
| "MCP server falla" | Revisa que las variables de entorno estén en `.env` y que esté `disabled: false` |
| "Sync.sh no copia algo" | Verifica que el `plugin.json` del vertical liste el skill en `"skills":` |

---

## Privacidad y seguridad

Ver [seguridad.md](seguridad.md) para detalles. Resumen:

- Todos los skills tratan datos de manera local — no hay envío automático a servicios externos.
- Si activas MCP servers reales (Facturama, etc.), esos servicios SÍ reciben datos. Revisa los términos.
- Los plugins NO retienen datos entre sesiones. Lo que se guarda está en archivos locales tuyos.
- Cumplimiento LFPDPPP es responsabilidad del usuario final (tú o tu cliente).

---

## Ver también

- [guia-desarrollo.md](guia-desarrollo.md) — para extender o modificar
- [troubleshooting.md](troubleshooting.md) — problemas comunes
- [integracion-pac.md](integracion-pac.md) — detalle de PACs
- [integracion-whatsapp.md](integracion-whatsapp.md) — detalle de WA Business
