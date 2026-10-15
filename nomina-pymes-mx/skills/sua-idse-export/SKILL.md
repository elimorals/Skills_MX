---
name: sua-idse-export
description: Prepara los movimientos afiliatorios del mes (altas, bajas, modificaciones de salario, ausentismos, incapacidades) para cargarlos en el SUA (Sistema Único de Autodeterminación) e IDSE (IMSS Desde Su Empresa), y concilia la liquidación mensual (IMSS) y bimestral (RCV + INFONAVIT) con pago a más tardar el día 17. No sustituye al SUA oficial. Usar cuando el usuario diga SUA, IDSE, archivo IMSS, movimientos IMSS del mes, pago IMSS bimestral, liquidación SUA, cédula de determinación.
allowed-tools: Read, Write
---

# SUA / IDSE — preparación de movimientos

## Qué es cada cosa

- **IDSE** (IMSS Desde Su Empresa): portal donde el patrón presenta, con su e.firma, los **avisos afiliatorios** (alta, baja, modificación de salario) dentro de 5 días hábiles (Art. 15 fr. I LSS).
- **SUA**: programa de escritorio del IMSS que calcula la **liquidación de cuotas**. Genera el archivo de pago que se entera en banco o por SIPARE.
  - **Mensual**: enfermedades y maternidad, invalidez y vida, riesgos de trabajo, guarderías.
  - **Bimestral**: retiro, cesantía y vejez (RCV) + INFONAVIT (aportación y amortización).
  - Pago: a más tardar el **día 17** del mes siguiente (Art. 39 LSS).

## Qué genera este skill

Un archivo de trabajo por mes con cada movimiento, listo para capturar o importar al SUA con su layout oficial de importación. **El layout exacto (posiciones y longitudes) lo define el manual del SUA vigente**; este skill no lo inventa: si el usuario necesita el archivo de importación, pídele la versión del SUA y usa el layout de su manual.

Campos por movimiento:
- ALTA / REINGRESO: NSS, RFC, CURP, nombre, fecha, SBC, tipo de trabajador, tipo de jornada, registro patronal.
- BAJA: NSS, fecha, causa.
- MODIFICACIÓN de salario: NSS, nuevo SBC, fecha (incluye la de aniversario por más días de vacaciones).
- AUSENTISMOS: NSS, fechas (su efecto en cuotas sigue el Art. 31 LSS; el SUA lo aplica).
- INCAPACIDADES: NSS, folio, periodo, rama.

## Algoritmo

```python
def preparar_movimientos(mes: str, empleados: list, registro_patronal: str) -> Path:
    out = Path(f"~/.local/share/plugins-mx/sua/{mes}-movimientos.csv").expanduser()
    filas = [m.as_row(registro_patronal) for e in empleados for m in e.movimientos_mes(mes)]
    escribir_csv(out, filas)
    return out
```

Conciliación: compara la cédula del SUA contra la **EMA/EBA** (emisión mensual/bimestral del IMSS). Si existe `mp_imss_patronal` (`imss_ema_vs_eba_diferencias`, `imss_descargar_cedula_autodeterminacion`; estado "sin verificar"), úsalo como apoyo y confirma en el portal.

## Output

```json
{
  "mes_periodo": "2026-06",
  "registro_patronal": "...",
  "movimientos_totales": 13,
  "altas": 2,
  "bajas": 1,
  "modificaciones": 5,
  "ausentismos": 3,
  "incapacidades": 2,
  "archivo_path": "~/.local/share/plugins-mx/sua/2026-06-movimientos.csv",
  "pago_mensual_imss_deadline": "2026-07-17",
  "pago_bimestral_rcv_infonavit": "bimestre may-jun, mismo día 17-jul-2026",
  "siguiente_paso": "Capturar/importar en SUA, cotejar contra EMA/EBA y pagar",
  "vigencia_validada": false
}
```

## ⚠ Si hay errores

- Diferencias entre lo pagado y lo debido: el IMSS emite **cédula de liquidación de diferencias** con actualización, recargos y multa (Art. 304 LSS: 40% a 100% de las cuotas omitidas).
- **Capital constitutivo** (Arts. 77-79 LSS) aplica cuando un trabajador no inscrito o con salario mal registrado sufre un riesgo: el patrón reembolsa al IMSS las prestaciones otorgadas. Es otro riesgo, no la multa por diferencias.
- Revisa con tu contador antes de presentar.
