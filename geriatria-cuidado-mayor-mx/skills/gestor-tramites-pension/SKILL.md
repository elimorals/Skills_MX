---
name: gestor-tramites-pension
description: Gestiona trámites de pensión y prestaciones del adulto mayor en México: pensión IMSS Ley 73 vs Ley 97 según fecha de cotización (Ley 73 más generosa, requiere mínimo 500 semanas cotizadas), pensión ISSSTE para servidores públicos, pensión bienestar federal (programa adultos mayores 65+ no contributiva $6,000 MXN bimestrales), tracking de cobro mensual o bimestral con alerta si no llega depósito, renovación periódica de constancias requeridas, sobrevivencia del pensionado para evitar suspensión por inactividad bancaria, cambio de domicilio en padrón pensionado, modificación de beneficiarios para la pensión de viudez al fallecer el titular, y conversión de pensión retroactiva (caso típico: persona se pensionó tarde y le deben varios meses). Cubre AFORE para retiro de fondos al cumplir 65 o por desempleo previo. Usar cuando el usuario diga "pensión IMSS abuelita", "tramite pensión bienestar", "AFORE retiro", "viudez pensión", "renovar pensionado", "no llegó pago pensión". NO usar para cálculo de pensión de empresa privada (puede ser plan paralelo) ni para seguro de gastos médicos del jubilado.
allowed-tools: Read, Write, Edit
---

# Trámites de pensión del adulto mayor

## Tipos de pensión

### IMSS Ley 73 (más generosa)

- Aplica si cotizó antes del 1-julio-1997
- Requiere mínimo **500 semanas cotizadas** (10 años aprox)
- Beneficio: % del salario promedio últimos 5 años (escalado por edad)
- Modalidades: vejez (65+), cesantía (60-64), invalidez

### IMSS Ley 97

- Aplica si cotizó desde 1-julio-1997
- Requiere **1,250 semanas cotizadas** (~24 años)
- Beneficio: AFORE acumulado + cuenta individual
- Generalmente menor pensión que Ley 73

### ISSSTE

- Servidores públicos federales
- Sistema similar Ley 73/Ley 97 ISSSTE-Décimo

### Pensión Bienestar Federal

- No contributiva — todos los mexicanos 65+
- $6,000 MXN bimestrales (2026, validar vigencia)
- Trámite en módulos del programa

## Tracking mensual de cobro

```yaml
pensionado_id: ABC123
modalidad: IMSS_LEY_73_VEJEZ
ultimo_pago_recibido: 2026-06-01
monto: 12500.00
banco_pagador: BBVA
clabe_destino: ...
proximo_pago_esperado: 2026-07-01
estado: vigente
alertas:
  - vigencia_certificado_supervivencia: 2026-12-31
```

## Trámites comunes

| Trámite | Frecuencia | Documentación |
|---|---|---|
| Sobrevivencia | Anual / bianual | INE + acta nacimiento |
| Cambio domicilio | Una vez | Comprobante domicilio |
| Modificación beneficiarios | Una vez (vida) | INE beneficiarios + parentesco |
| Renovación CLABE | Si cambia cuenta | Estado cuenta nuevo |
| Pensión viudez (al fallecer) | Una vez | Acta defunción + matrimonio |
| Retroactivos pensión | Una vez | Constancias trabajo + cálculo |

## Alertas críticas

- 30 días antes vencimiento constancia supervivencia → recordar trámite
- 5 días sin recibir pago → contactar IMSS/ISSSTE/Bienestar
- Cambio de banco → 30 días antes activar nueva CLABE
- Fallecimiento titular → inmediato trámite viudez (no perder meses)

## Validación pendiente

⚠ Montos bienestar federal pueden cambiar. Validar contra portal oficial vigente.
⚠ Reglas Ley 73 vs Ley 97 son complejas — consultar con asesor IMSS.
