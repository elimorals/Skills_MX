---
name: dispersion-cuadrilla
description: Dispersa la raya semanal de una cuadrilla de obra civil con CFDI de nómina 4.0 (complemento Nómina 1.2) por trabajador: salario diario integrado (factor de integración por aguinaldo y prima vacacional), retención ISR con la tarifa semanal del Anexo 8 RMF 2026 y subsidio para el empleo, cuotas obreras IMSS (enfermedad y maternidad, invalidez y vida, cesantía y vejez), descuento INFONAVIT si hay aviso de retención, ISN estatal a cargo del patrón, y pago por SPEI a la CLABE del trabajador con bitácora. Considera el pago semanal obligatorio para trabajo material (Art. 88 LFT), el registro de obra en IMSS (SATIC) y altas/bajas frecuentes. Separa trabajadores propios de subcontratistas REPSE (no son nómina). Usar cuando el usuario diga "raya semanal", "pago cuadrilla", "nómina obra", "dispersión SPEI construcción", "CFDI nómina constructora". NO usar para pago a subcontratistas REPSE (usar retenciones-repse) ni para nómina de oficina.
allowed-tools: Read, Write, Edit
---

# Dispersión semanal de raya a cuadrilla

## Flujo semanal

1. **Asistencia** por trabajador (días laborados).
2. **SDI** = salario diario × factor de integración. Factor mínimo LFT 2026 (15 días de aguinaldo, 12 días de vacaciones el primer año con prima de 25%): 1 + (15 + 12 × 0.25) / 365 = **1.0493**. Agrega bonos habituales si los hay. Tope: 25 UMA diarias ($2,932.75 con UMA 2026 de $117.31); mínimo: salario mínimo ($315.04 general / $440.87 ZLFN). Tool: `imss_sbc_calcular` (MCP `mp_imss_patronal`, sin verificar).
3. **Cuotas obreras IMSS** (las retiene el patrón):
   - Enfermedad y maternidad: 0.40% sobre el excedente de 3 UMA; prestaciones en dinero 0.25%; gastos médicos de pensionados 0.375%
   - Invalidez y vida: 0.625%
   - Cesantía y vejez: 1.125%
   - Riesgos de trabajo: **solo patronal**, según la prima de la empresa (construcción suele ser clase V)
4. **ISR**: tarifa semanal del Anexo 8 RMF 2026 (no dividir la mensual entre 4.33) y subsidio para el empleo vigente (decreto; verificar monto 2026).
5. **INFONAVIT**: descuento solo si el Instituto envió aviso de retención (`infonavit_descuento_calcular`, MCP `mp_infonavit_patronal`, sin verificar).
6. **ISN estatal** (patronal, no se descuenta al trabajador): `isn_calcular` (MCP `mp_isn_mx`; tasas 2026 en `mcp-servers/shared/catalogo_isn_estatal.py`, p. ej. CDMX 4%).
7. **CFDI de nómina** por trabajador.
8. **SPEI** a la CLABE de cada trabajador.
9. **Bitácora** con comprobante por persona.

## Configuración CFDI Nómina

| Campo | Valor obra |
|---|---|
| TipoNomina | O (ordinaria) |
| PeriodicidadPago | 02 (semanal) |
| TipoContrato | 02 (por obra determinada) o 03 (tiempo determinado) según el contrato |
| RiesgoPuesto | 5 (clase V) si esa es la clase de la empresa |
| OrigenRecurso | Solo aplica a entidades públicas; no se llena en constructora privada |

## Validaciones

1. Alta IMSS previa al inicio de labores (IDSE) y obra registrada en SATIC (Reglamento del Seguro Social Obligatorio para los Trabajadores de la Construcción por Obra o Tiempo Determinado).
2. CLABE válida: `clabe_validador_validar_clabe` (MCP `mp_clabe_validador_oficial`, validado en vivo).
3. SBC entre el salario mínimo y 25 UMA.
4. Salario semanal ≥ 7 × salario mínimo diario de la zona.

## Output

```
nominas/<rfc-hash>/<año>-<semana>/
  ├── lista-raya.json
  ├── dispersion-spei-lote.csv
  ├── cfdis-nomina-timbrados/
  └── bitacora-dispersion.md
```

## ⚠ Compliance

Cuotas y tarifas cambian por reforma o decreto: valida la nómina con el contador o el sistema de nómina antes de timbrar.
