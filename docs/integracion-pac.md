# Integración con PAC (Proveedor Autorizado de Certificación)

**Propósito**: cómo conectar el monorepo a un PAC real para timbrado de CFDI.

**Audiencia**: desarrolladores que pasan de mock a producción.

**Pre-lectura**: [glosario-fiscal-mx.md](glosario-fiscal-mx.md), `_shared/cfdi-emision/SKILL.md`.

---

## ¿Qué es un PAC?

Empresa autorizada por el SAT para timbrar CFDIs. El PAC valida el XML que generas, le agrega el sello del SAT, y te devuelve el CFDI con UUID oficial.

Sin PAC NO PUEDES emitir CFDIs en México. Es paso obligatorio.

---

## PACs más usados en México (para PyMEs y devs)

| PAC | Sandbox gratis | API/REST | SDK | Notas |
|---|---|---|---|---|
| **Facturama** | Sí | Sí, bueno | Múltiples lenguajes | Más popular para devs por documentación |
| **SW Sapien** | Sí | Sí | Sí | Más enterprise |
| **Solución Factible** | Sí, limitado | Sí | Sí | Maduro, robusto |
| **Buzón E** | Sí | Sí | Limitado | Económico, soporte regular |
| **The Factory HKA** | Sí | Sí | Sí | Operación en varios países |

Este monorepo asume **Facturama** por default en `.mcp.json` placeholders, pero cualquier otro funciona con ajustes.

---

## Setup con Facturama (paso a paso)

### 1. Crear cuenta sandbox

1. Ir a https://facturama.mx
2. Sign up — cuenta sandbox es gratuita
3. Recibes credenciales en email

### 2. Generar API Key

1. Login en panel Facturama
2. Settings → API Keys → Generate
3. Guardar el API Key generado

### 3. Configurar `.env` local

```bash
cd ~/plugins-mx
cp .env.example .env
nano .env
```

Agrega:
```
FACTURAMA_API_KEY=tu_api_key_aqui
FACTURAMA_ENV=sandbox
```

### 4. Activar MCP server

Edita el `.mcp.json` del plugin que vas a usar (ej. `freelancers-mx/.mcp.json`):

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
      "disabled": false   // ← cambiar de true a false
    }
  }
}
```

> **Nota**: el package `@facturama/mcp-server` puede no existir como tal. Verificar en npm registry. Si no existe, hay que construir un MCP server propio que envuelva la API REST de Facturama.

### 5. Reiniciar Claude Code

```bash
# Salir y volver a entrar a la sesión
exit
claude --plugin-dir ~/plugins-mx/freelancers-mx
```

### 6. Verificar conexión

```
Usuario: "Verifica que el MCP server de Facturama está activo."
Claude → debería listar las tools de Facturama si conectó bien.
```

### 7. Primer timbrado de prueba

```
Usuario: "Timbra un CFDI de prueba: emisor mi RFC, receptor IBM970131DRA,
        servicio de consultoría 1,000 MXN."

Claude → invoca cfdi-emision
        Construye payload
        Llama a Facturama via MCP
        Devuelve UUID, sello, XML
```

---

## Construir MCP server propio para un PAC

Si no hay MCP server oficial del PAC que usas, hay que construirlo. Es ~200-400 líneas de Python con FastMCP.

### Estructura mínima

```python
# mcp-servers/mi-pac-server.py
import os
from fastmcp import FastMCP
import httpx

mcp = FastMCP("mi-pac")

API_KEY = os.getenv("MI_PAC_API_KEY")
BASE_URL = os.getenv("MI_PAC_BASE_URL", "https://api.mi-pac.com/v1")

@mcp.tool()
async def timbrar_cfdi(payload: dict) -> dict:
    """Timbra un CFDI 4.0 contra el PAC.
    
    Args:
        payload: dict con estructura del CFDI 4.0 (emisor, receptor,
                conceptos, impuestos, etc.)
    
    Returns:
        dict con uuid, fecha_timbrado, sello_sat, cadena_original, xml_timbrado.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/cfdi/40",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=payload,
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def cancelar_cfdi(uuid: str, motivo: str, folio_sustituto: str = None) -> dict:
    """Cancela un CFDI emitido previamente.
    
    Args:
        uuid: folio fiscal del CFDI a cancelar
        motivo: clave 01-04 del catálogo c_MotivoCancelacion
        folio_sustituto: UUID del CFDI sustituto (solo si motivo = 01)
    """
    body = {"uuid": uuid, "motivo": motivo}
    if folio_sustituto:
        body["folio_sustituto"] = folio_sustituto
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/cfdi/cancelar",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=body,
        )
        return response.json()

@mcp.tool()
async def consultar_estatus_cfdi(uuid: str) -> dict:
    """Consulta el estatus actual de un CFDI: Vigente, Cancelado, En proceso."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/cfdi/{uuid}/estatus",
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        return response.json()

if __name__ == "__main__":
    mcp.run()
```

### Registrar en `.mcp.json`

```json
{
  "mcpServers": {
    "mi-pac": {
      "command": "python",
      "args": ["./mcp-servers/mi-pac-server.py"],
      "env": {
        "MI_PAC_API_KEY": "${MI_PAC_API_KEY}",
        "MI_PAC_BASE_URL": "${MI_PAC_BASE_URL}"
      },
      "disabled": false
    }
  }
}
```

---

## Manejo de credenciales

### Lo que SÍ hacer
- Variables de entorno en `.env` (local, en `.gitignore`)
- Distintos API keys para sandbox vs producción
- Rotación periódica de API keys (cada 90-180 días)
- Logs sin exponer credenciales

### Lo que NUNCA hacer
- Commitear `.env` (revisar `.gitignore`)
- Compartir API key en mensajes/Slack/email
- Usar credenciales de producción en pruebas
- Hardcodear credenciales en código

---

## Diferencias sandbox vs producción

| Aspecto | Sandbox | Producción |
|---|---|---|
| CFDI timbrado | Sí, pero sin valor fiscal real | Sí, válido ante SAT |
| Costo por timbre | Gratuito (con límites) | $0.50 - $3 MXN según PAC y volumen |
| Cancelación | Funciona | Funciona (con aceptación receptor) |
| UUIDs | Reales pero marcados como prueba | Reales |
| Validación SAT | No | Sí (sello real del SAT) |
| Errores | Mismos códigos que producción | Mismos códigos |

**Recomendación**: hacer 100+ timbrados de prueba en sandbox antes de cambiar a producción.

---

## Costos típicos en producción

| PAC | Setup | Por timbre (volumen alto) | Soporte |
|---|---|---|---|
| Facturama | Gratis | $0.50-$1.50 MXN | Email, chat |
| SW Sapien | $1k-3k MXN | $1-2 MXN | Email, teléfono |
| Solución Factible | $0-5k MXN | $0.80-$2 MXN | Email, teléfono |

Para un freelancer que emite 30-100 CFDIs/mes: costo despreciable (~$50-300 MXN/mes).
Para un colegio con 500 padres: costo significativo (~$500-1500 MXN/mes), buscar plan con volumen.

---

## Validación post-timbrado

Después de cada timbrado exitoso, validar con el SAT directamente (gratuito):

```
URL: https://verificacfdi.facturaelectronica.sat.gob.mx/
Inputs: UUID + RFC emisor + RFC receptor + total
Output: estado del CFDI (Vigente, Cancelado, etc.)
```

Para CFDIs masivos, usar API masiva del SAT (requiere FIEL).

---

## Troubleshooting timbrado

### Error: "RFC del receptor no encontrado en padrón"
- Validar el RFC con `rfc-validacion`
- Confirmar que el receptor está en padrón SAT (Constancia de Situación Fiscal)
- Si es PF/PM nuevo: pedir constancia al receptor

### Error: "Uso CFDI incompatible con régimen del receptor"
- El SAT mantiene matriz de compatibilidad
- Sugerir uso alternativo válido para ese régimen (G03 es el más universal)

### Error: "CP del receptor no existe"
- Validar el CP de 5 dígitos
- El SAT publica catálogo c_CodigoPostal con todos los válidos

### Error: "Método pago inconsistente con forma pago"
- PUE no puede llevar FormaPago 99
- PPD debe llevar FormaPago 99
- Validar con `cfdi-emision` antes de llamar al PAC

### Error: "Fecha del CFDI fuera de rango"
- Máximo 72h hacia el pasado, 0 hacia el futuro
- Validar timezone del emisor

### Error: "Sello del emisor inválido"
- Verificar CSD (Certificado de Sello Digital) vigente
- El CSD se vence cada 4 años, hay que renovar

---

## Caso producción: validar con cliente real

Antes de usar PAC real con cliente:

1. **Validar al menos 5 CFDIs de prueba en sandbox**
2. **Hacer 1 CFDI real en producción con monto pequeño** ($100-500 MXN) a tu propio RFC
3. **Verificar que se descarga XML correctamente** del portal del PAC
4. **Validar contra portal SAT** con UUID
5. **Recién entonces facturar a cliente real**

---

## Ver también

- `_shared/cfdi-emision/SKILL.md` — el skill que orquesta el timbrado
- `_shared/cfdi-emision/references/catalogos-sat.md` — catálogos a validar
- `_shared/cfdi-emision/references/casos-edge-cfdi.md` — patrones complejos
- [seguridad.md](seguridad.md) — manejo de credenciales
- [troubleshooting.md](troubleshooting.md) — más problemas comunes
