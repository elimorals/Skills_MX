---
name: dispersion-cuadrilla
description: Dispersa pagos semanales (raya) a cuadrilla de obra civil con CFDI Nómina 4.0 (TipoNomina O ordinaria) por cada trabajador, calculando salario diario integrado SDI con base en sueldo base + prima vacacional + aguinaldo + bonos habituales, retención ISR según tarifa Art. 96 LISR mensualizada a la semana, cuotas IMSS obrero retenidas (enfermedad-maternidad, invalidez-vida, cesantía-vejez, riesgos de trabajo categoría construcción típicamente clase IV o V), descuento INFONAVIT cuando aplica con cédula EMIS, y dispersión vía SPEI por CLABE personal del trabajador con bitácora de comprobante por persona. Crítico cumplir con Art. 17 LFT (pago semanal mínimo en construcción) y registro IMSS de altas/bajas dinámico (frecuente en obra). Diferencia entre trabajador con vínculo laboral directo y subcontratista REPSE (este último no es nómina). Usar cuando el usuario diga "raya semanal", "pago cuadrilla", "nómina obra", "dispersión SPEI construcción", "CFDI nómina constructora". NO usar para pago a subcontratistas REPSE (usar retenciones-repse) ni para nómina de oficina.
allowed-tools: Read, Write, Edit
---

# Dispersión semanal de raya a cuadrilla

## Flujo semanal

1. **Captura asistencia** por trabajador (días laborados)
2. **Cálculo SDI** = (salario diario + prestaciones) / 365
3. **Cuotas IMSS obrero** (depende del salario y categoría de riesgo):
   - Enfermedad-maternidad: 0.25% del SBC
   - Invalidez-vida: 0.625%
   - Cesantía-vejez: 1.125%
4. **Retención ISR**: tarifa Art. 96 / 4.33 (semanal)
5. **Descuento INFONAVIT** si trabajador tiene crédito (consultar EMIS)
6. **Generar CFDI Nómina 4.0** por trabajador
7. **Dispersar SPEI** a CLABE personal
8. **Bitácora** con comprobante por persona

## Configuración CFDI Nómina

| Campo | Valor obra |
|---|---|
| TipoNomina | O (ordinaria) |
| Periodicidad | 02 (semanal) |
| TipoContrato | 01 (subordinación común) o 99 (otros) |
| RiesgoPuesto | Categoría IV o V típica construcción |
| OrigenRecurso | IP (recursos propios) |

## Validaciones

1. Cada trabajador con alta IMSS activa (si no: alta inmediata vía IDSE)
2. CLABE válida (validar con `mp_clabe_validador_oficial`)
3. SDI dentro de límite mínimo y máximo según UMA
4. Si trabajador NUEVO esta semana: alta previa al pago

## Output

```
nominas/<rfc-hash>/<año>-<semana>/
  ├── lista-raya.json
  ├── dispersión-spei-lote.csv
  ├── cfdis-nomina-timbrados/
  └── bitácora-dispersión.md
```
