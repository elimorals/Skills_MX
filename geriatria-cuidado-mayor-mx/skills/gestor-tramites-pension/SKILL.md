---
name: gestor-tramites-pension
description: Gestiona trámites de pensión y prestaciones del adulto mayor en México: pensión IMSS Ley 73 (cotizó antes del 1-jul-1997, 500 semanas) vs Ley 97 (875 semanas en 2026, sube 25 por año), pensión ISSSTE (décimo transitorio vs cuentas individuales), Pensión para el Bienestar de las Personas Adultas Mayores (65+, no contributiva, $6,400 bimestrales en 2026), retiro de AFORE, seguimiento de depósitos con alerta si no llega, comprobación de supervivencia, cambio de domicilio o cuenta, beneficiarios y pensión de viudez, y cobro de retroactivos. Usar cuando el usuario diga "pensión IMSS abuelita", "trámite pensión bienestar", "pensión 65 y más", "AFORE retiro", "viudez pensión", "no llegó pago pensión", "semanas cotizadas". NO usar para planes privados de pensión de empresa ni para seguro de gastos médicos del jubilado.
allowed-tools: Read, Write, Edit
---

# Trámites de pensión del adulto mayor

## Tipos de pensión

### IMSS Ley 73 (más generosa)

- Aplica si empezó a cotizar antes del 1-julio-1997 (puede elegir Ley 73 o Ley 97 al pensionarse)
- Requiere mínimo **500 semanas cotizadas** (≈ 9.6 años)
- Beneficio: % del salario promedio de las últimas 250 semanas; cesantía a los 60 = 75%, sube 5% por año hasta 100% a los 65
- Modalidades: vejez (65+), cesantía en edad avanzada (60-64), invalidez
- Requiere estar dado de baja del régimen obligatorio (o conservar derechos)

### IMSS Ley 97

- Obligatoria si empezó a cotizar a partir del 1-julio-1997
- Semanas mínimas (reforma LSS DOF 16-12-2020): **875 en 2026**, 900 en 2027, +25 por año hasta 1,000 en 2031 (fuente: decreto y prensa 2026; confianza media-alta)
- Edad: cesantía 60, vejez 65
- Beneficio: saldo de la cuenta individual AFORE (renta vitalicia o retiros programados), con pensión garantizada si el saldo no alcanza
- Fondo de Pensiones para el Bienestar (2024) complementa a ciertos pensionados Ley 97 de salario bajo; verificar elegibilidad con IMSS
- Sin semanas suficientes: negativa de pensión y retiro del saldo en una exhibición

### ISSSTE

- Servidores públicos federales
- Dos regímenes desde la Ley del ISSSTE 2007: **décimo transitorio** (pensión de reparto con requisitos de edad y años de servicio que suben por año) y **cuentas individuales** (PENSIONISSSTE/AFORE). Verificar requisitos del año con el ISSSTE

### Pensión Bienestar Federal

- No contributiva: personas mexicanas de 65+ residentes en el país
- **$6,400 MXN bimestrales en 2026** (2025: $6,200). Fuente: declaraciones de la Secretaría de Bienestar citadas en prensa (enero 2026); confianza media, confirmar en gob.mx/bienestar
- Mujeres de 60-64: programa aparte "Pensión Mujeres Bienestar" ($3,100 bimestrales 2026, misma fuente)
- Registro en Módulos del Bienestar con INE, CURP, acta de nacimiento y comprobante de domicilio; se paga en Tarjeta del Bienestar

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
| Comprobación de supervivencia | Según institución/banco (verificar: IMSS, ISSSTE y bancos tienen reglas distintas; obligatoria si vive en el extranjero) | INE + CURP |
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

⚠ Monto Bienestar 2026 tomado de fuente secundaria: validar en gob.mx/bienestar.
⚠ La skill no consulta IMSS/ISSSTE/AFORE: trabaja con los documentos que da el usuario. Semanas cotizadas: constancia en IMSS Digital.
⚠ Reglas Ley 73 vs Ley 97 son complejas — consultar con asesor IMSS.
