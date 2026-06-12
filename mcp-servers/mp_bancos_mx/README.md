# mp_bancos_mx — MCP para portales bancarios mexicanos

⚠ **Path Playwright real NO implementado todavía.** Sin credenciales corre 100% mock con datos demo plausibles. Construir cada path real requiere 60-100h de desarrollo + mantenimiento mensual ya que los portales bancarios cambian con frecuencia.

## Bancos soportados (placeholder)

| Banco | Share PyME | Estado |
|---|---|---|
| BBVA México | ~30% | Mock |
| Banamex (Citibanamex) | ~20% | Mock |
| Santander México | ~15% | Mock |
| Banorte | ~12% | Mock |
| HSBC México | ~5% | Mock |
| Inbursa | ~5% | Mock |
| Scotiabank | ~4% | Mock |
| Banregio | ~3% (norte) | Mock |
| Banco Azteca | ~3% (B2C) | Mock |

## Tools (4)

| Tool | Propósito |
|---|---|
| `bancos_listar_soportados` | Discovery: bancos, métodos auth, estado path real |
| `bancos_descargar_estado_cuenta` | Estado de cuenta del periodo |
| `bancos_listar_movimientos` | Movimientos últimos N días |
| `bancos_verificar_pago_por_referencia` | Buscar pago entrante por referencia + monto |

## Casos de uso (cuando path real esté implementado)

1. **Conciliación bancaria mensual**: cruzar movimientos vs CFDIs emitidos/recibidos
2. **Verificación de pago**: cliente reporta SPEI → buscar por referencia → marcar CFDI como pagado
3. **Cierre fiscal**: junto con `mp_sat_portal` para audit completo del mes
4. **Detección de depósitos efectivo > $15k**: alerta automática para Art. 32-D

## Para activar path real (cuando exista)

```bash
# 1. Instalar Playwright
pip install playwright
playwright install chromium

# 2. Configurar credenciales por banco
export BBVA_USUARIO=tu_usuario
export BBVA_PASSWORD=tu_password

# 3. Opt-in explícito
export PLUGINS_MX_PLAYWRIGHT_REAL=1
```

## Limitaciones

- Cada banco tiene auth distinto (token físico, app, SMS)
- Portales cambian sin previo aviso
- Reto OCR/captcha en algunos endpoints
- Sesiones expiran rápido (5-15 min de inactividad)
- Lockout tras 3 intentos fallidos

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_bancos_mx/tests/ -q
```
