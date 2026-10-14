---
name: compliance-lfpdppp
description: Cumplimiento de la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP) de México. Genera y revisa avisos de privacidad (integral, simplificado, corto), gestiona derechos ARCO (Acceso, Rectificación, Cancelación, Oposición), valida transferencias nacionales/internacionales de datos, identifica datos personales sensibles (salud, biométricos, financieros, ideología, origen étnico) y sus protecciones reforzadas, mapea bases de datos a obligaciones legales, y revisa cumplimiento de notificación de vulneraciones a titulares. Usar cuando el usuario diga aviso de privacidad, LFPDPPP, INAI, Secretaría Anticorrupción, datos personales, derechos ARCO, transferencia de datos, consentimiento, GDPR Mexico, privacy policy mx, data protection. NO usar para GDPR europeo (otra ley), CCPA california (otra ley), ni para datos en posesión de gobierno (esa es LGPDPPSO, otra ley distinta).
allowed-tools: Read, Write, Edit
---

# Cumplimiento LFPDPPP

**Nueva LFPDPPP publicada en el DOF el 20-mar-2025** (vigente desde el 21-mar-2025; última reforma DOF 14-nov-2025). Abrogó la ley de 2010. Regula cómo cualquier particular (empresa, profesionista, freelance) trata datos personales en México. El INAI se extinguió: la autoridad es la **Secretaría Anticorrupción y Buen Gobierno (SABG)**. Ante dudas de vigencia, citar artículos de la ley de 2025, no de la de 2010.

## Conceptos base

### Tres tipos de datos personales
1. **Datos personales** (default): nombre, RFC, CURP, teléfono, email, dirección, datos patrimoniales no sensibles.
2. **Datos personales sensibles**: salud, biométricos, origen racial/étnico, creencias religiosas/filosóficas, opiniones políticas, preferencia sexual, datos genéticos. **Requieren consentimiento expreso y por escrito** (firma autógrafa, firma electrónica o mecanismo de autenticación) — Art. 8.
3. **Datos personales financieros y patrimoniales**: ingresos, deudas, propiedades. **Requieren consentimiento expreso** (verbal, escrito, electrónico o signo inequívoco) — Art. 7. Para el resto, el consentimiento tácito es la regla general.

### Sujetos
- **Titular**: la persona dueña de los datos.
- **Responsable**: quien decide sobre el tratamiento (la empresa).
- **Encargado**: quien procesa por cuenta del responsable (proveedor de hosting, SaaS de CRM, etc.).

### Principios del tratamiento
Licitud, consentimiento, información, calidad, finalidad, lealtad, proporcionalidad, responsabilidad.

## Aviso de privacidad — integral y simplificado (Arts. 15-16)

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
Obligatorio cuando los datos se obtienen por medios electrónicos, ópticos, sonoros o visuales (web, apps, llamadas) — Art. 16 fr. II. Debe contener al menos las fracciones I a IV del Art. 15 (identidad y domicilio del responsable, datos que se recaban, finalidades, etc.) y el sitio donde consultar el integral.

### Aviso "corto"
La ley de 2025 solo regula integral y simplificado. Un banner o letrero que remita al aviso integral es buena práctica, pero no sustituye al simplificado.

## Derechos ARCO

El titular puede ejercer:
- **A** Acceso: saber qué datos tienes, para qué los usas.
- **R** Rectificación: corregir datos inexactos o incompletos.
- **C** Cancelación: que dejes de tratarlos. Período de bloqueo y luego supresión.
- **O** Oposición: que cesen tratamientos específicos (no todos).

Plazo legal de respuesta: **20 días hábiles** desde recepción; si procede, se hace efectivo dentro de los **15 días hábiles** siguientes (Art. 31). Si el titular no está conforme, puede presentar solicitud de protección de derechos ante la SABG dentro de los 15 días siguientes a la respuesta.

Formato de respuesta recomendado:
- Recibo de la solicitud
- Identificación del titular (copia INE o equivalente para evitar suplantación)
- Resolución (concedida, parcialmente concedida, negada con motivo legal)

## Transferencias de datos

Si compartes datos con un tercero:
- **Encargado** (procesa para ti): no es transferencia legalmente. Pero necesitas contrato/cláusula de tratamiento.
- **Tercero** (procesa para sí mismo o para otro responsable): SÍ es transferencia. Generalmente requiere consentimiento del titular, salvo excepciones (mismo grupo corporativo, cumplimiento legal, etc.).

Transferencias internacionales: misma regla, pero si el país destino tiene nivel de protección menor, agregar cláusulas contractuales tipo.

## Vulneraciones de seguridad — notificación a titulares

Si hay un incidente que afecte la confidencialidad, integridad o disponibilidad de datos personales:
- Informar **de forma inmediata** al titular cuando afecte de forma significativa sus derechos patrimoniales o morales (Art. 19).
- Documentar el incidente, su gravedad, medidas tomadas.
- La ley no impone notificar a la autoridad; la SABG puede verificar y sancionar (Arts. 54 y 58).

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

Multas (Art. 59, impuestas por la SABG): 100 a 160,000 UMA o 200 a 320,000 UMA según la infracción, más 100 a 320,000 UMA si es reiterada; hasta el doble con datos sensibles. Con UMA 2026 = $117.31: de **$11,731** a **$37.5 M MXN** por infracción (hasta ~$75 M con datos sensibles).

## ⚠ Datos que requieren verificación vigente

1. **Ley de 2025**: revisado contra el texto vigente (DOF 20-mar-2025, última reforma 14-nov-2025). El Reglamento de la ley de 2025 puede cambiar detalles operativos.

2. **Multas**: en UMA (Art. 59). UMA 2026 = $117.31 (vigente 1-feb-2026 a 31-ene-2027, INEGI/DOF 9-ene-2026).

3. **Plazo ARCO**: 20 días hábiles + 15 para hacerlo efectivo (Art. 31).

4. **Vulneraciones**: aviso inmediato al titular (Art. 19); sin obligación legal de notificar a la autoridad.

5. **Transferencias internacionales**: revisar lineamientos que emita la SABG.

6. **Plantillas de aviso por sector** (`references/aviso-privacidad-plantillas.md`): basadas en patrones comunes, no en plantilla oficial. Validar con abogado.

7. **Sectores específicos**:
   - **Salud**: la NOM-024 puede tener actualización; la PFPDPPP-Salud tiene guías específicas.
   - **Educación**: tratamiento de datos de menores tiene matices que esta plantilla cubre genéricamente.
   - **Financiero**: la regulación CNBV/CONDUSEF agrega obligaciones que este skill NO cubre.

**Antes de exponer a cliente**:
- Para sectores regulados: derivar a abogado especializado.
- Para PyMEs no reguladas: el contenido es razonable como punto de partida pero recomendar revisión legal antes de publicar aviso en sitio web.
