---
name: contrato-arrendamiento-residencial
description: Genera contrato de arrendamiento residencial conforme al Código Civil para la CDMX (Art. 2398-2496) con adaptaciones por estado donde se requieran. Cubre cláusulas estándar (objeto, vigencia, renta + actualización, depósito de garantía, fiador, uso casa-habitación, mantenimiento, terminación anticipada, jurisdicción) más adendums comunes (mascotas, modificaciones, sub-arrendamiento prohibido). Genera PDF firmable. Usar cuando el usuario diga generar contrato arrendamiento, contrato renta, contrato inquilino. NO usar para arrendamiento comercial (local, oficina — vertical aparte) ni para predios rústicos.
allowed-tools: Read, Write
---

# Contrato arrendamiento residencial — generación

## Trigger

- "generar contrato para X inquilino"
- "redacta contrato arrendamiento"
- "contrato residencial"

## Pre-requisitos

- Screening del inquilino aprobado (output de `screening-inquilino-completo`)
- Propiedad registrada en tracker
- Aviso de privacidad entregado al inquilino (Arts. 15-16 LFPDPPP 2025)

## Inputs

```json
{
  "propiedad": {
    "direccion_completa": "...",
    "cp": "06700",
    "municipio": "Cuauhtémoc",
    "estado": "CDMX",
    "metros": 80,
    "habitaciones": 2,
    "banos": 1,
    "estacionamientos": 1,
    "amueblado": false
  },
  "arrendador": {
    "rfc": "...",
    "nombre_completo": "...",
    "direccion": "...",
    "regimen_fiscal": "606"  // o "626 RESICO PF"
  },
  "inquilino": {
    "rfc": "...",
    "nombre_completo": "...",
    "curp": "...",
    "tel": "+5215..."
  },
  "fiador": {  // opcional
    "rfc": "...",
    "nombre_completo": "...",
    "tipo": "propietario_solidario"  // o "aval personal"
  },
  "renta": {
    "monto_mensual_mxn": "12000",
    "moneda": "MXN",
    "actualizacion": "INPC_anual",  // o "5_pct_fijo"
    "dia_cobro_mes": 5
  },
  "vigencia": {
    "inicio": "2026-08-01",
    "fin": "2027-07-31",
    "renovacion_automatica": false
  },
  "deposito_garantia": {
    "monto_mxn": "12000",
    "concepto": "garantia_pago_y_danos"
  },
  "permite_mascotas": true,
  "permite_sub_arrendamiento": false,
  "uso_exclusivo": "casa_habitacion"
}
```

## Cláusulas estándar (CDMX)

### 1. Objeto
Inmueble situado en [dirección]. Uso exclusivo casa habitación (Art. 2398 CCDF).

### 2. Vigencia
[fecha_inicio] al [fecha_fin]. En CDMX la duración mínima para vivienda es de 1 año, forzoso para el arrendador y voluntario para el arrendatario (Art. 2448-C CCDF). Si no se prorroga ni desocupa al vencimiento, se entiende prorrogado por **tácita reconducción** mes a mes (Art. 2487 CCDF) hasta que cualquier parte avise con 30 días.

### 3. Renta mensual
- Monto: $X MXN
- Día de cobro: día Y del mes
- Forma de pago: transferencia SPEI a la CLABE [...]
- Si efectivo: en domicilio del arrendador antes del día Y
- Interés moratorio pactado (moderado: un juez puede reducir intereses usurarios)
- **CFDI**: el arrendador emite CFDI tipo I (uso S01 si el inquilino es PF que vive ahí; G03 si es PM) — ver `cfdi-arrendamiento-mensual`

### 4. Actualización anual de renta
- Mecanismo: INPC anual del INEGI (variación últimos 12 meses)
- Fecha: aniversario del contrato
- Comunicación: 30 días previos al inquilino
- CDMX: el incremento anual no puede exceder la inflación del año anterior (Art. 2448-D CCDF, reforma Gaceta 28-08-2024; SCJN la validó en feb-2026, AR 546/2025)

### 5. Depósito en garantía
- Monto equivalente a 1 mes (estándar) o más si screening lo justifica
- Devuelto al cierre del contrato si:
  - No hay daños fuera del uso normal
  - Servicios al corriente
  - Llaves devueltas
- Plazo de devolución: 30 días post-entrega

### 6. Mantenimiento
- Arrendador: conservar el inmueble en estado de servir, reparaciones necesarias (Art. 2412 fr. II CCDF)
- Inquilino: cuidado ordinario y reparaciones menores por uso (Art. 2425 CCDF); fijar en el contrato un monto tope para "reparaciones menores"
- Servicios (luz, agua, gas, internet): a cargo del inquilino

### 7. Uso exclusivo casa-habitación
- Prohibido sub-arrendar sin consentimiento por escrito del arrendador (Art. 2480 CCDF)
- Prohibido uso comercial / oficina
- Permitido home office personal (no atención al público)

### 8. Terminación anticipada
- Cualquier parte puede dar por terminado con aviso de 60 días + pago de penalización
- Penalización pactada (p. ej. 1 mes de renta) + rentas e intereses pendientes. En CDMX el plazo forzoso de 1 año obliga al arrendador, no al inquilino (Art. 2448-C)

### 9. Causas de rescisión (Art. 2489 CCDF)
- Falta de pago de la renta (pactar cuántas mensualidades; p. ej. 2 consecutivas)
- Daño doloso al inmueble
- Uso distinto al pactado
- Sub-arrendamiento sin consentimiento

### 10. Jurisdicción
Tribunales de [CDMX] (o estado donde se ubique). El inquilino renuncia a fuero por domicilio futuro.

## Adendums opcionales

### A. Mascotas
- Tipo y número permitidos
- Responsabilidad por daños
- Limpieza de áreas comunes

### B. Modificaciones al inmueble
- Pintura: permitida (color similar al original)
- Mejoras estructurales: requieren autorización por escrito
- Las mejoras quedan en beneficio del inmueble (Art. 2426 CCDF)

### C. Inventario inicial (foto+descripción)
- Tabla con muebles, electrodomésticos, estado
- Firmado por ambas partes al inicio
- Base para evaluar al cierre

## Output

PDF generado en:
`~/.local/share/plugins-mx/arrendador/<rfc_hash>/contratos/<propiedad_id>-<inquilino_id_hash>-<fecha>.pdf`

Estructura:
1. Carátula con identificación de partes
2. Cláusulas 1-10
3. Adendums activos
4. Página de firmas (arrendador + inquilino + fiador + 2 testigos)
5. Anexo: aviso de privacidad

## Casos edge

| Caso | Acción |
|---|---|
| Estado distinto a CDMX | Adaptar cláusulas a CCF (Federal) + código estatal — sugerir abogado local |
| Inquilino extranjero | Agregar cláusula de domicilio en territorio nacional |
| Renta en USD | Cláusula de conversión por TC Banxico fecha de pago |
| Renta con vacancia previa (descuento primer mes) | Adendum específico |
| Sub-rent con consentimiento explícito | Adendum con responsabilidades |
| Inquilino persona moral (empresa renta para ejecutivo) | Cláusulas adicionales — datos representante legal |

## Dependencias

- `mp_facturama_extendido` (CFDI mensual, ver `cfdi-arrendamiento-mensual`)
- Output de `screening-inquilino-completo`
- Tracker de propiedades

## ⚠ Compliance legal

- **Cláusulas revisadas al 2026-10-15** contra la reforma CDMX de 2024 (Arts. 2448-C, 2448-D). El registro obligatorio de contratos (Art. 2448-F) está pendiente de resolución en la SCJN: **verificar** su estado antes de firmar.
- Para estados diferentes a CDMX: **consultar abogado local**
- LFPDPPP: aviso de privacidad obligatorio + firmado por inquilino
- En caso de litigio, el contrato firmado es la prueba documental principal; firma ante testigos o ratificación ante notario la refuerza
- `vigencia_validada: false` — abogado certifica antes de imprimir
