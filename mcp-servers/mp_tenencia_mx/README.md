# mp_tenencia_mx

MCP unificado para tenencia + refrendo vehicular en 20 estados MX.

## Por qué importa

- **Universo**: 46M vehículos × cálculo anual.
- **Casos de uso**: leasing/flotillas, comparación re-emplaque, asesoría fiscal vehicular.
- **Tipo**: offline-first (cálculo no requiere red). Útil donde otros MCPs requieren CAPTCHA.

## Tools

### `tenencia_calcular(estado, valor_factura, anio_modelo)`
Calcula tenencia + refrendo proyectado.

### `tenencia_info_estado(estado)`
Configuración completa: tasa, refrendo, exenciones, portal.

### `tenencia_listar_estados(solo_con_tenencia)`
Lista 20 estados del catálogo.

### `tenencia_comparar_estados(estados, valor_factura, anio_modelo)`
Compara N estados — ranking barato a caro + ahorro máximo.

## Cobertura

| Estado | Tenencia | Refrendo | Notas |
|---|---|---|---|
| EdoMex | ✅ 3.0% | ✅ $940 | Exento < $400K |
| Jalisco | ✅ 2.6% | ✅ $720 | Exento < $250K |
| Oaxaca | ✅ 2.5% | ✅ $650 | Exento < $150K |
| NL, QRO, SON, VER, CHIH, SIN, TAM | ❌ | ✅ | Solo refrendo |
| AGS, HGO, BC, BCS, CAM, YUC, MICH, MOR, SLP, GTO | ❌ | ✅ | Solo refrendo |

## Cálculo

```
factor_depreciacion = tabla(antiguedad)  # 1.00 → 0.10
valor_depreciado    = valor_factura × factor
tenencia            = valor_depreciado × tasa_estado / 100  (si aplica)
refrendo            = costo_fijo_estado
subtotal            = tenencia + refrendo
```

Factor depreciación: 100% (0 años) → 85% (1 año) → ... → 10% (≥9 años).

Subsidio: si valor_factura < umbral_exencion del estado → tenencia = 0.

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_tenencia_mx/tests -v
```
