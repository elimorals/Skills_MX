---
spec: "bancos-mx-playwright-real"
estado: "DRAFT"
creado: "2026-06-11"
autor: "Elías Rashid Morales Mendoza"
ultima_actualizacion: "2026-06-11"
esfuerzo_estimado_horas: [240, 400]
prioridad: "tier-1"
---

# Spec 03 — `mp_bancos_mx` Playwright real (4 bancos prioritarios)

## 1. Propósito

`mp_bancos_mx` actualmente expone 4 tools mock para 9 bancos MX. Este spec define el **path Playwright real** para los **4 bancos prioritarios** (cubren ~77% del share PyME): BBVA, Banamex, Santander, Banorte.

Desbloquea:
- **Conciliación bancaria real** mensual (workflow #?)
- Verificación de pagos reales SPEI por referencia
- Estado de cuenta exportado para `mp_aspel_contpaqi` / cruce con CFDIs
- Detección automática de pagos recibidos sin webhook

Sin esto la conciliación es 100% manual (subir extracto CSV → parsear).

## 2. Contexto y por qué es novedoso

- **Lo que existe**: `mp_bancos_mx` stub con mock data plausible, shared `playwright_stub.py`.
- **Por qué es novedoso**: cada banco tiene auth **distinta** (token físico Banamex, app autenticadora BBVA, biométrico Santander, SMS Banorte). Es 4 implementaciones diferentes, no 1.
- **Reto técnico**: bancos cambian portal frecuentemente, **bloquean IPs**, requieren 2FA que solo el usuario puede completar.
- **Referencia plan original**: sección 6.2, esfuerzo 60-100h por banco.

## 3. Alcance

**Dentro:**
- 4 bancos: BBVA, Banamex (Citibanamex), Santander, Banorte
- Tools: `bancos_descargar_estado_cuenta`, `bancos_listar_movimientos`, `bancos_verificar_pago_por_referencia`
- Modo **asistido** (usuario completa 2FA en navegador headed, repo continúa)
- Sesión cacheable con timeout corto (15-30min según banco)

**Fuera (decisión deliberada):**
- 5 bancos secundarios (HSBC, Banregio, Inbursa, Azteca, Scotiabank) — Fase 2
- Login 100% automatizado con token físico (imposible)
- Transferencias / pagos automatizados (escritura — riesgo enorme)
- Persistencia de credenciales entre sesiones (riesgo seguridad)

## 4. Inputs / outputs / schemas

### Auth setup (por banco)

```bash
# BBVA
BBVA_USUARIO=tu_usuario
BBVA_PASSWORD=tu_password
# 2FA es manual via app BBVA (popup al ejecutar)

# Banamex
BANAMEX_USUARIO=tu_usuario
BANAMEX_PASSWORD=tu_password
BANAMEX_TOKEN_TYPE=physico | challenge
# 2FA token físico o challenge

# Santander
SANTANDER_USUARIO=tu_usuario
SANTANDER_PASSWORD=tu_password
# 2FA biometría/app

# Banorte
BANORTE_USUARIO=tu_usuario
BANORTE_PASSWORD=tu_password
BANORTE_SOFT_TOKEN_SEED=...  # opcional: TOTP seed si lo configuras
# 2FA SMS o soft token

# Opt-in
PLUGINS_MX_PLAYWRIGHT_REAL=1
```

### Schema movimiento (común a 4 bancos)

```python
class Movimiento(BaseModel):
    fecha: date
    tipo: TipoMovimiento  # depósito, retiro, transferencia, comisión...
    concepto: str
    referencia_numerica: str | None
    clave_rastreo_spei: str | None  # si SPEI
    monto: Decimal
    saldo_resultante: Decimal | None
    rfc_ordenante: str | None        # si fue transferencia recibida
    banco_ordenante: str | None
```

## 5. Tools afectados

| Tool | Estado mock | Path real |
|---|---|---|
| `bancos_descargar_estado_cuenta(banco, cuenta, ejercicio, mes, formato)` | ✅ | + Playwright navegar + descargar PDF/Excel/CSV |
| `bancos_listar_movimientos(banco, cuenta, dias)` | ✅ | + scraping tabla movimientos |
| `bancos_verificar_pago_por_referencia(banco, referencia, monto)` | ✅ | + búsqueda por filtro |

## 6. Casos edge

| Caso | Comportamiento |
|---|---|
| 2FA timeout (usuario no completa en 60s) | Fallback mock + alerta |
| Banco bloquea por demasiados intentos | Espera 30 min + alert al usuario |
| Sesión expira durante operación | Re-login asistido (2FA otra vez) |
| Portal del banco cambió selectores | Detector + fallback mock + alerta |
| Cliente tiene > 100 movimientos en el mes | Pagina automáticamente o limita resultado |
| Formato CSV exportado por el banco difiere | Parser tolerante (extender `export_parser.py`) |
| IP bloqueada por geo-distinto al login | Notificar usuario + retry next session |
| Cuenta empresarial vs personal (URLs distintas) | Detector por usuario |

## 7. Dependencias

- **Librerías**: `playwright`, `playwright-stealth`, `pyotp` (TOTP para Banorte si aplica)
- **MCPs**: ninguno nuevo
- **Tiempo**: requiere usuario presente para 2FA (modo asistido headed por default)

## 8. Criterios de aceptación

Por banco (BBVA primero, luego replicar):

- [ ] Sin credenciales → mock idéntico al actual
- [ ] Con credenciales + opt-in → login real con 2FA asistido
- [ ] `bancos_listar_movimientos("bbva", cuenta, dias=30)` retorna movimientos REALES
- [ ] Cada movimiento tiene schema completo (fecha, tipo, monto, referencia, clave_rastreo)
- [ ] CSV/PDF descargado se guarda en `~/.cache/plugins-mx/bancos_mx/`
- [ ] Bitácora con cuenta_hash (nunca cuenta en claro)
- [ ] Test smoke con cuenta de prueba (cada banco tiene una)
- [ ] Sesión cacheada con TTL apropiado al banco

## 9. Esfuerzo estimado por banco

| Banco | Esfuerzo | Notas |
|---|---|---|
| **BBVA** (primero) | 80-120h | + arquitectura común reutilizable |
| **Banamex** | 60-80h | Reutiliza arquitectura |
| **Santander** | 50-70h | Biométrico complica un poco |
| **Banorte** | 50-70h | TOTP simplifica si seed disponible |
| **Hardening + docs comunes** | 20-40h | Una vez |
| **TOTAL** | **260-380 horas** | |

⚠ **Mantenimiento ongoing**: ~4-8h/banco/mes por cambios en portales (~16-32h/mes para 4 bancos).

## 10. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Bancos cambian portal | **Alta (mensual)** | Alto | Tests programados + alerta breakage + presupuestar mantenimiento |
| Bloqueo de cuenta por scraping | Media | **CRÍTICO** (afecta operación real) | Rate limit estricto + tiempos humanos + IP estable |
| 2FA no automatizable = UX rota | Alta | Medio | Modo headed con instrucciones claras |
| Robo de credenciales bancarias | Baja | **CRÍTICO** | Nunca .env en commit, considerar Vault/HSM |
| Banco cambia política y prohíbe automation | Media | Alto | Aceptable fallback a CSV manual export |
| Sesión expira en mid-batch | Alta | Bajo | Re-login automático |

## 11. Decisiones pendientes

- [ ] ¿Cuál banco implementar primero? (BBVA tiene mayor share — 30%)
- [ ] ¿Modo headed siempre, o headless cuando 2FA es TOTP?
- [ ] ¿Storage CSV/PDF descargado: ~/.cache o el usuario decide?
- [ ] ¿Implementar logout limpio al terminar o dejar sesión viva?
- [ ] ¿Aceptar BBVA Net Cash empresarial (URL distinta a personal)?

## 12. Plan de implementación

### Fase 1: Arquitectura común (40-60h)
1. `mp_bancos_mx/playwright_drivers/__init__.py` con base class `BancoPlaywrightDriver`
2. Métodos abstractos: `login()`, `descargar_estado()`, `listar_movs()`, `verificar_pago()`
3. Session cache shared
4. Detector breakage común
5. Logging estructurado

### Fase 2: BBVA (40-60h)
1. Driver BBVA hereda base
2. Login: usuario + password + 2FA app push
3. Descarga estado cuenta CSV
4. Parser CSV movimientos
5. Tests smoke

### Fase 3: Banamex (60-80h)
1. Driver Banamex
2. Login con token físico (asistido) o challenge
3. Resto idéntico patrón BBVA

### Fase 4: Santander + Banorte (100-140h paralelo)
1. Drivers respectivos
2. Variantes 2FA específicas

### Fase 5: Docs + tests integración (20-40h)
1. `mp_bancos_mx/README.md` actualizado
2. Setup guide por banco
3. Tests con cuenta sandbox (cada banco la tiene)
4. Update STATUS.md

## 13. Links

- Plan original: sección 6.2
- `mp_bancos_mx` actual: `mcp-servers/mp_bancos_mx/`
- BBVA banca digital: https://www.bbva.mx
- BBVA Net Cash (empresarial): https://www.bbvanetcash.mx/
- Banamex BNet: https://bancanetempresarial.banamex.com
- Santander: https://www.santandernet.com.mx
- Banorte empresarial: https://www.banorte.com/portales/empresarial
