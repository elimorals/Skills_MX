# Glosario fiscal mexicano

**Propósito**: Diccionario de términos del SAT, CFDI, LISR, LIVA, LFPDPPP. Útil cuando un skill menciona algo y necesitas contexto sin salir del monorepo.

**Audiencia**: Desarrolladores y usuarios sin background fiscal mexicano.

**Pre-lectura**: ninguna.

---

## A

### Acreditamiento
Aplicar impuesto pagado (típicamente IVA) contra impuesto a pagar del mismo periodo. Si pagaste $1,600 de IVA en gastos y trasladaste $5,000 de IVA en ingresos, "acreditas" los $1,600 y solo enteras $3,400 al SAT.

### Acuse de cancelación
Comprobante que emite el SAT al cancelar exitosamente un CFDI. Contiene el folio fiscal del CFDI cancelado y la fecha.

### Acumulación
Reconocer ingresos como parte de la base gravable. Pueden acumularse por flujo (al cobrar) o devengado (al facturar), según régimen.

### ALD (Anti-Lavado de Dinero)
Conjunto de obligaciones bajo la Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita. Pagos en efectivo > $645k MXN (montos vigentes verificar) detonan reporte.

### Anexo 20
Documento técnico del SAT que define el estándar XML del CFDI. Es donde están publicados todos los catálogos (UsoCFDI, FormaPago, etc.) y reglas de validación.

### Anticipo
Pago que recibes antes de definir el servicio/bien final. Tratamiento fiscal especial: tres CFDIs (ingreso por anticipo + egreso al aplicar + ingreso final).

### ARCO
Derechos del titular sobre sus datos personales bajo LFPDPPP: **A**cceso, **R**ectificación, **C**ancelación, **O**posición. Responsable debe atender en 20 días hábiles.

---

## B

### Base gravable
Monto sobre el cual se calcula un impuesto. En el ISR PFAE: utilidad fiscal (ingresos − deducciones).

### Bitácora de cancelación
Registro de todos los CFDIs cancelados con motivo, fecha, folio sustituto si aplica.

### Buzón Tributario
Canal oficial de comunicación SAT-contribuyente. Notificaciones, solicitudes de aceptación de cancelación, requerimientos.

---

## C

### Cadena Original
Texto plano del CFDI que se firma criptográficamente. Permite verificar integridad del documento.

### Carta Porte
Complemento del CFDI obligatorio para movimientos de mercancía (autotransporte, ferroviario, marítimo, aéreo). Vigente desde 2022 con versiones actualizadas (3.0 al cierre de mi training).

### CCT (Clave de Centro de Trabajo)
Identificador del SAT para escuelas: 10 caracteres alfanuméricos (ej. `09PPR1234A`). Estructura: 2 estado + 1 nivel + 4 número + 3 control.

### CFDI (Comprobante Fiscal Digital por Internet)
Factura electrónica mexicana. Versión vigente: 4.0 desde abr 2023. Reemplaza factura impresa y CFD anterior.

### CFDI tipo:
- **I** Ingreso: factura por venta
- **E** Egreso: nota de crédito, devolución
- **T** Traslado: movimiento de mercancía
- **N** Nómina: recibo de nómina
- **P** Pago: complemento de pago (REP)

### Cliente RESICO
Persona moral o física inscrita en Régimen Simplificado de Confianza (régimen 626). Tarifa ISR efectiva muy baja sobre flujo.

### CLABE
Clave Bancaria Estandarizada: 18 dígitos que identifican una cuenta bancaria mexicana para SPEI.
- Estructura: 3 banco + 3 plaza + 11 cuenta + 1 verificador.

### CONDUSEF
Comisión Nacional para la Protección y Defensa de los Usuarios de Servicios Financieros. Regula instituciones financieras y atiende quejas.

### Constancia de Situación Fiscal
Documento que emite el SAT con datos del contribuyente: RFC, razón social, domicilio, régimen, obligaciones. Útil para confirmar datos antes de facturar.

### Constancia de Servicios Educativos
Documento anual obligatorio que emite el colegio al padre para sustentar la deducción de colegiaturas (Art. 151 LISR fracción VIII).

### Contribuyente
Persona física o moral con obligaciones fiscales. Tiene RFC y régimen asignado.

### Coeficiente de Utilidad
Ratio usado en pagos provisionales PFAE: (utilidad fiscal del ejercicio anterior) / (ingresos del ejercicio anterior). Se calcula una vez al año y se usa los 12 meses siguientes.

### CURP
Clave Única de Registro de Población: 18 caracteres. Identifica personas físicas en México para fines administrativos. Distinto del RFC.
- Estructura: 4 apellidos+nombre + 6 fecha + 1 sexo + 5 estado/consonantes + 2 verificadores.

---

## D

### DOF (Diario Oficial de la Federación)
Publicación oficial del gobierno mexicano. Publica tipo de cambio diario USD/MXN entre otros datos.

### Deducción autorizada
Gasto que reduce la base gravable del ISR. Tiene requisitos (CFDI, forma de pago electrónica, relación con actividad, etc.).

### Deducciones personales (Art. 151 LISR)
Reducciones a la base gravable de personas físicas en declaración anual: médicos, intereses hipotecarios, colegiaturas, transporte escolar, primas de seguros.

### Devengado vs Flujo
- **Devengado**: contabilizar al facturar (cuando nace la obligación)
- **Flujo**: contabilizar al cobrar (cuando entra el dinero)
- RESICO PF: base flujo
- PFAE: base devengado para acumular, flujo para deducir

### Discrepancia fiscal
Diferencia significativa entre ingresos declarados y gastos/depósitos observados. SAT puede presumir ingresos no declarados (Art. 91 LISR).

### Domicilio fiscal
Dirección registrada ante SAT. Determina jurisdicción y obligaciones locales.

---

## E

### EFOS (Empresa que Factura Operaciones Simuladas)
Contribuyente publicado en la lista del Art. 69-B CFF. Sus CFDIs pueden ser desconocidos por el SAT, afectando deducciones del receptor.

### Efectivo > $2,000 MXN
Pagos en efectivo de gastos arriba de este monto NO son deducibles para ISR (Art. 27 frac. III LISR). Mismo principio aplica para deducciones personales.

### Emisor
Quien emite el CFDI (vende el bien o presta el servicio).

### Encargado
Tercero que trata datos personales por cuenta de un Responsable bajo LFPDPPP. No es transferencia legalmente; requiere contrato/cláusula.

### Esquema de pago
- **PUE**: Pago en Una sola Exhibición
- **PPD**: Pago en Parcialidades o Diferido

### Estímulo fiscal
Reducción de impuesto otorgada por decreto. Ej.: IVA 8% región fronteriza es estímulo fiscal.

### Exento
Operación que NO causa IVA por estar excluida por ley (no la misma cosa que tasa 0%).

### Exportación
- Bienes: movimiento de mercancía fuera de México
- Servicios: prestación aprovechada en el extranjero por residente extranjero

Ambos a tasa 0% IVA si cumplen requisitos del Art. 29 LIVA.

---

## F

### Factura global
CFDI que agrupa operaciones de público en general no facturadas individualmente, en un periodo (diario/semanal/mensual). RFC receptor genérico `XAXX010101000`, UsoCFDI `S01`.

### FIEL (e.firma)
Firma Electrónica Avanzada del SAT. Archivo .cer + .key + contraseña. Permite acceso a portales SAT y firma de documentos oficiales.

### Folio Fiscal
Sinónimo de UUID del CFDI. Cadena de 36 caracteres (8-4-4-4-12) hexadecimal.

### Forma de Pago (FormaPago)
Cómo se realizó el pago. Catálogo `c_FormaPago`. Ej.: 01 Efectivo, 03 SPEI, 04 TDC, 99 Por definir.

### Frontera norte / sur
Decreto que aplica IVA 8% e ISR reducido a contribuyentes con domicilio fiscal en municipios específicos. Vigencia se renueva por decreto.

---

## H

### Homoclave
3 últimos caracteres del RFC. Calculados por algoritmo SAT con tabla específica.

### Honorarios médicos
Servicios profesionales de medicina, odontología, psicología, nutrición. Régimen específico (Art. 142 LISR). Pago al PF EXENTO de IVA. Pago a clínica/hospital sí causa IVA al 16%.

---

## I

### IMSS
Instituto Mexicano del Seguro Social. Maneja seguridad social. Patrón retiene cuotas + paga su cuota patronal.

### INAI
Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales. Autoridad de LFPDPPP.

### INE
Identificación Nacional Electoral. Como credencial es lo más usado para identificar PF en México.

### InfoNavit
Instituto del Fondo Nacional de la Vivienda para los Trabajadores. Crédito hipotecario para trabajadores con esquema patronal.

### Inscripción al RFC
Trámite ante SAT para obtener RFC. PF requiere CURP + identificación + comprobante de domicilio. PM requiere acta constitutiva + RFC del representante.

### ISR (Impuesto Sobre la Renta)
Impuesto principal en México. PF tarifa progresiva (Art. 96 LISR), PM tasa 30% en general.

### IVA (Impuesto al Valor Agregado)
- 16% tasa general
- 8% región fronteriza (decreto)
- 0% tasa especial (exportación, alimentos básicos, medicinas patente, etc.)
- Exento (servicios médicos PF, vivienda PF, etc.)

### IVA acreditable vs trasladado
- **Trasladado**: el IVA que cobras al vender (te lo dan)
- **Acreditable**: el IVA que pagaste en gastos (lo deduces del trasladado)
- Diferencia: lo que enteras al SAT

---

## L

### LFPC (Ley Federal de Protección al Consumidor)
Ley que regula relación comerciante-consumidor. Autoridad: PROFECO. Establece garantías mínimas, prohíbe prácticas abusivas.

### LFPDPPP
Ley Federal de Protección de Datos Personales en Posesión de los Particulares. Vigente desde 2010. Regula tratamiento de datos por privados (empresas, profesionistas).

### LISR
Ley del Impuesto Sobre la Renta. Norma principal del ISR.

### LIVA
Ley del Impuesto al Valor Agregado.

---

## M

### M.N.
Moneda Nacional. Sufijo en montos en letra para CFDI y contratos. Indica que la cantidad es en pesos mexicanos.

### Método de Pago (MétodoPago)
Esquema de pago: PUE o PPD. Determina si se requiere REP posterior.

### MOR
Modelo Operativo de RESICO. Documento del SAT que explica cómo funciona el régimen.

### Multas
Sanciones económicas. SAT: por incumplimiento fiscal. INAI: por incumplimiento de LFPDPPP. PROFECO: por incumplimiento de LFPC.

---

## N

### NOM
Norma Oficial Mexicana. Estándar técnico publicado en el DOF.

Algunas relevantes:
- NOM-004-SSA3-2012: expediente clínico
- NOM-024-SSA3-2012: expediente clínico electrónico
- NOM-035-STPS-2018: factores de riesgo psicosocial en el trabajo
- NOM-051-SCFI/SSA1-2010: etiquetado de alimentos (con reformas 2020)
- NOM-251-SSA1-2009: prácticas de higiene en producción/preparación de alimentos
- NMX-D-003-IMNC: talleres automotrices

### Nómina (CFDI tipo N)
Recibo de nómina del trabajador. Patrón emite mensual/quincenal con complemento Nómina 1.2.

---

## O

### Obligaciones fiscales
Conjunto de deberes ante el SAT según régimen: declaraciones, pagos, retenciones, contabilidad, conservación de documentos.

### ObjetoImp
Campo del concepto CFDI 4.0 que indica si causa impuesto:
- 01 No objeto
- 02 Sí objeto
- 03 Sí objeto sin desglose
- 04 Sí objeto sin causa impuesto

### Opinión de cumplimiento
Documento que el SAT emite confirmando que el contribuyente está al corriente. Requisito para licitaciones y muchos contratos B2B.

---

## P

### PAC (Proveedor Autorizado de Certificación)
Empresa autorizada por SAT para timbrar CFDIs. Algunos populares: Facturama, SW Sapien, Solución Factible, Buzón E.

### Pago provisional
Pago mensual a cuenta del ISR anual. Día 17 del mes siguiente.

### Pagos2.0
Versión actual del complemento de pago para CFDI tipo P. Estructura el detalle del pago recibido y el CFDI al que aplica.

### Persona Física (PF)
Individuo con RFC y obligaciones fiscales propias.

### Persona Moral (PM)
Entidad jurídica con RFC: empresa, asociación, sociedad civil, fundación.

### PFAE (Personas Físicas con Actividades Empresariales y Profesionales)
Régimen 612. El más tradicional para freelancers e independientes. Deducciones, retenciones tradicionales.

### Plataformas Tecnológicas (régimen 625)
PF que recibe ingresos a través de Uber, Rappi, Airbnb, etc. La plataforma retiene ISR e IVA. Régimen creado en 2020.

### PPD (Pago en Parcialidades o Diferido)
MétodoPago cuando el cliente paga después de recibir bien/servicio. Requiere REP posterior por cada cobro.

### PUE (Pago en Una sola Exhibición)
MétodoPago cuando el cliente paga al recibir bien/servicio (o ya pagó). Sin REP posterior.

### Prelación
Orden de cobro entre acreedores cuando un deudor no puede pagar a todos. Acreedores garantizados primero.

### PROFECO
Procuraduría Federal del Consumidor. Aplica LFPC. Atiende quejas de consumidores y sanciona empresas.

---

## R

### Razón Social
Nombre legal de una persona moral, registrado en acta constitutiva y SAT.

### Receptor
Quien recibe el CFDI (compra el bien o paga el servicio).

### Régimen Fiscal
Categoría del contribuyente que determina sus obligaciones y forma de cálculo de impuestos. Catálogo `c_RegimenFiscal` (601-630).

Más relevantes hoy:
- 601 PM General
- 612 PFAE
- 626 RESICO

### REP (Recibo Electrónico de Pago)
Sinónimo de CFDI tipo P. Obligatorio cuando recibes pago de un CFDI emitido con MétodoPago = PPD.

### REPSE
Registro de Prestadoras de Servicios Especializados u Obras Especializadas. Obligatorio desde reforma de subcontratación 2021.

### RESICO (Régimen Simplificado de Confianza)
Régimen 626. Vigente desde 2022. Tarifa muy baja sobre flujo (PF: 1-2.5%). Pensado para PyMEs con ingresos hasta $3.5M anuales.

### Resolución Miscelánea Fiscal (RMF)
Documento anual del SAT con reglas específicas de cumplimiento de obligaciones. Se actualiza varias veces al año mediante "Resoluciones de Modificaciones".

### Retención
Cantidad que el receptor del servicio paga directamente al SAT en lugar de pagarla al emisor. El emisor declara como pago a cuenta de su impuesto anual.

Retenciones más comunes:
- 10% ISR + 10.6667% IVA: servicios profesionales PF→PM (PFAE)
- 1.25% ISR: servicios profesionales RESICO PF→PM
- 4% ISR + 4% IVA: autotransporte de carga PF→PM
- 6% IVA: servicios especializados REPSE

### RFC (Registro Federal de Contribuyentes)
Identificador del contribuyente. PF 13 caracteres, PM 12 caracteres.

### RVOE (Reconocimiento de Validez Oficial de Estudios)
Autorización SEP para que un colegio privado emita estudios con validez oficial. Sin RVOE, los estudios no son válidos para autoridad educativa.

---

## S

### SAT (Servicio de Administración Tributaria)
Autoridad fiscal federal mexicana.

### Sello SAT
Firma criptográfica que el SAT estampa sobre el CFDI timbrado. Garantiza autenticidad.

### Sello del emisor
Firma criptográfica del emisor sobre el CFDI antes del timbrado. Usa CSD (Certificado de Sello Digital).

### SEP
Secretaría de Educación Pública. Regula educación en México. Asigna CCT y RVOE.

### SPEI (Sistema de Pagos Electrónicos Interbancarios)
Sistema de transferencias bancarias interbancarias en México. Operado por Banxico. Casi instantáneo, sin costo para clientes finales típicamente.

### Subcontratación
Tercerización de servicios. Reformada en 2021 (eliminada salvo servicios especializados con REPSE).

### Sustitución de CFDI
Cancelar un CFDI con error y emitir uno nuevo correcto. Usa TipoRelacion 04 + motivo de cancelación 01 + folio sustituto.

---

## T

### Tasa 0%
Operación que SÍ causa IVA pero a tasa 0%. El emisor sí acumula IVA acreditable de sus gastos. **Distinto de exento.**

### Tasa Efectiva
Porcentaje real de impuesto sobre el ingreso bruto después de aplicar tarifa y deducciones.

### TC (Tipo de Cambio)
Relación USD/MXN o EUR/MXN, etc. Para CFDI: usar el del DOF del día hábil anterior al CFDI.

### Timbrado
Proceso de envío del CFDI al PAC para que lo firme y obtenga el sello del SAT.

### TipoFactor
Atributo de un impuesto en CFDI:
- "Tasa": aplica un porcentaje (puede ser 0)
- "Cuota": cantidad fija (raro)
- "Exento": no causa impuesto

### TipoRelacion
Catálogo `c_TipoRelacion` para relacionar CFDIs entre sí. Usado en sustitución, devolución, anticipo aplicado, etc.

---

## U

### UMA (Unidad de Medida y Actualización)
Valor que reemplaza al salario mínimo como referencia para cálculos legales/fiscales/multas. Se actualiza anualmente en febrero por INPC.

### Uso CFDI (UsoCFDI)
Para qué utilizará el receptor el comprobante. Catálogo `c_UsoCFDI`. Ej.: G03 gastos en general, D01 honorarios médicos, D10 colegiaturas.

### UUID
Universally Unique Identifier. En CFDI: el folio fiscal asignado por el SAT al timbrar.

---

## V

### Validador SAT
Servicio del SAT para verificar autenticidad de un CFDI usando UUID + RFC emisor + RFC receptor + total.

### Verificación de Comprobantes
Página del SAT donde cualquier persona puede consultar la situación de un CFDI con su UUID. URL pública.

---

## X

### XML del CFDI
Formato estructurado del CFDI. Lleva el cuerpo del comprobante + complementos + sellos.

### XSD
XML Schema Definition. Define la estructura de un XML. SAT publica XSD del CFDI 4.0 y de cada complemento.

---

## Códigos de RFC genéricos

- `XAXX010101000`: público en general nacional
- `XEXX010101000`: público en general extranjero
- `XAX010101000`: genérico para algunos sistemas legacy (no oficial)

---

## Ver también

- [glosario-tecnico.md](glosario-tecnico.md) — términos técnicos del monorepo
- [integracion-pac.md](integracion-pac.md) — detalle de PACs
- `_shared/cfdi-emision/references/catalogos-sat.md` — catálogos detallados
