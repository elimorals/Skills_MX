---
name: documento-pruebas-sat
description: Genera el papel de trabajo y respaldo documental para defender la declaración anual cripto ante una auditoría SAT. Incluye CSVs originales, capturas de explorer, hojas FIFO, justificación de criterios, TC DOF usados. Usar cuando el usuario diga "papel de trabajo cripto", "respaldo SAT", "documentar cripto", "auditoría cripto", "evidencia declaración cripto", "expediente fiscal cripto".
allowed-tools: Read, Write, Bash
---

# Documento de pruebas para SAT — declaración cripto

## Para qué sirve

Si el SAT te audita por operaciones cripto (probable con CARF 2026 en vigor), necesitas demostrar:
1. **Origen de los recursos**: cómo llegaron las criptos a tu wallet/cuenta
2. **Costo base verificable**: precio en MXN al momento de adquisición
3. **Cálculo de ganancia**: FIFO documentado
4. **Tratamiento aplicado**: enajenación, permuta, intereses, demás ingresos
5. **Conservación de comprobantes**: 5 años (Art. 30 CFF)

Este skill produce el **expediente completo** para responder a un requerimiento.

## Estructura del expediente

```
expediente-cripto-{rfc}-{ejercicio}/
├── 00-resumen-ejecutivo.pdf
├── 01-csvs-originales/
│   ├── bitso-{ejercicio}.csv
│   ├── binance-{ejercicio}.csv
│   ├── coinbase-{ejercicio}.csv
│   └── kraken-{ejercicio}.csv
├── 02-self-custody/
│   ├── ethereum-{address}.json     # export de Etherscan
│   ├── polygon-{address}.json
│   └── txs-clasificadas.csv
├── 03-tc-dof/
│   └── tc-usd-mxn-{ejercicio}.csv  # TC DOF de cada día con operación
├── 04-precios-mercado/
│   ├── fuente-coingecko-{ejercicio}.csv
│   └── fuente-coinmarketcap-{ejercicio}.csv  # backup
├── 05-calculos-fifo/
│   ├── inventario-inicial.csv
│   ├── operaciones-procesadas.csv
│   ├── ganancias-realizadas.csv
│   └── inventario-final.csv
├── 06-permutas/
│   └── permutas-detectadas-{ejercicio}.csv
├── 07-rendimientos/
│   ├── staking-{ejercicio}.csv
│   ├── lending-{ejercicio}.csv
│   └── airdrops-{ejercicio}.csv
├── 08-nfts/
│   └── operaciones-nft-{ejercicio}.csv
├── 09-cfdis-recibidos/
│   ├── cfdi-bitso-comisiones.xml   # CFDIs por servicios pagados
│   └── cfdi-binance-comisiones.xml
├── 10-justificacion-criterios.md
├── 11-conciliacion-final.xlsx
└── 12-declaracion-anual-borrador.pdf
```

## Algoritmo de generación

```python
import os
import shutil
import json
from datetime import datetime
from decimal import Decimal

def generar_expediente_sat(rfc: str, ejercicio: int, contexto: dict) -> str:
    """
    Genera el expediente completo a partir del contexto procesado por:
    - importar-operaciones-exchange
    - calcular-costo-base-fifo
    - permuta-cripto-cripto-gravable
    - staking-y-airdrops-ingreso
    - nft-enajenacion-bienes
    - tracking-wallets-self-custody
    """
    rfc_hash = hash_rfc(rfc)
    ruta = f"expediente-cripto-{rfc_hash}-{ejercicio}"
    os.makedirs(ruta, exist_ok=True)

    # 1. Copiar CSVs originales (NO modificarlos — auditoria requiere)
    for fuente in contexto.get("csvs_originales", []):
        shutil.copy(fuente["path"], f"{ruta}/01-csvs-originales/")

    # 2. Self-custody: export JSON crudo del explorer + tabla clasificada
    for wallet in contexto.get("wallets_self_custody", []):
        with open(f"{ruta}/02-self-custody/{wallet['cadena']}-{wallet['address']}.json", "w") as f:
            json.dump(wallet["raw_explorer_response"], f, indent=2)

    # 3. TCs DOF de cada día operado (NO solo del 31-dic)
    fechas_operadas = sorted({op["fecha"][:10] for op in contexto["operaciones"]})
    with open(f"{ruta}/03-tc-dof/tc-usd-mxn-{ejercicio}.csv", "w") as f:
        f.write("fecha,tc_dof_usd_mxn,fuente_publicacion\n")
        for fecha in fechas_operadas:
            tc = contexto["tcs_dof"].get(fecha, "—")
            f.write(f"{fecha},{tc},DOF\n")

    # 4. Precios de mercado (CoinGecko + CMC como backup)
    # ... (mismo patrón)

    # 5. Hojas FIFO
    with open(f"{ruta}/05-calculos-fifo/operaciones-procesadas.csv", "w") as f:
        f.write("fecha,activo,tipo,cantidad,valor_mxn,costo_base_aplicado,ganancia\n")
        for op in contexto["operaciones_fifo"]:
            f.write(f"{op['fecha']},{op['activo']},{op['tipo']},{op['cantidad']},"
                    f"{op['valor_mxn']},{op['costo_base']},{op['ganancia']}\n")

    # 10. Justificación de criterios (importante para SAT)
    with open(f"{ruta}/10-justificacion-criterios.md", "w") as f:
        f.write(generar_justificacion(contexto))

    # 11. Conciliación final (xlsx con totales por concepto)
    # 12. Declaración anual borrador
    generar_conciliacion_xlsx(f"{ruta}/11-conciliacion-final.xlsx", contexto)

    # PDF resumen ejecutivo
    generar_pdf_resumen(f"{ruta}/00-resumen-ejecutivo.pdf", contexto)

    return ruta


def generar_justificacion(contexto: dict) -> str:
    return f"""# Justificación de criterios aplicados

## Método de costo base
Se aplicó **FIFO** (Primeras Entradas, Primeras Salidas) por permitirlo el SAT
y ser el método de mayor aceptación internacional. Documentado en hoja
`05-calculos-fifo/`.

## Tratamiento de permutas cripto-cripto
Cada intercambio activo-activo se reconoció como **enajenación** del activo
entregado (Art. 119 LISR — transmisión de propiedad), valuado al TC DOF y precio
de mercado del día. Detalle en `06-permutas/`.

## Tratamiento de staking y airdrops
Reconocidos como **ingreso acumulable Cap IX (demás ingresos)** al valor de
mercado del día de recepción. El valor reconocido se vuelve costo base para la
posterior venta. Detalle en `07-rendimientos/`.

## NFTs
Operaciones de coleccionista esporádico — enajenación de bienes (Art. 119).
Royalties recibidos como Cap IX.

## Conservación
Este expediente se conservará en formato digital con firma electrónica (e.firma)
por **5 años** desde la fecha de presentación de la declaración (Art. 30 CFF).

## Fuentes de precio
- TC DOF: publicación oficial Banco de México
- Precios cripto: CoinGecko (primario) + CoinMarketCap (verificación)

## Vigencia
Criterios al {datetime.now().strftime('%Y-%m-%d')}. Reglas SAT pueden cambiar
en RMF anual — revisar antes de aplicar a años posteriores.
"""
```

## Buenas prácticas

1. **Inmutabilidad**: el expediente se genera 1 vez y se archiva. NO modificar después.
2. **Firma electrónica**: firmar el ZIP con e.firma al presentar declaración.
3. **Backup off-site**: copia en almacenamiento independiente (Google Drive cifrado, Mega, etc.).
4. **Versionado**: si se corrige declaración posterior (complementaria), generar expediente v2 sin tocar v1.
5. **Hash de integridad**: incluir `sha256sums.txt` de cada archivo para demostrar no-alteración.

## Output

```json
{
  "expediente_generado": "expediente-cripto-abc123-2026/",
  "archivos_incluidos": 47,
  "tamanio_mb": 12.5,
  "hash_zip": "sha256:abc...",
  "fecha_generacion": "2026-04-15T10:30:00Z",
  "vigencia_criterios": "RMF 2026 — anexo cripto pendiente",
  "checklist_pre_envio": [
    "[ ] Firmar ZIP con e.firma",
    "[ ] Subir backup off-site",
    "[ ] Anotar hash en contrato de servicios contables",
    "[ ] Conservar 5 años mínimo"
  ]
}
```
