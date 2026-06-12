# Complementos del CFDI 4.0

El CFDI base puede llevar **complementos** adicionales que agregan información específica para casos particulares. Cada complemento tiene su propio XSD publicado por el SAT.

## Complementos más usados

| Complemento | Cuándo se requiere | Vigente versión |
|---|---|---|
| **Pagos 2.0** | CFDI tipo P (REP), cuando un CFDI tipo I fue PPD y se recibe pago | 2.0 |
| **Nómina 1.2** | CFDI tipo N para recibo de nómina | 1.2 |
| **Carta Porte** | Movimiento de mercancía (CFDI tipo T o I + traslado) | 3.0+ |
| **INE** | Pagos a partidos políticos y precandidatos | 1.1 |
| **Comercio Exterior** | Exportación de bienes | 2.0+ |
| **Notarios Públicos** | Operaciones notariales | 1.0 |
| **Instituciones Educativas (InsEduc)** | Colegiaturas deducibles (UsoCFDI D10) | 1.0 |
| **Donatarias** | Recibos de donativos a donatarias autorizadas | 1.1 |
| **Concepto Por Cuenta de Terceros** | Cuando facturas por cuenta de un tercero | 1.0 |
| **Vehículo Usado** | Compraventa de auto usado | 1.0 |
| **Aerolíneas** | Cargos adicionales en boleto aéreo | 1.0 |
| **Estado de Cuenta de Combustible** | Monedero electrónico de combustible | 1.2 |

---

## Pagos 2.0 (REP)

### Cuándo usar
Cuando emitiste un CFDI tipo I con `MetodoPago = PPD` y posteriormente recibes un pago.

### Plazo de emisión
Día **10 del mes siguiente** al pago recibido.

### Estructura básica

```xml
<cfdi:Complemento>
  <pago20:Pagos Version="2.0">
    <pago20:Totales 
      MontoTotalPagos="..."
      TotalTrasladosBaseIVA16="..."
      TotalTrasladosImpuestoIVA16="..."/>
    <pago20:Pago
      FechaPago="2026-03-15T14:30:00"
      FormaDePagoP="03"
      MonedaP="MXN"
      Monto="11600.00">
      <pago20:DoctoRelacionado
        IdDocumento="<UUID del CFDI original>"
        Serie="..."
        Folio="..."
        MonedaDR="MXN"
        EquivalenciaDR="1"
        NumParcialidad="1"
        ImpSaldoAnt="11600.00"
        ImpPagado="11600.00"
        ImpSaldoInsoluto="0.00"
        ObjetoImpDR="02">
        <pago20:ImpuestosDR>
          <pago20:TrasladosDR>
            <pago20:TrasladoDR
              BaseDR="10000.00"
              ImpuestoDR="002"
              TipoFactorDR="Tasa"
              TasaOCuotaDR="0.160000"
              ImporteDR="1600.00"/>
          </pago20:TrasladosDR>
        </pago20:ImpuestosDR>
      </pago20:DoctoRelacionado>
    </pago20:Pago>
  </pago20:Pagos>
</cfdi:Complemento>
```

### Casos comunes
- **Pago único de un CFDI PPD**: NumParcialidad=1
- **Múltiples parcialidades**: emitir REP por cada cobro con NumParcialidad incremental
- **Cancelación de pago (cheque devuelto)**: emitir CFDI tipo E + cancelar el REP correspondiente

---

## Nómina 1.2

### Cuándo usar
CFDI tipo N para recibo de nómina (mensual, quincenal, semanal según política del patrón).

### Estructura básica

```xml
<cfdi:Complemento>
  <nomina12:Nomina 
    Version="1.2"
    TipoNomina="O"
    FechaPago="2026-03-31"
    FechaInicialPago="2026-03-16"
    FechaFinalPago="2026-03-31"
    NumDiasPagados="15">
    <nomina12:Emisor RegistroPatronal="A0123456789"/>
    <nomina12:Receptor
      Curp="..." NumSeguridadSocial="..."
      FechaInicioRelLaboral="..."
      Antigüedad="P3Y6M0D"
      TipoContrato="01"
      Sindicalizado="No"
      TipoJornada="01"
      TipoRegimen="02"
      NumEmpleado="..."
      Departamento="..."
      Puesto="..."
      RiesgoPuesto="1"
      PeriodicidadPago="04"
      Banco="012"
      CuentaBancaria="..."
      SalarioBaseCotApor="..."
      SalarioDiarioIntegrado="..."/>
    <nomina12:Percepciones
      TotalSueldos="..."
      TotalGravado="..."
      TotalExento="...">
      <nomina12:Percepcion
        TipoPercepcion="001"
        Clave="001"
        Concepto="Sueldo"
        ImporteGravado="..."
        ImporteExento="0"/>
    </nomina12:Percepciones>
    <nomina12:Deducciones
      TotalOtrasDeducciones="..."
      TotalImpuestosRetenidos="...">
      <nomina12:Deduccion
        TipoDeduccion="001"
        Clave="001"
        Concepto="Seguridad Social"
        Importe="..."/>
      <nomina12:Deduccion
        TipoDeduccion="002"
        Clave="002"
        Concepto="ISR"
        Importe="..."/>
    </nomina12:Deducciones>
  </nomina12:Nomina>
</cfdi:Complemento>
```

### Catálogos referenciados
- `c_TipoNomina`: O Ordinaria, E Extraordinaria
- `c_TipoContrato`: 01-08
- `c_TipoJornada`: 01-07
- `c_TipoRegimen`: 02-13
- `c_PeriodicidadPago`: 01-99
- `c_TipoPercepcion`: 001-051 (muchas claves específicas)
- `c_TipoDeduccion`: 001-107

---

## Carta Porte 3.0

### Cuándo usar
- Movimiento de mercancías por autotransporte federal
- Marítimo, aéreo o ferroviario
- Aplica si la mercancía se mueve por carreteras federales

### Estructura altamente compleja
Incluye:
- Origen y destino
- Ruta
- Mercancías con desglose de cantidad, unidad, peso, valor
- Vehículo (placas, año, tipo)
- Operador (nombre, RFC, licencia)
- Si es propio o subcontratado
- Aseguradora

### Importante
Carta Porte ha tenido **múltiples versiones y cambios** desde su introducción en 2022. **Verificar versión vigente y obligaciones específicas** para tu giro.

---

## Comercio Exterior 2.0

### Cuándo usar
Exportación definitiva o temporal de bienes.

### Estructura básica

```xml
<cfdi:Complemento>
  <cce20:ComercioExterior
    Version="2.0"
    TipoOperacion="2"
    ClaveDePedimento="A1"
    CertificadoOrigen="0"
    Subdivision="0"
    Observaciones="..."
    TipoCambioUSD="18.50"
    TotalUSD="10000.00">
    <cce20:Emisor>
      <cce20:Domicilio
        Calle="..." NumeroExterior="..."
        Colonia="..." Localidad="..." Municipio="..."
        Estado="..." Pais="MEX" CodigoPostal="..."/>
    </cce20:Emisor>
    <cce20:Receptor
      NumRegIdTrib="...">
      <cce20:Domicilio
        Calle="..." NumeroExterior="..."
        Colonia="..." Localidad="..." Municipio="..."
        Estado="..." Pais="USA" CodigoPostal="..."/>
    </cce20:Receptor>
    <cce20:Mercancias>
      <cce20:Mercancia
        NoIdentificacion="..."
        FraccionArancelaria="..."
        CantidadAduana="1"
        UnidadAduana="01"
        ValorUnitarioAduana="..."
        ValorDolares="..."/>
    </cce20:Mercancias>
  </cce20:ComercioExterior>
</cfdi:Complemento>
```

### Requisitos previos
- RFC en el padrón de exportadores SAT
- Fracción arancelaria correcta (clasificación TIGIE)
- Tipo de pedimento del catálogo

---

## InsEduc (Instituciones Educativas)

### Cuándo usar
CFDI con UsoCFDI = D10 (colegiaturas deducibles).

### Estructura

```xml
<cfdi:Complemento>
  <iedu:instEducativas
    Version="1.0"
    nombreAlumno="Diego Pérez Rodríguez"
    CURP="PERD150301HDFRZG02"
    nivelEducativo="Primaria"
    autoRVOE="20060123"
    rfcPago="PERA800101ABC"/>
</cfdi:Complemento>
```

### Niveles educativos válidos
- "Preescolar"
- "Primaria"
- "Secundaria"
- "Profesional técnico"
- "Bachillerato o su equivalente"

### Reglas clave
- **rfcPago** debe coincidir con RFC del receptor del CFDI (padre que paga)
- **autoRVOE** es el número de RVOE del colegio (no del nivel)
- **CURP** del alumno (no del padre)
- **nombreAlumno** debe coincidir EXACTAMENTE con acta de nacimiento

---

## Donatarias

### Cuándo usar
Cuando emites recibo de donativo y eres una donataria autorizada SAT.

### Estructura

```xml
<cfdi:Complemento>
  <donat:Donatarias
    Version="1.1"
    noAutorizacion="..."
    fechaAutorizacion="..."
    leyenda="Este comprobante ampara un donativo, el cual será destinado por la donataria a los fines propios de su objeto social."/>
</cfdi:Complemento>
```

### Requisitos
- Estar autorizada en el listado SAT de donatarias autorizadas
- Tener publicación vigente
- Receptor puede deducir hasta 7% de ingresos del año anterior (Art. 27 LISR)

---

## Vehículo Usado

### Cuándo usar
Compraventa de vehículo usado entre particulares (con intermediación de PM).

Información del vehículo: marca, modelo, año, VIN, placas, número de motor, etc.

---

## Estado de Cuenta de Combustible

### Cuándo usar
Comprobantes de monedero electrónico de combustible (PEMEX, Shell, etc.).

Estructura específica con detalle de cada carga.

---

## Aerolíneas

### Cuándo usar
Boleto aéreo con cargos por servicios adicionales (equipaje, asientos premium, etc.) que se facturan separadamente del boleto base.

---

## ⚠ Verificación vigente

Todos los complementos tienen XSDs publicados por el SAT que se actualizan periódicamente. Validar:
- Versión actual vigente
- Estructura XML completa
- Validación contra XSD oficial

Tu PAC mantiene los XSDs actualizados y valida automáticamente. Si tu XML no cumple, el PAC lo rechaza con código específico.

---

## Cómo agregar un complemento al CFDI

```xml
<cfdi:Comprobante 
    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:pago20="http://www.sat.gob.mx/Pagos20"
    xmlns:iedu="http://www.sat.gob.mx/iedu"
    xsi:schemaLocation="
      http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd
      http://www.sat.gob.mx/Pagos20 http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos20.xsd
      http://www.sat.gob.mx/iedu http://www.sat.gob.mx/sitio_internet/cfd/iedu/iedu.xsd
    "
    ...>
  
  <!-- Conceptos, impuestos, etc. -->
  
  <cfdi:Complemento>
    <!-- aquí van los complementos -->
  </cfdi:Complemento>
</cfdi:Comprobante>
```

---

## Ver también

- `catalogos-sat.md` — catálogos generales
- `casos-edge-cfdi.md` — patrones de uso
- [glosario-fiscal-mx.md](../../../docs/glosario-fiscal-mx.md) — términos
