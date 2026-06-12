---
name: compliance-lfpdppp
description: Cumplimiento de la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP) de México. Genera y revisa avisos de privacidad (integral, simplificado, corto), gestiona derechos ARCO (Acceso, Rectificación, Cancelación, Oposición), valida transferencias nacionales/internacionales de datos, identifica datos personales sensibles (salud, biométricos, financieros, ideología, origen étnico) y sus protecciones reforzadas, mapea bases de datos a obligaciones legales, y revisa cumplimiento de notificación de vulneraciones al INAI. Usar cuando el usuario diga aviso de privacidad, LFPDPPP, INAI, datos personales, derechos ARCO, transferencia de datos, consentimiento, GDPR Mexico, privacy policy mx, data protection. NO usar para GDPR europeo (otra ley), CCPA california (otra ley), ni para datos en posesión de gobierno (esa es LGPDPPSO, otra ley distinta).
allowed-tools: Read, Write, Edit
---

# Cumplimiento LFPDPPP

Ley vigente desde 2010, reformada varias veces. Es la ley que regula cómo cualquier privado (empresa, profesionista, freelance) maneja datos personales en México. INAI es la autoridad reguladora.

## Conceptos base

### Tres tipos de datos personales
1. **Datos personales** (default): nombre, RFC, CURP, teléfono, email, dirección, datos patrimoniales no sensibles.
2. **Datos personales sensibles**: salud, biométricos, origen racial/étnico, creencias religiosas/filosóficas, opiniones políticas, preferencia sexual, datos genéticos. **Requieren consentimiento expreso por escrito**.
3. **Datos personales financieros y patrimoniales**: ingresos, deudas, propiedades. **Requieren consentimiento expreso** (no por escrito necesariamente, pero sí inequívoco).

### Sujetos
- **Titular**: la persona dueña de los datos.
- **Responsable**: quien decide sobre el tratamiento (la empresa).
- **Encargado**: quien procesa por cuenta del responsable (proveedor de hosting, SaaS de CRM, etc.).

### Principios del tratamiento
Licitud, consentimiento, información, calidad, finalidad, lealtad, proporcionalidad, responsabilidad.

## Aviso de privacidad — los tres formatos obligatorios

### Aviso integral
Documento completo, debe estar **siempre disponible** (web, sucursal, etc.). Debe incluir:
1. Identidad y domicilio del responsable
2. Datos personales que se recaban
3. Finalidades del tratamiento (separar primarias vs secundarias)
4. Mecanismos para ejercer derechos ARCO
5. Si hay transferencias y a quién
6. Procedimiento de cambios al aviso
7. Mecanismo para limitar uso/divulgación
8. Cláusula de tratamiento de datos sensibles (si aplica)

### Aviso simplificado
Versión corta para entornos donde el integral no cabe (apps móviles, formularios de contacto, llamadas telefónicas). Debe incluir:
- Identidad del responsable
- Finalidades
- Cómo conocer el aviso integral (link, código QR)

### Aviso corto
Para anuncios físicos, banners cortos:
- Mención de que se recaban datos
- Cómo conocer el aviso integral

## Derechos ARCO

El titular puede ejercer:
- **A** Acceso: saber qué datos tienes, para qué los usas.
- **R** Rectificación: corregir datos inexactos o incompletos.
- **C** Cancelación: que dejes de tratarlos. Período de bloqueo y luego supresión.
- **O** Oposición: que cesen tratamientos específicos (no todos).

Plazo legal de respuesta: **20 días hábiles** desde recepción.

Formato de respuesta esperado por INAI:
- Recibo de la solicitud
- Identificación del titular (copia INE o equivalente para evitar suplantación)
- Resolución (concedida, parcialmente concedida, negada con motivo legal)

## Transferencias de datos

Si compartes datos con un tercero:
- **Encargado** (procesa para ti): no es transferencia legalmente. Pero necesitas contrato/cláusula de tratamiento.
- **Tercero** (procesa para sí mismo o para otro responsable): SÍ es transferencia. Generalmente requiere consentimiento del titular, salvo excepciones (mismo grupo corporativo, cumplimiento legal, etc.).

Transferencias internacionales: misma regla, pero si el país destino tiene nivel de protección menor, agregar cláusulas contractuales tipo.

## Vulneraciones de seguridad — notificación al INAI

Si hay un incidente que afecte la confidencialidad, integridad o disponibilidad de datos personales:
- Notificar al **titular afectado** sin dilación cuando pueda afectar significativamente sus derechos.
- Documentar el incidente, su gravedad, medidas tomadas.
- Si es masivo o sensible, evaluar notificación al INAI (no es siempre obligatoria, pero recomendable en casos graves).

## Lo que este skill hace por ti

1. **Generar aviso de privacidad integral** customizado por giro (clínica, escuela, agencia, ecommerce). Plantillas pre-hechas para los principales sectores.
2. **Generar aviso simplificado y corto** consistente con el integral.
3. **Revisar un aviso existente** y marcar elementos faltantes contra el checklist legal.
4. **Estructurar política de gestión de ARCO**: contacto, plazos, procedimiento.
5. **Identificar datos sensibles en un dataset** y alertar sobre obligaciones reforzadas.
6. **Generar cláusula de transferencia** para contratos con proveedores (encargados o terceros).

## Casos comunes por giro

- **Salud (clínica, consultorio)**: SIEMPRE hay datos sensibles (salud). Requiere consentimiento expreso por escrito. Aviso integral debe ser exhibido al paciente. Adicionalmente NOM-024 si hay expediente clínico electrónico.
- **Educación (colegios)**: datos de menores requieren consentimiento de padres/tutores. Cuidado con publicar fotos de alumnos sin consentimiento expreso.
- **Ecommerce**: datos financieros (pago) requieren consentimiento expreso (puede ser checkbox claro). Transferencia a procesador de pagos es transferencia (Stripe, MP) — debe estar declarada.
- **Agencia de marketing**: si manejan datos de clientes de sus clientes (subprocesador), son encargados frente al titular pero requieren contrato sólido con su cliente.
- **Recursos humanos / reclutamiento**: datos sensibles en perfiles (salud, antecedentes). Consentimiento expreso. Política de retención clara post-proceso.

## Salida esperada

Para "genérame el aviso de privacidad de [giro]":
- Aviso integral en formato markdown estructurado, listo para copiar/pegar a sitio web o exhibir.
- Aviso simplificado para formularios.
- Aviso corto para banners.
- Lista de obligaciones operativas adicionales (registrar consentimientos, designar responsable de privacidad, etc.).

Para revisar un aviso existente:
- Checklist con ✓ o ✗ por cada elemento legal obligatorio.
- Sugerencias de redacción para los elementos faltantes.
- Riesgo cualitativo (bajo / medio / alto) si se queda como está.

## Reservas y límites

Este skill no sustituye asesoría legal especializada. Para empresas grandes, sectores muy regulados (salud hospitalaria, banca, telecomunicaciones), o demandas activas, derivar a un abogado de protección de datos certificado.

Las multas del INAI van de ~$11k MXN (faltas menores) hasta $14M MXN (faltas graves repetidas). El daño reputacional suele ser mayor.

## ⚠ Datos que requieren verificación vigente

1. **Reformas LFPDPPP post-2017**: confirmar que el contenido refleja modificaciones de los últimos años.

2. **Multas INAI** ($11k a $14M MXN): rangos pueden haber actualizado.

3. **Plazo de 20 días hábiles para ARCO**: estable pero confirmar.

4. **Notificación de vulneraciones**: la obligación específica al INAI vs solo al titular puede tener actualizaciones.

5. **Tratamiento de datos transfronterizos**: las reglas sobre transferencia internacional con países de nivel de protección menor pueden tener cláusulas tipo actualizadas por INAI.

6. **Plantillas de aviso por sector** (`references/aviso-privacidad-plantillas.md`): basadas en patrones comunes, no en plantilla oficial INAI. Validar con abogado.

7. **Sectores específicos**:
   - **Salud**: la NOM-024 puede tener actualización; la PFPDPPP-Salud tiene guías específicas.
   - **Educación**: tratamiento de datos de menores tiene matices que esta plantilla cubre genéricamente.
   - **Financiero**: la regulación CNBV/CONDUSEF agrega obligaciones que este skill NO cubre.

**Antes de exponer a cliente**:
- Para sectores regulados: derivar a abogado especializado.
- Para PyMEs no reguladas: el contenido es razonable como punto de partida pero recomendar revisión legal antes de publicar aviso en sitio web.
