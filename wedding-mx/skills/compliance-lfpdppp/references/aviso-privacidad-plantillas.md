# Plantillas de Aviso de Privacidad LFPDPPP

Tres niveles de aviso obligatorios + plantillas por sector. Adaptar campos `{{VARIABLE}}` al responsable específico.

## Aviso de Privacidad Integral — plantilla base

```markdown
# Aviso de Privacidad Integral

**Responsable**: {{RAZON_SOCIAL_O_NOMBRE}}, con domicilio en {{DOMICILIO_COMPLETO}}, México, en lo sucesivo "El Responsable".

## 1. Datos personales que recabamos

El Responsable recaba los siguientes datos personales:

**Datos de identificación**:
{{LISTA_DATOS_IDENTIFICACION}}
(p.ej.: nombre completo, RFC, CURP, dirección, teléfono, correo electrónico)

**Datos de contacto**:
{{LISTA_DATOS_CONTACTO}}

**Datos patrimoniales y/o financieros** (cuando aplique):
{{LISTA_DATOS_FINANCIEROS}}
(p.ej.: forma de pago, número de tarjeta -solo terminación-, comprobantes fiscales)

**Datos sensibles** (cuando aplique):
{{LISTA_DATOS_SENSIBLES}}
(p.ej.: datos de salud, biométricos, origen étnico)

> Si recabamos datos sensibles, requerimos su **consentimiento expreso por escrito** mediante la firma de este aviso o casilla equivalente.

## 2. Finalidades del tratamiento

### Finalidades primarias (necesarias para la relación)
{{LISTA_FINALIDADES_PRIMARIAS}}
(p.ej.: prestación del servicio contratado, facturación CFDI, contacto operativo, cumplimiento de obligaciones fiscales)

### Finalidades secundarias (opcionales)
{{LISTA_FINALIDADES_SECUNDARIAS}}
(p.ej.: envío de promociones, comunicaciones de marketing, estudios estadísticos, encuestas de satisfacción)

Si no desea que sus datos sean tratados para alguna finalidad secundaria, puede manifestarlo enviando un correo a {{EMAIL_CONTACTO_PRIVACIDAD}} antes de que comencemos el tratamiento.

## 3. Transferencias de datos

{{TRANSFERENCIAS}}

Ejemplos comunes a declarar:
- Procesadores de pago: Stripe, Mercado Pago (cuando aplique)
- PAC para timbrado de CFDI: {{NOMBRE_PAC}}
- Plataforma de mensajería: Meta Platforms Inc. (WhatsApp Business)
- Servicios en la nube: {{PROVEEDOR_NUBE}}
- Contadores externos: {{NOMBRE_DESPACHO}}
- Autoridades cuando lo requiera la ley

Para las transferencias mencionadas no requerimos su consentimiento por estar en los supuestos previstos en el artículo 37 de la LFPDPPP.

## 4. Derechos ARCO

Usted tiene derecho a conocer qué datos personales tenemos de usted, para qué los utilizamos y las condiciones del uso (**Acceso**). Asimismo, es su derecho solicitar la corrección de su información personal en caso de que esté desactualizada, sea inexacta o incompleta (**Rectificación**); que la eliminemos de nuestros registros o bases de datos cuando considere que la misma no está siendo utilizada conforme a los principios, deberes y obligaciones previstos en la normativa (**Cancelación**); así como oponerse al uso de sus datos personales para fines específicos (**Oposición**).

Para ejercer cualquier derecho ARCO, envíe su solicitud a:

- Correo: {{EMAIL_ARCO}}
- Dirección física: {{DOMICILIO_ARCO}}
- Atención: Responsable de Datos Personales

Su solicitud debe contener:
1. Nombre completo y domicilio
2. Identificación oficial vigente (copia)
3. Descripción clara del derecho que ejerce
4. Cualquier elemento que facilite la localización de sus datos

Responderemos en un plazo máximo de **20 días hábiles** a partir de la recepción de su solicitud.

## 5. Revocación del consentimiento

Puede revocar su consentimiento en cualquier momento siguiendo el mismo procedimiento que para derechos ARCO. La revocación no tendrá efecto retroactivo.

## 6. Limitación del uso o divulgación

Para limitar el uso o divulgación de sus datos para fines secundarios, puede registrarse en el Registro Público para Evitar Publicidad (REPEP) de la PROFECO o enviar solicitud a nuestro correo {{EMAIL_CONTACTO_PRIVACIDAD}}.

## 7. Uso de cookies y tecnologías de rastreo

{{SECCION_COOKIES_SI_APLICA}}

Nuestro sitio web puede usar cookies y tecnologías similares para mejorar su experiencia. Puede configurar su navegador para rechazarlas.

## 8. Modificaciones al aviso

El Responsable se reserva el derecho de modificar este aviso. Las modificaciones se publicarán en {{MEDIO_DE_PUBLICACION}} y se comunicarán {{COMO_NOTIFICAMOS_CAMBIOS}}.

## 9. Autoridad

Si considera que su derecho de protección de datos personales ha sido vulnerado, puede acudir al INAI (Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales): www.inai.org.mx.

---

**Fecha de última actualización**: {{FECHA}}
```

## Aviso de Privacidad Simplificado

```markdown
{{RAZON_SOCIAL}} recaba sus datos personales para {{FINALIDADES_RESUMEN}} (p.ej.: prestar el servicio contratado y facturar).

Si no desea que sus datos sean utilizados para finalidades secundarias (marketing y encuestas), manifiéstelo a {{EMAIL}}.

Consulte el aviso integral completo en: {{URL_AVISO_INTEGRAL}}.
```

Pensado para formularios web, ventanas modales, llamadas de venta donde no hay espacio para el integral.

## Aviso de Privacidad Corto

```markdown
Datos personales tratados por {{RAZON_SOCIAL}}. Consulte el aviso integral en {{URL_CORTA_O_QR}}.
```

Pensado para banners físicos, anuncios pequeños, recibos de papel.

---

## Plantillas adaptadas por sector

### Clínica/consultorio médico

Sección 1 — agregar:
```
Datos sensibles de salud: historial médico, padecimientos, alergias,
medicación, resultados de estudios, imágenes diagnósticas.

Estos datos requieren su consentimiento EXPRESO POR ESCRITO mediante la
firma del consentimiento informado adjunto.
```

Sección 2 finalidades primarias — incluir:
- Integración del expediente clínico conforme a NOM-004-SSA3-2012
- Continuidad del tratamiento
- Comunicación con especialistas referidos (con su consentimiento previo)

### Colegio / institución educativa

Sección 1 — agregar:
```
Datos de menores de edad: tratamos datos personales de alumnos menores
únicamente con consentimiento expreso del padre, madre o tutor.

Datos de tutores: nombre, identificación, parentesco, contacto de emergencia,
información laboral relevante para becas o financiamiento.
```

Transferencias — declarar:
- SEP y autoridades educativas para reportes obligatorios
- Plataformas tecnológicas educativas (Google Workspace for Education, Microsoft 365)

### Ecommerce / tienda online

Sección 1 datos financieros — declarar:
```
Para procesamiento de pagos: información de tarjeta (manejada directamente
por nuestro procesador certificado PCI-DSS, nosotros solo guardamos
los últimos 4 dígitos para referencia).
```

Transferencias — declarar:
- Procesador de pagos: {{PROCESADOR}}
- Paquetería: {{PAQUETERIAS}}
- Plataforma e-commerce: Shopify Inc., Mercado Libre, Amazon

### Salón de belleza / spa / estética

Sección 1 — agregar (si aplica):
```
Fotografías "antes/después" de tratamientos: solo con su consentimiento
expreso por escrito mediante el formato de consentimiento de uso de imagen.
No se publicarán sin autorización adicional para cada caso.
```

### Agencia de marketing

Sección crítica adicional:
```
Datos de clientes de nuestros clientes: cuando manejamos campañas
para terceros, podemos acceder a datos personales de sus contactos.
Actuamos como encargados frente al titular y como responsables frente
a obligaciones fiscales. El contrato con nuestros clientes establece
cláusulas de tratamiento de datos personales.
```

### Despacho legal

Sección — agregar:
```
Datos sensibles relacionados con asuntos legales: información sobre
procesos judiciales, situaciones familiares, patrimoniales, laborales
o personales del cliente, que sean necesarios para el ejercicio del
servicio profesional.

Estos datos están protegidos por el secreto profesional del abogado.
```

---

## Checklist de obligaciones operativas (más allá del aviso)

Para que el responsable cumpla LFPDPPP no basta el aviso. Lista mínima:

- [ ] **Designar Responsable de Datos Personales** dentro de la organización (puede ser una persona o departamento).
- [ ] **Mantener Sistema de Gestión de Seguridad de Datos Personales** documentado (políticas, procedimientos, controles).
- [ ] **Registrar consentimientos** demostrables (opt-in con timestamp para marketing).
- [ ] **Capacitar al personal** que accede a datos personales al menos anualmente.
- [ ] **Cláusulas de tratamiento de datos** en contratos con encargados (proveedores, hosting, SaaS).
- [ ] **Procedimiento documentado de atención de ARCO** con plazo de 20 días hábiles.
- [ ] **Bitácora de incidentes** y procedimiento de notificación a titulares en caso de vulneración.
- [ ] **Política de retención** de datos personales (cuánto tiempo se guardan y cuándo se eliminan).
- [ ] **Aviso de privacidad accesible** en todos los puntos de recolección (web, formularios, mostrador).

---

## Cuándo derivar a un abogado de protección de datos

- Empresa con > 50 empleados o > 10,000 titulares en BD
- Tratamiento de datos sensibles a escala (clínica grande, hospital, escuela grande)
- Reportes de incidentes / vulneraciones con potencial impacto significativo
- Demandas o procedimientos del INAI activos
- Operaciones internacionales con transferencias trans-fronterizas regulares

Este skill genera plantillas y revisa cumplimiento estructural. No sustituye asesoría legal especializada para los casos anteriores.
