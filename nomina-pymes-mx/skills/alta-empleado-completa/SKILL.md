---
name: alta-empleado-completa
description: Alta completa de empleado nuevo - captura RFC, CURP y NSS, valida RFC contra el padrón SAT y la CLABE de pago, calcula el SBC con el factor de integración mínimo 2026 (1.0493 el primer año, con 12 días de vacaciones de la reforma 2023), aplica topes (salario mínimo y 25 UMA), registra en el tracker local, prepara el aviso de alta IMSS por IDSE dentro de 5 días hábiles (Art. 15 LSS) y la primera CFDI de nómina. Usar cuando el usuario diga alta empleado, contratar nuevo, registrar trabajador, alta IMSS, alta en el seguro, inscribir trabajador.
allowed-tools: Read, Write
---

# Alta empleado completa

## Schema empleado

```python
class Empleado(BaseModel):
    rfc: str
    curp: str
    nss: str  # 11 dígitos
    nombre_completo: str
    fecha_alta: date
    puesto: str
    departamento: str | None
    tipo_regimen: Literal["02_sueldos", "09_asimilados_honorarios", "13_indemnizacion_separacion"]  # c_TipoRegimen
    tipo_contrato: Literal["01_indefinido", "02_obra_determinada", "03_tiempo_determinado"]  # c_TipoContrato
    tipo_jornada: str  # c_TipoJornada
    salario_diario_mxn: Decimal
    factor_integracion: Decimal  # ver abajo
    sbc_diario: Decimal
    periodicidad_pago: Literal["02_semanal", "04_quincenal", "05_mensual"]  # c_PeriodicidadPago
    cuenta_clabe_pago: str
    credito_infonavit: bool  # se confirma con el aviso de retención
    pension_alimenticia: Decimal | None  # orden judicial
```

## Validaciones

1. **RFC en padrón SAT**: `sat_consultar_padron` (MCP `mp_sat_portal`; el login con e.firma está sin validar en vivo, si falla pide al trabajador su Constancia de Situación Fiscal). El CP y nombre del CFDI deben coincidir con la CSF.
2. **NSS**: 11 dígitos con dígito verificador; si no tiene, el trabajador lo obtiene en el portal del IMSS.
3. **CURP** coherente con RFC y fecha de nacimiento (`curp_validar_estructura`, `mp_curp_renapo`, validación local).
4. **SBC ≥ salario mínimo** vigente: $315.04 general / $440.87 ZLFN (2026).
5. **SBC ≤ 25 UMA** = $2,932.75 (Art. 28 LSS).
6. **CLABE válida**: `clabe_validador_validar_clabe` (MCP `mp_clabe_validador_oficial`, validado en vivo).
7. **Crédito INFONAVIT**: pregúntalo al trabajador y confírmalo con el aviso de retención o `infonavit_consultar_creditos_trabajadores` (`mp_infonavit_patronal`, estado "sin verificar").

## Cálculo SBC

Factor mínimo = 1 + 15/365 (aguinaldo) + días de vacaciones × 25% / 365.

| Año de servicio | Vacaciones | Factor mínimo |
|---|---|---|
| 1 | 12 | 1.0493 |
| 2 | 14 | 1.0507 |
| 3 | 16 | 1.0521 |

El factor sube con cada aniversario: presenta modificación de salario en IDSE dentro de 5 días hábiles. Si das más prestaciones (aguinaldo > 15 días, prima > 25%, prestaciones fijas), recalcúlalo (Art. 27 LSS).

```python
def sbc(salario_diario: D, dias_vac: int = 12, dias_aguinaldo: int = 15, prima_vac: D = D("0.25")) -> D:
    factor = 1 + D(dias_aguinaldo) / 365 + D(dias_vac) * prima_vac / 365
    return (salario_diario * factor).quantize(D("0.01"))
```

Ejemplo: $600 × 1.0493 = **$629.58**.

## Output

```json
{
  "empleado_id": "EMP-001",
  "rfc_hash": "...",
  "alta_exitosa": true,
  "fecha_alta": "2026-06-12",
  "salario_diario_mxn": "600.00",
  "factor_integracion": "1.0493",
  "sbc_diario_mxn": "629.58",
  "validaciones": {
    "rfc_padron_sat": "activo",
    "nss_valido": true,
    "clabe_valida": true,
    "infonavit_credito_activo": false
  },
  "aviso_idse_pendiente_envio": true,
  "deadline_idse_5_dias_habiles": "2026-06-19",
  "cfdi_primera_quincena_pendiente": true,
  "advertencias": []
}
```

## ⚠ Compliance

- Aviso de alta: a más tardar 5 días hábiles (Art. 15 fr. I LSS). Lo prudente es darlo **antes** de que empiece a trabajar.
- Si ocurre un accidente antes del aviso, el IMSS atiende al trabajador pero cobra al patrón el **capital constitutivo** (Arts. 77-79 LSS), además de la multa.
- Jornada: hoy la máxima sigue siendo 48 h semanales; la reforma constitucional (DOF 03-03-2026) y a la LFT (DOF 01-05-2026, confianza media) la reducen gradualmente a partir de 2027 (46 h) hasta 40 h en 2030. Contratos nuevos: prevé el ajuste.
- Valida con tu contador antes de presentar.
