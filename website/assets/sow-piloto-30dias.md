# Statement of Work — Piloto Plugins MX 30 días

**Plantilla base · versión 1.0 · 2026-06-15**

> Este documento es la plantilla del SOW que firmamos cliente y proveedor antes de arrancar el piloto. Reemplaza todos los campos `{{ ... }}` y borra esta nota antes de firmar.

---

## 1. Partes

| Rol | Razón social | RFC | Representante | Email | WhatsApp |
|---|---|---|---|---|---|
| **Cliente** | `{{ RAZON_SOCIAL_CLIENTE }}` | `{{ RFC_CLIENTE }}` | `{{ NOMBRE_REPRESENTANTE_CLIENTE }}` | `{{ EMAIL_CLIENTE }}` | `{{ WHATSAPP_CLIENTE }}` |
| **Proveedor** | Elías Rashid Morales Mendoza | MORE990101AAA | Elías Rashid Morales Mendoza | elimoralsmendox@gmail.com | +52 271 142 8381 |

## 2. Alcance del piloto

### 2.1 Vertical objetivo

`{{ DESCRIBIR_EN_1_PARRAFO_QUE_PROBLEMA_REAL_DEL_CLIENTE_SE_RESUELVE }}`

Ejemplos: "Consolidar la consulta predial de la cartera de 47 inmuebles que actualmente se hace manual en 12 municipios distintos" · "Validar mensualmente el cumplimiento REPSE de los 18 proveedores subcontratados del cliente" · "Calcular el ISN correcto en los 7 estados donde el cliente opera nómina".

### 2.2 MCPs a implementar (máximo 3)

1. `mp_{{ MCP_1 }}` — `{{ JUSTIFICACION }}`
2. `mp_{{ MCP_2 }}` — `{{ JUSTIFICACION }}`
3. `mp_{{ MCP_3 }}` — `{{ JUSTIFICACION }}`

### 2.3 Workflow a entregar

Un (1) workflow Claude Agent SDK que orqueste los MCPs anteriores con:
- Input: `{{ DESCRIBIR_INPUT }}`
- Output: `{{ DESCRIBIR_OUTPUT_FORMATO_DESTINO }}`
- Frecuencia: `{{ MANUAL | DIARIO | SEMANAL | MENSUAL }}`

## 3. Métricas de éxito

El piloto se considera **exitoso** si al día 30 se cumplen las siguientes métricas medibles:

| # | Métrica | Línea base actual | Meta del piloto |
|---|---|---|---|
| 1 | `{{ EJ: tiempo consulta cartera completa }}` | `{{ EJ: 4 horas manuales }}` | `{{ EJ: <5 min automatizado }}` |
| 2 | `{{ EJ: cobertura cartera }}` | `{{ EJ: 60% (28/47) }}` | `{{ EJ: 100% (47/47) }}` |
| 3 | `{{ EJ: errores detectados }}` | `{{ EJ: indeterminado }}` | `{{ EJ: reporte semanal con flags }}` |

## 4. Calendario

| Semana | Fechas | Hito |
|---|---|---|
| 1 | `{{ FECHA_INICIO }}` a `{{ +7 días }}` | Kickoff + SOW firmado + lista de credenciales |
| 2 | `{{ +8 }}` a `{{ +14 }}` | Container desplegado + 1 consulta real ejecutada |
| 3 | `{{ +15 }}` a `{{ +21 }}` | Workflow productivo + equipo capacitado |
| 4 | `{{ +22 }}` a `{{ +30 }}` | Operación real + reporte ejecutivo + decisión |

## 5. Inversión

**Monto fijo del piloto:** $45,000 MXN (IVA no incluido)

Pago único anticipado, contra CFDI emitido desde RFC MORE990101AAA — clave régimen 612 (Personas Físicas con Actividades Empresariales y Profesionales).

Forma de pago aceptada: SPEI a CLABE `{{ CLABE_PROVEEDOR }}` o tarjeta vía Mercado Pago.

## 6. Credenciales que aporta el Cliente

El Cliente genera y opera las siguientes credenciales en su propia infraestructura. **El Proveedor NUNCA tiene acceso directo a estas credenciales** — el contenedor Docker corre en infraestructura del Cliente y las lee desde variables de entorno locales.

- [ ] e.firma SAT vigente (.cer + .key + contraseña)
- [ ] RFC + CIEC SAT del cliente
- [ ] NPIE IMSS (si aplica al vertical)
- [ ] Usuario INFONAVIT Empresarial (si aplica)
- [ ] Otras: `{{ ESPECIFICAR }}`

## 7. Responsabilidades

### 7.1 Del Cliente
- Generar las credenciales listadas en sección 6 antes del día 7.
- Designar un punto de contacto técnico disponible L-V 9-19h CDMX.
- Acceso al equipo operativo (3-8 personas) para sesión de capacitación de 2h en Semana 3.
- Pago anticipado del 100% antes del día 1 del piloto.

### 7.2 Del Proveedor
- Entregables semanales según calendario sección 4.
- Soporte directo por WhatsApp/email durante los 30 días.
- Confidencialidad total sobre cualquier dato del Cliente.
- Capacitación final + entrega de documentación operativa.

## 8. Confidencialidad

Ambas partes acuerdan no divulgar a terceros información del negocio, técnica o financiera intercambiada durante el piloto, salvo autorización expresa por escrito. La vigencia de esta cláusula es de 24 meses contados desde el día 30 del piloto.

## 9. Garantía de devolución parcial

Si al día 30 NO se cumplieron al menos 2 de las 3 métricas de éxito declaradas en sección 3 **por causas atribuibles al Proveedor**, el Cliente tiene derecho a una devolución del 50% del monto ($22,500 MXN).

Causas NO atribuibles al Proveedor (no aplica devolución):
- Credenciales aportadas por el Cliente con problemas.
- Cambios de alcance solicitados por el Cliente durante el piloto.
- Falta de disponibilidad del equipo del Cliente para capacitación.
- Cambios en portales gob.mx que excedan el SLA contractual posterior.

## 10. Cierre del piloto

Al día 30 hay tres salidas posibles:

1. **Renovar** → firmar contrato Producción anual a $18,000 MXN/mes (50% off el primer mes como bono por ser piloto).
2. **Ajustar** → renegociar alcance y firmar nuevo SOW (sin penalización).
3. **Cerrar** → recibir documentación final + datos generados, y dar por concluida la relación. Sin compromiso futuro.

## 11. Jurisdicción

Cualquier controversia se resolverá amistosamente. Si no es posible, las partes se someten a la jurisdicción de los tribunales civiles de la Ciudad de México, renunciando a cualquier otra que pudiera corresponderles por razón de su domicilio.

---

**Firmas digitales o autógrafas** (cualquiera aplica):

| Cliente | Proveedor |
|---|---|
| `{{ FIRMA_CLIENTE }}` | `{{ FIRMA_PROVEEDOR }}` |
| `{{ NOMBRE_REPRESENTANTE_CLIENTE }}` | Elías Rashid Morales Mendoza |
| Fecha: `{{ FECHA }}` | Fecha: `{{ FECHA }}` |
