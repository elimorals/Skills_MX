# Catálogos SAT — CFDI 4.0

Catálogos publicados en el Anexo 20 de la Resolución Miscelánea Fiscal. Vigencia consultar siempre en `https://www.sat.gob.mx`. Esta referencia es **espejo de los más usados**; los catálogos completos viven en el portal SAT.

## Tabla de contenidos
1. UsoCFDI (`c_UsoCFDI`)
2. FormaPago (`c_FormaPago`)
3. MetodoPago (`c_MetodoPago`)
4. RegimenFiscal (`c_RegimenFiscal`)
5. TipoDeComprobante
6. ObjetoImp
7. Exportacion
8. ClaveUnidad — más usadas
9. ClaveProdServ — patrones por giro
10. Moneda (`c_Moneda`)
11. TipoRelacion (cancelación, sustitución, devolución)

---

## 1. UsoCFDI (`c_UsoCFDI`)

| Clave | Descripción | Aplica PF | Aplica PM |
|---|---|---|---|
| G01 | Adquisición de mercancías | Sí | Sí |
| G02 | Devoluciones, descuentos o bonificaciones | Sí | Sí |
| G03 | Gastos en general | Sí | Sí |
| I01 | Construcciones | Sí | Sí |
| I02 | Mobiliario y equipo de oficina por inversiones | Sí | Sí |
| I03 | Equipo de transporte | Sí | Sí |
| I04 | Equipo de cómputo y accesorios | Sí | Sí |
| I05 | Dados, troqueles, moldes, matrices y herramental | Sí | Sí |
| I06 | Comunicaciones telefónicas | Sí | Sí |
| I07 | Comunicaciones satelitales | Sí | Sí |
| I08 | Otra maquinaria y equipo | Sí | Sí |
| D01 | Honorarios médicos, dentales y gastos hospitalarios | Sí | No |
| D02 | Gastos médicos por incapacidad o discapacidad | Sí | No |
| D03 | Gastos funerales | Sí | No |
| D04 | Donativos | Sí | Sí |
| D05 | Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación) | Sí | No |
| D06 | Aportaciones voluntarias al SAR | Sí | No |
| D07 | Primas por seguros de gastos médicos | Sí | No |
| D08 | Gastos de transportación escolar obligatoria | Sí | No |
| D09 | Depósitos en cuentas para el ahorro, primas por pensiones | Sí | No |
| D10 | Pagos por servicios educativos (colegiaturas) | Sí | No |
| S01 | Sin efectos fiscales | Sí | Sí |
| CP01 | Pagos | Sí | Sí |
| CN01 | Nómina | Sí | Sí |

**Reglas críticas**:
- Los `D0X` solo aplican a **personas físicas** (deducciones personales).
- `S01` se usa para factura global a público en general (con RFC genérico XAXX010101000).
- `CP01` y `CN01` son obligatorios para los comprobantes tipo P (pago) y N (nómina) respectivamente.

---

## 2. FormaPago (`c_FormaPago`)

| Clave | Descripción |
|---|---|
| 01 | Efectivo |
| 02 | Cheque nominativo |
| 03 | Transferencia electrónica de fondos (SPEI) |
| 04 | Tarjeta de crédito |
| 05 | Monedero electrónico |
| 06 | Dinero electrónico |
| 08 | Vales de despensa |
| 12 | Dación en pago |
| 13 | Pago por subrogación |
| 14 | Pago por consignación |
| 15 | Condonación |
| 17 | Compensación |
| 23 | Novación |
| 24 | Confusión |
| 25 | Remisión de deuda |
| 26 | Prescripción o caducidad |
| 27 | A satisfacción del acreedor |
| 28 | Tarjeta de débito |
| 29 | Tarjeta de servicios |
| 30 | Aplicación de anticipos |
| 31 | Intermediario pagos |
| 99 | Por definir (SOLO válido cuando MétodoPago = PPD) |

---

## 3. MetodoPago (`c_MetodoPago`)

| Clave | Descripción |
|---|---|
| PUE | Pago en una sola exhibición |
| PPD | Pago en parcialidades o diferido |

**Reglas críticas**:
- PUE + FormaPago en `{01..31}` (específico). FormaPago `99` con PUE = error.
- PPD + FormaPago `99` obligatorio. Cualquier otra FormaPago con PPD = error.
- PPD obliga a emitir CFDI tipo P (complemento de pago, REP) al recibir cada cobro.

---

## 4. RegimenFiscal (`c_RegimenFiscal`)

| Clave | Descripción | Aplica PF | Aplica PM |
|---|---|---|---|
| 601 | General de Ley Personas Morales | No | Sí |
| 603 | Personas Morales con Fines no Lucrativos | No | Sí |
| 605 | Sueldos y Salarios e Ingresos Asimilados a Salarios | Sí | No |
| 606 | Arrendamiento | Sí | No |
| 607 | Régimen de Enajenación o Adquisición de Bienes | Sí | No |
| 608 | Demás ingresos | Sí | No |
| 610 | Residentes en el Extranjero sin Establecimiento Permanente en México | Sí | Sí |
| 611 | Ingresos por Dividendos (socios y accionistas) | Sí | No |
| 612 | Personas Físicas con Actividades Empresariales y Profesionales (PFAE) | Sí | No |
| 614 | Ingresos por intereses | Sí | No |
| 615 | Régimen de los ingresos por obtención de premios | Sí | No |
| 616 | Sin obligaciones fiscales | Sí | No |
| 620 | Sociedades Cooperativas de Producción que optan por diferir sus ingresos | No | Sí |
| 621 | Incorporación Fiscal (RIF) — sin nuevas altas desde 2022, solo migraciones | Sí | No |
| 622 | Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras | No | Sí |
| 623 | Opcional para Grupos de Sociedades | No | Sí |
| 624 | Coordinados (autotransporte) | No | Sí |
| 625 | Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas | Sí | No |
| 626 | Régimen Simplificado de Confianza (RESICO) | Sí | Sí |

**El más relevante hoy para PyMEs y freelancers**: 626 (RESICO).

---

## 5. TipoDeComprobante

| Clave | Descripción |
|---|---|
| I | Ingreso (factura por venta de bien/servicio) |
| E | Egreso (nota de crédito, devolución, bonificación, descuento) |
| T | Traslado (movimiento de mercancía sin transferencia de propiedad — requiere Carta Porte) |
| N | Nómina (requiere complemento Nómina 1.2) |
| P | Pago (complemento de pago / REP) |

---

## 6. ObjetoImp (por concepto)

| Clave | Descripción |
|---|---|
| 01 | No objeto del impuesto |
| 02 | Sí objeto del impuesto |
| 03 | Sí objeto del impuesto y no obligado al desglose |
| 04 | Sí objeto del impuesto y no causa impuesto |

**Regla**: si cualquier concepto tiene ObjetoImp = 02, el nodo `Impuestos` a nivel comprobante es obligatorio. Si todos los conceptos son 01, no debe existir.

---

## 7. Exportacion

| Clave | Descripción |
|---|---|
| 01 | No aplica |
| 02 | Definitiva con clave A1 |
| 03 | Temporal |
| 04 | Definitiva con clave distinta a A1 o cuando no se cuente con pedimento |

Obligatorio en CFDI 4.0.

---

## 8. ClaveUnidad — más usadas (`c_ClaveUnidad`)

| Clave | Descripción |
|---|---|
| H87 | Pieza |
| E48 | Unidad de servicio |
| ACT | Actividad |
| KGM | Kilogramo |
| MTR | Metro |
| MTK | Metro cuadrado |
| MTQ | Metro cúbico |
| LTR | Litro |
| HUR | Hora |
| DAY | Día |
| MON | Mes |
| ANN | Año |

Para servicios profesionales lo más común es `E48` (unidad de servicio) o `ACT` (actividad).

---

## 9. ClaveProdServ — patrones por giro (`c_ClaveProdServ`)

El catálogo tiene ~52,000 claves de 8 dígitos. Estas son patrones de uso común:

### Servicios profesionales / consultoría
- `80141600` Servicios de consultoría empresarial
- `80111600` Servicios de personal de tecnología de información
- `80101500` Servicios de consultoría gerencial
- `81111500` Servicios de programación de computadoras
- `81111800` Diseño y desarrollo de software
- `82141500` Servicios de promoción y publicidad
- `93151501` Servicios de gestión de proyectos

### Marketing y agencias
- `82101500` Publicidad impresa
- `82101501` Publicidad en redes sociales
- `82141500` Servicios de mercadotecnia
- `82121500` Servicios de diseño gráfico
- `83121700` Producción de videos

### Comercio / venta de productos físicos
Varía mucho por SKU. Patrón: buscar la categoría más específica del producto en el portal SAT.

### Educación
- `86111600` Servicios de educación preescolar
- `86111700` Servicios de educación primaria
- `86111800` Servicios de educación secundaria
- `86121500` Servicios de educación profesional
- `86131500` Capacitación y entrenamiento

### Salud
- `85121500` Servicios de medicina
- `85121800` Servicios odontológicos
- `85121600` Servicios de psicología
- `85121700` Servicios de nutrición

### Talleres y refacciones automotrices
- `25172500` Refacciones y accesorios para vehículos automotores
- `78180100` Servicios de mantenimiento y reparación de vehículos

### Belleza y estética
- `90111600` Servicios de salones de belleza
- `42172300` Productos de cuidado personal

**Cuándo dudes**: usar la herramienta de búsqueda del SAT en `https://www.sat.gob.mx/consultas/53693/catalogo-de-productos-y-servicios` antes de elegir.

---

## 10. Moneda (`c_Moneda`)

| Clave | Descripción |
|---|---|
| MXN | Peso Mexicano |
| USD | Dólar Estadounidense |
| EUR | Euro |
| CAD | Dólar Canadiense |
| GBP | Libra Esterlina |
| JPY | Yen Japonés |
| CNY | Yuan Chino |
| XXX | Sin denominación (uso muy específico) |

**Regla**: si moneda ≠ MXN, agregar campo `TipoCambio` con valor positivo del DOF del día hábil anterior.

---

## 11. TipoRelacion (cancelación y sustitución)

| Clave | Descripción |
|---|---|
| 01 | Nota de crédito de los documentos relacionados |
| 02 | Nota de débito de los documentos relacionados |
| 03 | Devolución de mercancía sobre facturas o traslados previos |
| 04 | Sustitución de los CFDI previos |
| 05 | Traslados de mercancías facturados previamente |
| 06 | Factura generada por los traslados previos |
| 07 | CFDI por aplicación de anticipo |

Usado en el nodo `CfdiRelacionados` cuando un CFDI se relaciona con otro previo (sustitución por error, nota de crédito, etc.).

---

## Vigencia

Anexo 20 RMF vigente. Los catálogos cambian cada año en la Resolución Miscelánea. **Antes de poner un skill en producción**, verificar contra el portal SAT actual. Esta referencia se actualiza al menos una vez al año en este monorepo.
