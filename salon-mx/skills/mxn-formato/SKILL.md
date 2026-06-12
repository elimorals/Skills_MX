---
name: mxn-formato
description: Formatea y normaliza valores monetarios en pesos mexicanos (MXN) según convenciones mexicanas. Cubre formato con separador de miles y decimales correctos ($1,234,567.89), conversión a letra para contratos y CFDI (un millón doscientos treinta y cuatro mil quinientos sesenta y siete pesos 89/100 M.N.), distinción entre "$" y "MXN $" cuando hay riesgo de confusión con USD, normalización de inputs sucios ($1,234.56, 1234.56, 1.234,56 europeo, 1234, "mil doscientos") a formato canónico, y conversión a otras monedas (USD, EUR, CAD) usando tipo de cambio DOF. Usar cuando el usuario diga formatear pesos, formato moneda, monto a letra, importe en letra, convert to MXN, normalize amount, o esté generando contratos, cotizaciones, facturas, recibos donde el monto debe verse profesional. NO usar para criptomonedas (otra cosa) ni para unidades no monetarias (kg, cm, etc.).
allowed-tools: Read, Bash
---

# Formato de moneda MXN

Skill utilitario pero crítico: un monto mal formateado en una cotización proyecta amateurismo y abre disputas legales.

## Formato canónico MXN

```
Símbolo:      $
Separador:    , (coma) para miles
Decimal:      . (punto) para fracción
Decimales:    siempre 2 (centavos)
Sufijo:       MXN (cuando se necesita distinguir de USD/CAD)
```

Ejemplos canónicos:
- `$1,234.56`
- `$1,234,567.89 MXN`
- `$0.50`
- `$1,000,000.00 MXN`

## Cuándo agregar "MXN" después del monto

**Sí agregar**:
- Cualquier documento bilingüe o que mencione otras monedas
- Cotizaciones a clientes extranjeros
- Contratos formales
- Facturas para empresas con operaciones internacionales

**No es necesario**:
- Documentos 100% mexicanos dirigidos a clientes 100% mexicanos
- Tickets de venta de mostrador
- Mensajes informales WhatsApp

Cuando dudes, agrega "MXN". Es defensivo.

## Distinción visual con USD

México y EE.UU. comparten el símbolo `$`, lo que crea ambigüedad real en facturación bilingüe. Convenciones:
- `$1,234.56 MXN` — pesos mexicanos
- `$1,234.56 USD` — dólares americanos
- `USD $1,234.56` — alternativa común en contratos
- `MX$1,234.56` o `MXN$1,234.56` — válido en notación financiera

Nunca asumir. Si el documento es bilingüe, explicitar siempre.

## Conversión a letra (formato CFDI y contratos)

El SAT acepta varios formatos; el más común para CFDI es:
```
($1,234.56 MXN) UN MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 M.N.
```

Componentes:
- Mayúsculas (convención CFDI)
- Cantidad en letras (cardinales)
- "PESOS" o "PESOS M.N." (Moneda Nacional)
- Centavos en formato fraccional `XX/100`
- Sufijo `M.N.` reforzando moneda nacional

Casos especiales:
- Cero pesos: `CERO PESOS 00/100 M.N.`
- Solo centavos: `CERO PESOS 50/100 M.N.`
- Miles, millones: respetando reglas RAE de números (catorce mil, no diecicuatromil; cien mil sin "uno"; mil sin "uno": "mil pesos" no "un mil pesos" salvo en contexto contable formal).

## Normalización de inputs sucios

Este skill acepta entradas en cualquier formato común y las normaliza:

| Input | Normalizado a |
|---|---|
| `1234.56` | `$1,234.56` |
| `1,234.56` | `$1,234.56` |
| `$1,234.56` | `$1,234.56` |
| `1.234,56` (europeo) | `$1,234.56` (advertir cambio) |
| `$1,234` | `$1,234.00` |
| `mil doscientos pesos` | `$1,200.00` |
| `1.5k` | `$1,500.00` |
| `2 millones` | `$2,000,000.00` |
| `$1234.567` | `$1,234.57` (redondeo) y advertencia |

**Importante**: cuando hay ambigüedad (ej. `1.234` ¿es mil doscientos treinta y cuatro o uno punto dos tres cuatro?), el skill debe **preguntar antes de asumir**.

## Redondeo

Reglas para CFDI:
- Redondeo a 2 decimales con regla matemática estándar (>= 5 sube).
- En sumatorias, redondear cada subtotal antes de sumar puede generar diferencias de centavos vs sumar primero y redondear al final.
- Convención SAT: redondear cada concepto y sumar. Diferencias deben absorberse o ajustarse con un concepto de "redondeo" con valor mínimo si es necesario.

Reglas para contratos:
- Si el contrato es a precio fijo: redondear a 2 decimales, sin ajustes posteriores.
- Si involucra cálculos (porcentajes, prorrateo): especificar regla de redondeo en cláusula.

## Conversión a otras monedas

Para conversión MXN ↔ USD/EUR/GBP/CAD/JPY:
1. Tipo de cambio del **Diario Oficial de la Federación (DOF)** publicado por Banxico.
2. SAT requiere usar el TC del día hábil **anterior** al acto que se factura (no el del día mismo).

### MCP disponible: `banxico`

El MCP `banxico` (en `mcp-servers/mp_banxico/`) provee tools directos:

- `banxico_get_tc_dof(moneda, fecha)` — TC para fecha específica (ajusta a día hábil anterior si la fecha cae en fin de semana o feriado mexicano)
- `banxico_get_tc_dia_habil_anterior(moneda, fecha_referencia)` — la regla SAT para CFDI: TC del día hábil estrictamente anterior a la fecha del comprobante
- `banxico_convertir_monto(monto, de_moneda, a_moneda, fecha)` — conversión completa con precisión decimal

Si `BANXICO_TOKEN` no está configurado, los tools regresan valores plausibles marcados con `simulated: true`. Para producción, registrar token gratuito en https://www.banxico.org.mx/SieAPIRest/service/v1/token.

El MCP maneja automáticamente:
- Feriados bancarios mexicanos (incluyendo Semana Santa calculada vía algoritmo de Gauss)
- Cache de 24h para TC (los publicados ya no cambian)
- Bitácora de cada consulta en `~/.local/share/plugins-mx/audit-log/banxico_mcp/`

## Salida esperada

```json
{
  "monto_input": "1234.56",
  "monto_normalizado": 1234.56,
  "formato_corto": "$1,234.56",
  "formato_largo": "$1,234.56 MXN",
  "letra": "UN MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 M.N.",
  "alertas": []
}
```

## Casos edge

- **Decimales no estándar (3+ decimales)**: redondear con advertencia. Tipos de cambio sí usan más decimales y deben preservarse en el campo `TipoCambio` del CFDI.
- **Montos negativos**: para notas de crédito, mostrar con signo `−` o entre paréntesis según convención del documento.
- **Cero**: `$0.00 MXN` no `$0` ni `Gratuito` (en documentos legales).

## Integración

- `cotizacion-mxn`, `cfdi-emision`, `contrato-mercantil-mx` consumen este skill para todos los importes que aparecen en sus outputs.
- Cualquier documento generado debe pasar por este skill para uniformidad.
