# Seguridad — manejo de credenciales, secrets y datos personales

**Propósito**: prácticas para que el monorepo opere sin exponer credenciales ni violar privacidad.

**Audiencia**: cualquiera que opere plugins-mx con integraciones reales.

**Pre-lectura**: [glosario-fiscal-mx.md](glosario-fiscal-mx.md) (LFPDPPP).

---

## Principios

1. **Defensa en profundidad**: múltiples capas, no una sola
2. **Least privilege**: cada componente solo lo mínimo necesario
3. **Separation of duties**: dev de sandbox NO toca producción
4. **Audit trail**: logs de operaciones sensibles
5. **Fail closed**: si algo falla, default a denegar

---

## Manejo de secrets

### Variables de entorno

Todas las credenciales viven en `.env` LOCAL (nunca commiteado):

```bash
# .env (NO commitear)

# PAC
FACTURAMA_API_KEY=fk_live_xxx
FACTURAMA_ENV=production

# WhatsApp Business
GUPSHUP_API_KEY=xxx
GUPSHUP_APP_NAME=xxx

# Pagos
STRIPE_API_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxx

# CRM (opcional)
NOTION_TOKEN=secret_xxx
```

### `.env.example` (sí commiteado)

```bash
# .env.example (template público, sin valores reales)
FACTURAMA_API_KEY=tu_api_key_aqui
FACTURAMA_ENV=sandbox
GUPSHUP_API_KEY=tu_api_key
# ... etc
```

### Verificar que `.env` está en `.gitignore`

Ya está incluido pero verifica:
```bash
grep "^.env$" ~/plugins-mx/.gitignore
# Debe devolver: .env
```

### Si commiteaste `.env` por error

```bash
# 1. Borrar del último commit (si no se hizo push)
git rm --cached .env
git commit --amend -m "ajuste: remover .env por error"

# 2. Si ya hiciste push, rotar TODAS las credenciales que estuvieron expuestas
# (revocar las viejas + generar nuevas en cada servicio)

# 3. (Opcional pero recomendado) Reescribir historia con git-filter-repo
pip install git-filter-repo
git filter-repo --invert-paths --path .env
git push --force --all
```

---

## Rotación de credenciales

| Tipo | Frecuencia recomendada |
|---|---|
| API keys de pasarela de pagos | Cada 6 meses |
| API keys de PAC | Cada 12 meses |
| Tokens WhatsApp permanentes | Cada 12 meses |
| Webhook secrets | Cuando se modifique infra |
| Cuando empleado deja la organización | Inmediato |
| Tras detección de compromiso | Inmediato |

### Procedimiento de rotación

```
1. Generar nueva credencial en panel del servicio
2. Probar nueva credencial en sandbox/test
3. Actualizar `.env` local
4. Validar que servicio funciona
5. Revocar credencial vieja en panel
6. (Si hay equipo) notificar a todos para que actualicen `.env` local
```

---

## Permisos mínimos por servicio

### Facturama
- Solo permisos de timbrado, no de administración de cuenta
- Si tienen scopes: usar el más restrictivo

### Stripe
- API key con scope de "Restricted key" si solo necesitas crear pagos
- NO usar la "Secret key" (full access) para integraciones automáticas
- Crear key específica para webhooks

### WhatsApp Business
- Solo permisos del número específico que usarás
- NO acceso al Business Manager completo

### Mercado Pago
- Access token de aplicación específica
- NO access token de cuenta personal

---

## Datos personales (LFPDPPP)

### Lo que se considera dato personal en el contexto del monorepo

| Dato | Sensibilidad |
|---|---|
| Nombre completo | Normal |
| RFC, CURP | Normal |
| Email, teléfono | Normal |
| Domicilio fiscal | Normal |
| Datos bancarios (CLABE, cuenta) | Patrimonial — requiere consentimiento expreso |
| Datos de salud (clínica) | Sensible — consentimiento expreso por escrito |
| Datos de menores (colegios) | Sensible — consentimiento del tutor |
| Foto/video del cliente o de su auto | Normal pero requiere consentimiento si se publica |

### Reglas en el monorepo

1. **Almacenamiento mínimo**: solo lo necesario para operar
2. **Aislamiento por cliente**: cada cliente en su propio directorio (no en un solo CSV gigante)
3. **No transmisión a terceros sin aviso**: si un dato va a Stripe, Facturama, WA — esto es declarado en aviso de privacidad
4. **Encriptación en reposo recomendada**: para directorios con datos sensibles (clínica, colegio)
5. **Borrado al ejercer derecho de cancelación**: cuando el titular lo pida

### Encriptación local (opcional pero recomendada)

Para directorios con datos sensibles:

```bash
# Usar age (más simple que GPG)
brew install age

# Encriptar carpeta de clientes
tar -czf - clientes/ | age -r tu_public_key > clientes.tar.gz.age
rm -rf clientes/   # Solo después de confirmar el encrypted

# Desencriptar cuando necesites
age -d clientes.tar.gz.age | tar -xzf -
```

### Logs y datos sensibles

NUNCA loggear:
- Tokens, API keys completos (solo prefijo)
- Datos de tarjeta de pago
- Contraseñas
- CURPs completos en archivos accesibles públicamente

SÍ se puede loggear:
- Hash de identificadores
- IDs anonimizados
- Eventos sin datos sensibles

---

## Seguridad de operación

### Multi-factor authentication (MFA)

Activar en TODOS los servicios:
- SAT (e.firma + contraseña)
- Facturama / PAC
- Stripe / Mercado Pago
- WhatsApp Business
- GitHub donde vive el monorepo
- Google Workspace / Microsoft 365 si tienes

### Acceso al monorepo

Si trabajas con equipo:
- Repo privado en GitHub/GitLab
- Acceso por SSH key, no contraseña
- Branches protegidos en main
- Code review obligatorio para cambios en `_shared/`

### Auditoría

Para cada operación de timbrado, cobro o envío masivo, guardar:
- Timestamp
- Usuario que disparó
- Cliente / titular afectado
- Resultado
- (No los datos completos, solo metadatos)

En archivo `audit-log.json` (con su propio aviso de privacidad si los identificadores son personales).

---

## Vulneraciones de seguridad

### Si descubres una brecha

1. **Detener** la operación afectada
2. **Documentar** qué pasó, cuándo, qué datos
3. **Notificar al titular afectado** sin dilación si afecta significativamente sus derechos (Art. 20 LFPDPPP)
4. **Notificar al INAI** si es grave (criterio del responsable)
5. **Mitigar** y prevenir recurrencia
6. **Rotar credenciales** afectadas

### Plantilla de notificación a titular afectado

```
Estimado/a [Nombre]:

Le informamos que el día [fecha] detectamos un incidente que pudo
afectar la confidencialidad de sus datos personales en nuestra base.

Datos potencialmente afectados:
- [lista específica]

Acciones que estamos tomando:
- [lista de mitigaciones]

Acciones que le recomendamos:
- Cambiar contraseñas si aplican
- Vigilar movimientos en sus cuentas
- [otras según contexto]

Para mayor información o ejercicio de derechos ARCO:
[contacto]

Atentamente,
[Responsable]
```

---

## Backups

### Qué respaldar

- Directorios `clientes/`, `cfdi/`, `cobranza/`, `garantias/`
- `.env` (encriptado)
- Repo git (en remote redundante)
- `config/` específicos del usuario

### Frecuencia

- Diaria automatizada
- Semanal con verificación de restauración
- Mensual a almacenamiento offsite

### Implementación simple

```bash
# Backup diario a S3 (con encriptación)
0 23 * * * cd ~/plugins-mx && tar -czf - clientes/ cfdi/ | age -r $PUBKEY | aws s3 cp - s3://my-bucket/plugins-mx/$(date +%Y%m%d).tar.gz.age
```

### Restauración periódica

Al menos una vez al mes, verificar que un backup se puede restaurar:
```bash
aws s3 cp s3://my-bucket/plugins-mx/YYYYMMDD.tar.gz.age - | age -d -i $PRIVKEY | tar -xzf - -C /tmp/test-restore
```

---

## Checklist de seguridad por etapa

### Setup inicial
- [ ] `.gitignore` incluye `.env`, `secrets/`, credenciales
- [ ] `.env` creado y poblado
- [ ] Verificar repo es privado si tiene clientes reales
- [ ] MFA activado en todos los servicios

### Antes de primer cliente real
- [ ] Encriptación de carpeta de clientes activada
- [ ] Aviso de privacidad enviado a clientes
- [ ] Política de retención documentada
- [ ] Backup automatizado funcionando
- [ ] Plan de respuesta a incidentes documentado

### Operación continua
- [ ] Rotación de credenciales según calendario
- [ ] Revisión de logs mensual
- [ ] Pruebas de backup mensuales
- [ ] Auditoría de accesos trimestral

### Si dejas de operar el plugin
- [ ] Revocar todas las credenciales activas
- [ ] Borrar datos personales (o devolver al titular conforme política)
- [ ] Avisar a clientes de la baja

---

## Ver también

- [compliance-checklist.md](compliance-checklist.md) — cumplimiento sectorial
- `_shared/compliance-lfpdppp/SKILL.md` — skill de protección de datos
- [integracion-pac.md](integracion-pac.md) — credenciales PAC
- [integracion-pagos.md](integracion-pagos.md) — credenciales pasarelas
