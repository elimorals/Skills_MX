---
name: fiscal-host-art113a
description: Cálculo fiscal específico para host de Airbnb bajo Art. 113-A LISR + régimen 626 RESICO PF o 612 PFAE. La plataforma retiene 4% ISR + 8% IVA automáticamente. Adicionalmente, los hosts deben declarar y pagar ISH (Impuesto Sobre Hospedaje) estatal (3-5% según entidad) que NO retiene la plataforma. Si ingresos anuales > $300k, considera complementar deducciones. Usar cuando el usuario diga calcular impuestos airbnb, ISR host, ISH hospedaje, retenciones airbnb.
allowed-tools: Read, Write
---

# Fiscal Airbnb host — Art. 113-A LISR + ISH

## Componente federal (Art. 113-A LISR)

**Retención automática plataforma**:
- ISR: 4% del ingreso bruto
- IVA: 8% (50% del 16% acumulable, simplificado)

Estas retenciones aparecen en CFDI emitido por la plataforma a tu RFC.

## Componente estatal (ISH — Impuesto Sobre Hospedaje)

⚠ La plataforma NO retiene ISH. **Tú debes declararlo y pagarlo**.

**Tasas por estado (referencia 2026, validar vigencia)**:
- CDMX: 3.5%
- Quintana Roo: 5.0%
- Yucatán: 3.0%
- Jalisco: 3.0%
- Baja California Sur: 3.0%
- Estado de México: 4.0%

**Plazo**: declaración mensual al estado (varía día, típico 15-20 del mes siguiente).

## Algoritmo

```python
def calcular_fiscal_host_mes(ingreso_bruto: Decimal, estado: str, regimen: str) -> dict:
    # Plataforma ya retuvo
    isr_retenido = ingreso_bruto * Decimal("0.04")
    iva_retenido = ingreso_bruto * Decimal("0.08")

    # ISH estatal
    tasas_ish = {"cdmx": 0.035, "qroo": 0.05, "jalisco": 0.03, "edomex": 0.04}
    tasa_ish = Decimal(str(tasas_ish.get(estado, 0.035)))
    ish_a_pagar = ingreso_bruto * tasa_ish

    # ISR adicional (si aplica más allá de retención)
    if regimen == "626_RESICO_PF":
        # En RESICO la retención es definitiva si no hay otras actividades
        isr_adicional = Decimal("0")
    else:  # 612 PFAE
        # Necesita declaración con cálculo completo
        isr_adicional = "TODO_CALCULAR_CON_DEDUCCIONES"

    return {
        "ingreso_bruto_mxn": str(ingreso_bruto),
        "isr_retenido_plataforma_mxn": str(isr_retenido),
        "iva_retenido_plataforma_mxn": str(iva_retenido),
        "ish_estado": estado,
        "ish_tasa": float(tasa_ish),
        "ish_a_pagar_mxn": str(ish_a_pagar),
        "neto_estimado_mxn": str(ingreso_bruto - isr_retenido - iva_retenido - ish_a_pagar),
    }
```

## Output

```json
{
  "rfc_hash": "...",
  "mes": "2026-06",
  "estado": "cdmx",
  "regimen": "626_RESICO_PF",
  "ingreso_bruto_mxn": "40700.00",
  "comision_airbnb_mxn": "5698.00",
  "neto_de_airbnb_mxn": "35002.00",
  "isr_retenido_plataforma_mxn": "1628.00",
  "iva_retenido_plataforma_mxn": "3256.00",
  "ish_cdmx_3.5_pct_mxn": "1425.00",
  "deadline_ish_cdmx": "2026-07-20",
  "neto_final_mxn": "28693.00",
  "obligacion_declaracion_isr": false,
  "obligacion_declaracion_ish": true,
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Ingreso > $3.5M anuales | NO RESICO, pasa a PFAE — re-cálculo |
| Host con múltiples propiedades en distintos estados | ISH por cada estado por separado |
| Huésped pide CFDI | Emitir CFDI tipo I uso D04 (casa habitación temporal) o G03 si fines de negocio |
| Vrbo + Booking | Cada plataforma retiene Art. 113-A independientemente |

## ⚠ Compliance

- ISH cambia cada año por estado — validar tasa vigente
- Multas por no declarar ISH: $3,000-$50,000 MXN según estado
- `vigencia_validada: false` — contador valida
