---
name: sua-idse-export
description: Genera archivo .SUA del IMSS (Sistema Único de Autodeterminación) para envío vía IDSE (Internet Delegacional). Cubre altas/bajas/modificaciones del mes + cálculo de cuotas mensuales / bimestrales. Formato propietario IMSS — debe coincidir 100% con sistema oficial para evitar capital constitutivo. Usar cuando el usuario diga SUA, IDSE, archivo IMSS, movimientos IMSS mes.
allowed-tools: Read, Write
---

# SUA / IDSE export

## SUA = Sistema Único de Autodeterminación

Software DESKTOP obligatorio del IMSS para generar la declaración mensual / bimestral de cuotas obrero-patronales.

- **Mensual**: cuotas IMSS
- **Bimestral**: cuotas IMSS + INFONAVIT (al mismo tiempo)

## IDSE = Internet Delegacional

Portal IMSS para subir el archivo .SUA generado y pagar las cuotas.

## Formato archivo .SUA

Formato propietario texto plano (extensión `.AFI` para afiliación, `.LIQ` para liquidación). Cada línea representa un movimiento:
- ALTA: incluir NSS, RFC, CURP, nombre, fecha alta, SBC, registro patronal
- BAJA: NSS + fecha baja + causa
- MODIFICACIÓN: NSS + nuevo SBC + fecha
- AUSENTISMOS: NSS + fechas + razón
- INCAPACIDADES: NSS + período + tipo

## Algoritmo

```python
def generar_archivo_sua(mes: str, empleados: list[Empleado], registro_patronal: str) -> Path:
    output_path = Path(f"~/.local/share/plugins-mx/sua/{mes}.AFI").expanduser()
    lines = []

    # Header
    lines.append(f"# IMSS-IDSE archivo SUA generado {datetime.now().isoformat()}")
    lines.append(f"# Registro patronal: {registro_patronal}")
    lines.append(f"# Mes: {mes}")

    for emp in empleados:
        # Cada movimiento del mes
        for mov in emp.movimientos_mes(mes):
            line = format_movimiento_sua(mov, emp)
            lines.append(line)

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
```

## Validación

⚠ **CRÍTICO**: Antes de subir a IDSE, verificar manualmente que coincide con lo que muestra el SUA oficial del IMSS. Diferencias = capital constitutivo.

## Output

```json
{
  "mes_periodo": "2026-06",
  "registro_patronal": "...",
  "movimientos_totales": 45,
  "altas": 2,
  "bajas": 1,
  "modificaciones": 5,
  "ausentismos": 3,
  "incapacidades": 2,
  "archivo_path": "~/.local/share/plugins-mx/sua/2026-06.AFI",
  "tamaño_bytes": 18450,
  "siguiente_paso": "Validar contra SUA oficial IMSS antes de IDSE",
  "deadline_idse": "2026-07-17",
  "vigencia_validada": false
}
```

## ⚠ Errar = capital constitutivo

Diferencia entre lo enterado y lo correcto → IMSS calcula capital constitutivo (3-5x el monto + recargos + multa). Puede quebrar PyME pequeña.

**Siempre validar manualmente con contador antes de enviar IDSE.**
