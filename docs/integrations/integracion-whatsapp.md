# Integración con WhatsApp Business Platform

**Propósito**: cómo conectar el monorepo a un provider de WhatsApp Business para envío real.

**Audiencia**: desarrolladores que activan WhatsApp en producción.

**Pre-lectura**: `_shared/whatsapp-business-mx/SKILL.md`, [glosario-tecnico.md](glosario-tecnico.md).

---

## Opciones de provider WhatsApp Business

| Provider | Tipo | Setup | Costo | Recomendado para |
|---|---|---|---|---|
| **Meta Cloud API** | Directo | Medio | Más barato (paga directo a Meta) | Devs senior, control total |
| **Gupshup** | BSP (Business Solution Provider) | Fácil | Markup ~10-30% sobre Meta | PyMEs, soporte en español |
| **Twilio** | BSP | Medio | Premium | Enterprise, soporte 24/7 |
| **360Dialog** | BSP | Fácil | Markup ~10-20% | Europa, América |
| **Sirena** | BSP | Fácil | Premium | LATAM, soporte local |

---

## Setup con Gupshup (recomendado para PyMEs MX)

### 1. Crear cuenta

1. https://www.gupshup.io → Sign up
2. Verificar email
3. Crear "App" en panel

### 2. Verificar número de WhatsApp Business

- Necesitas un número de teléfono que NO esté usado en WhatsApp personal
- Gupshup guía el proceso de verificación con Meta

### 3. Obtener API key

Panel → App settings → API Key → Generate

### 4. Configurar `.env`

```bash
GUPSHUP_API_KEY=tu_api_key
GUPSHUP_APP_NAME=tu_app_name
GUPSHUP_BUSINESS_NUMBER=521555...
```

### 5. Activar MCP en plugin

```json
{
  "mcpServers": {
    "whatsapp-business": {
      "command": "npx",
      "args": ["-y", "@gupshup/mcp-whatsapp"],
      "env": {
        "GUPSHUP_API_KEY": "${GUPSHUP_API_KEY}",
        "GUPSHUP_APP_NAME": "${GUPSHUP_APP_NAME}"
      },
      "disabled": false
    }
  }
}
```

> **Nota**: si `@gupshup/mcp-whatsapp` no existe en npm, construir MCP propio (ver sección final).

### 6. Subir templates a Meta Business Manager

Antes de enviar, Meta debe aprobar tus templates:

1. Tomar template de `_shared/whatsapp-business-mx/references/templates-aprobados.md`
2. Subirlo a Business Manager → Message Templates
3. Esperar aprobación (1-48h)
4. Una vez aprobado: usar el `name` del template para enviar

### 7. Primer envío

```
Usuario: "Manda recordatorio de cita a Juan Pérez al +52 55 1234 5678 para
        mañana viernes 15 a las 10:30 AM en Clínica Aurora."

Claude → invoca whatsapp-business-mx
        Identifica template: utility_confirmacion_cita_general_mx
        Llena variables: {{1}} Juan, {{2}} Clínica Aurora, {{3}} viernes 15
        Llama a Gupshup MCP
        Devuelve confirmación de envío con message_id
```

---

## Setup con Meta Cloud API (control total)

### 1. Aplicar a programa de desarrolladores

https://developers.facebook.com → Create app → Business

### 2. Configurar WhatsApp Business Account

- Vincular número telefónico
- Verificar tu negocio (Business Verification)
- Configurar webhooks para mensajes entrantes

### 3. Obtener Permanent Access Token

Tutorial oficial: https://developers.facebook.com/docs/whatsapp/business-management-api

### 4. Configurar `.env`

```bash
META_WA_ACCESS_TOKEN=tu_token_permanente
META_WA_PHONE_NUMBER_ID=tu_phone_id
META_WA_BUSINESS_ACCOUNT_ID=tu_business_id
```

### 5. Construir MCP server propio

```python
# mcp-servers/whatsapp-cloud.py
import os
import httpx
from fastmcp import FastMCP

mcp = FastMCP("whatsapp-cloud")

ACCESS_TOKEN = os.getenv("META_WA_ACCESS_TOKEN")
PHONE_ID = os.getenv("META_WA_PHONE_NUMBER_ID")
BASE_URL = f"https://graph.facebook.com/v18.0/{PHONE_ID}"

@mcp.tool()
async def send_template(
    to: str,
    template_name: str,
    language: str = "es_MX",
    variables: list = None,
) -> dict:
    """Envía un template aprobado de WhatsApp.
    
    Args:
        to: número destinatario en formato internacional (521...)
        template_name: nombre del template aprobado por Meta
        language: código idioma (es_MX por default)
        variables: lista de strings para llenar {{1}}, {{2}}, etc.
    """
    components = []
    if variables:
        components.append({
            "type": "body",
            "parameters": [{"type": "text", "text": v} for v in variables]
        })
    
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": components,
        }
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/messages",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json=body,
        )
        return resp.json()

@mcp.tool()
async def send_freeform_text(to: str, message: str) -> dict:
    """Envía mensaje de texto libre (solo dentro de ventana de 24h).
    
    Args:
        to: número destinatario
        message: texto del mensaje
    """
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/messages",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json=body,
        )
        return resp.json()

if __name__ == "__main__":
    mcp.run()
```

---

## Tipos de mensaje y reglas

### Mensajes salientes que TÚ inicias
- **Solo templates aprobados** por Meta
- Costo por conversación según categoría
- Requiere opt-in del destinatario

### Mensajes salientes en respuesta a entrante
- **Cualquier mensaje libre** dentro de 24h de la última interacción del cliente
- Costo $0 (incluido en la sesión)
- No requiere template

### Recibir mensajes
- Webhook configurado en Meta Business Manager
- Cada mensaje entrante reinicia la ventana 24h
- Procesar con tu sistema (typicamente un bot o CRM)

---

## Categorías de template Meta (actualizado a tu entrenamiento)

| Categoría | Cuándo usar | Costo MX (aprox) |
|---|---|---|
| **UTILITY** | Transaccional ligado a una acción del usuario | $0.03-$0.05 USD/conversación |
| **MARKETING** | Promociones, ofertas, newsletters | $0.06-$0.09 USD/conversación |
| **AUTHENTICATION** | OTP, códigos de verificación | $0.01-$0.02 USD/conversación |

**Conversación = 24h de mensajes ilimitados** desde el primer template enviado o respuesta del cliente.

---

## Quality Rating y por qué importa

Meta evalúa tu cuenta:
- **GREEN (alta)**: todo bien, tarifas normales
- **YELLOW (media)**: algunos reportes de spam, posible elevación de tarifa
- **RED (baja)**: muchos reportes, Meta puede limitar tu volumen diario

**Para mantener GREEN**:
- No mandar mismo template a TODA la base si no aplica
- Respetar opt-outs inmediatamente
- Footer con marca clara para identificación
- Templates útiles (UTILITY) > promocionales (MARKETING) en ratio

---

## Opt-in compliance

LFPDPPP + Meta requirements:

### Para mensajes UTILITY
- El opt-in es implícito si el usuario te dio su número para servicio (ej. orden de compra, cita)
- Pero documentar la fuente del consentimiento

### Para mensajes MARKETING
- **Opt-in explícito demostrable**
  - Checkbox claro en formulario
  - Confirmación de doble opt-in (recomendado)
  - Registro con timestamp, IP, fuente
- Respetar "STOP" / "BAJA" / "MENOS" automáticamente

### Almacenar consentimientos
```json
{
  "telefono": "+5215512345678",
  "fecha_optin": "2026-03-15T10:30:00-06:00",
  "fuente": "formulario_web_landing_aurora",
  "tipos_consentidos": ["utility", "marketing"],
  "ip_origen": "201.123.45.67"
}
```

Si llega queja al INAI: estos registros son tu defensa.

---

## Plantillas listas para usar

Ver `_shared/whatsapp-business-mx/references/templates-aprobados.md` para biblioteca de 15+ templates por categoría y vertical.

Estos templates **NO han sido sometidos al flujo real de aprobación Meta**. Pueden requerir ajustes según política vigente. Validar en sandbox de Meta Business Manager antes de producción.

---

## Costos típicos en producción

### Freelancer (50-200 mensajes/mes)
- ~$3-15 USD/mes en mensajes
- + $0-50 USD/mes plan BSP (Gupshup tiene tier gratuito)

### Colegio (500-2000 mensajes/mes)
- ~$30-150 USD/mes en mensajes
- + $50-200 USD/mes plan BSP

### Agencia con varios clientes (5000-20000 mensajes/mes)
- ~$300-1500 USD/mes
- + plan empresarial BSP

---

## Troubleshooting

### Template rechazado por Meta
- Revisar razón en Business Manager
- Comunes: categorización incorrecta, contenido prohibido, urgencia falsa, mayúsculas excesivas
- Ajustar según `_shared/whatsapp-business-mx/SKILL.md` y reenviar

### "Mensaje no se entrega"
- Verificar formato del teléfono (debe incluir código país)
- Confirmar número activo en WhatsApp
- Check Quality Rating de tu cuenta

### "Quality Rating bajó"
- Identificar templates con alto reporte de spam
- Pausar campañas MARKETING agresivas
- Revisar opt-outs no respetados

### "Conversation cap reached"
- Meta limita volumen diario según tu Quality + verificación
- Esperar o solicitar tier upgrade

---

## Ver también

- `_shared/whatsapp-business-mx/SKILL.md` — capacidad central
- `_shared/whatsapp-business-mx/references/templates-aprobados.md` — biblioteca
- [seguridad.md](seguridad.md) — manejo de tokens y consentimientos
