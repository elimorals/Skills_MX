# mp_cfe_interconexion_solar

Generación distribuida (prosumidor) con CFE: clasificación legal, pasos y simulador de ahorro.

**Universo**: ~500k instalaciones residenciales + PyME.

## Tools

- `cfe_solar_solicitar(rpu, kw_instalados, tarifa_actual, tipo_sistema?, tension?)` — clasifica la
  central (Generadora Exenta < 0.7 MW / permiso CNE) y devuelve **handoff**; nunca presenta nada.
- `cfe_solar_estatus(folio)` — handoff (no hay consulta pública del estatus).
- `cfe_solar_simular_ahorro(costo_kwh_mxn, kwh_consumo, kwh_solar, esquema?, precio_exportacion_mxn_kwh?)`
  — modelo mensual con el costo del recibo; esquemas `medicion_neta` o `facturacion_neta`.
- `cfe_solar_listar_tarifas()` — nombres de tarifas, sin precios.

## Estado real

Tipo: **cálculo normativo local** + handoff. Verificado 2026-10-14 contra la Ley del Sector
Eléctrico ("Nueva Ley DOF 18-03-2025", https://www.diputados.gob.mx/LeyesBiblio/pdf/LSE.pdf):

| Constante | Valor | Fuente |
|---|---|---|
| Generadora Exenta / Generación Distribuida | < 0.7 MW, sin permiso | LSE Arts. 3 fr. XXII, 19, 25 |
| Autoconsumo con permiso simplificado | 0.7-20 MW | LSE Art. 30 |
| Venta de excedentes | a la Suministradora de Servicios Básicos; contratos y contraprestaciones los emite la CNE | LSE Art. 27 |

Retirado por no tener fuente: folios/estatus inventados, costos "promedio" por kWh por tarifa, el
umbral de 0.5 que comparaba kW contra MW (un sistema de 1 kW salía como "PyME"), el límite de
500 kW y el "factor de exportación 0.70 / autoconsumo inteligente 2026".

Sitios de CFE (www.cfe.mx → www.cfe.gob.mx, app.cfe.mx) responden 403 a clientes no-navegador
(2026-10-14); no se usan como fuente automática.
