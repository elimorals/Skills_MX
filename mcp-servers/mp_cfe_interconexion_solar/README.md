# mp_cfe_interconexion_solar

Trámite interconexión solar prosumidor CFE + contrato bidireccional.

**Universo**: ~500k instalaciones residenciales+PyME MX 2026.

**Cambios 2026**: net metering 1:1 → autoconsumo inteligente (exportación ~70%).

## Tools

- `cfe_solar_solicitar(rpu, kw_instalados, tarifa_actual, tipo_sistema?, tension?)` — folio + docs.
- `cfe_solar_estatus(folio)` — avance + siguiente paso.
- `cfe_solar_simular_ahorro(tarifa, kwh_consumo, kwh_solar)` — ahorro mensual+anual MXN.
- `cfe_solar_listar_tarifas()` — DAC/PDBT/GDMTH/GDMTO/T1.
