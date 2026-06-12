---
name: alta-empleado-completa
description: Alta completa de empleado nuevo: captura RFC + CURP + NSS, valida datos contra padrón SAT y registro IMSS (vía mp_imss_patronal), calcula SBC con factor de integración 1.0452, registra en tracker local, genera aviso IDSE para enviar al IMSS dentro de 5 días hábiles (Art. 15 LSS), prepara primera CFDI Nómina. Usar cuando el usuario diga alta empleado, contratar nuevo, registrar trabajador, alta IMSS empleado.
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
    regimen_contratacion: Literal["02_sueldos", "08_indemnizacion"]
    tipo_contrato: Literal["01_indefinido", "02_obra_determinada", "03_tiempo_determinado"]
    sueldo_diario_mxn: Decimal
    factor_integracion: Decimal = Decimal("1.0452")
    sbc_diario: Decimal  # = sueldo_diario × factor_integracion
    periodicidad_pago: Literal["02_quincenal", "04_mensual"]
    cuenta_clabe_pago: str
    aplica_credito_infonavit: bool
    monto_credito_infonavit_mxn: Decimal | None
    aplica_alimentaria: bool
    monto_alimentaria_mxn: Decimal | None
```

## Validaciones

1. **RFC vs padrón SAT** (`mp_sat_portal.consultar_padron`)
2. **NSS válido** (11 dígitos, no inventado)
3. **CURP coherente** con RFC y fecha nacimiento
4. **SBC ≥ mínimo** (UMA × N días)
5. **SBC ≤ 25 UMAs** (tope superior IMSS)
6. **Cuenta CLABE válida** (`mp_clabe_validador_oficial`)
7. **Si tiene crédito INFONAVIT**: validar % descuento (`mp_infonavit_patronal`)

## Cálculo SBC

```python
def calcular_sbc(sueldo_diario: Decimal, prestaciones_fijas: Decimal = Decimal("0")) -> Decimal:
    """SBC = sueldo diario × factor de integración.

    Factor mínimo: 1.0452 (sin prestaciones fijas adicionales)
    Si paga aguinaldo > 15 días o prima vacacional > 25%: factor mayor.
    """
    return sueldo_diario * Decimal("1.0452") + prestaciones_fijas
```

## Output

```json
{
  "empleado_id": "EMP-001",
  "rfc_hash": "...",
  "nombre_completo_hash": "...",
  "alta_exitosa": true,
  "fecha_alta": "2026-06-12",
  "sbc_diario_mxn": "627.12",
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

- Aviso IDSE: 5 días hábiles desde alta (Art. 15 LSS)
- Sin aviso: trabajador no protegido si accidente + multa al patrón
- SBC mal calculado: capital constitutivo en auditoría IMSS
