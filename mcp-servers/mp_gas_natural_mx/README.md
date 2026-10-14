# mp_gas_natural_mx

Gas natural por red: Naturgy, ENGIE, Ecogas, Fenosa, Gas Natural del Norte.

## Tools

| Tool | Estado |
|---|---|
| `gas_tarifas_vigentes(distribuidor="ecogas", zona=None)` | Real: descarga y lee los PDFs oficiales que publica el distribuidor (precio mensual residencial por zona + lista de tarifas máximas aprobada). Cita cada PDF en `fuente`. Requiere el extra `estatal-resto` (pypdf). |
| `gas_consultar_recibo(distribuidor, contrato)` | Handoff humano (`motivo: login`): ningún distribuidor tiene consulta pública de recibo. |
| `gas_listar_distribuidores()` | Catálogo local; `tarifas_publicas` indica si hay fuente verificada. |

Base normativa de la publicación: Directiva DIR-GAS-001-2007, disposición 21.1 (citada en
el propio PDF de Ecogas, junto con el oficio de aprobación y el permiso G/013/DIS/1997).

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://www.ecogas.com.mx/tarifas.php` | 200; 5 PDFs (`pdf/index.php?file=…`) |
| 2026-10-14 | `…?file=preciosmexicali.pdf` | 200 PDF: "Usuarios Residenciales de Mexicali — Precio del mes de Septiembre $8.27 … MXP/Gjoule $217.56 (sin IVA)" |
| 2026-10-14 | `…?file=1c978b…_1811398071.pdf` | 200 PDF: "Zona Geográfica Chihuahua — Lista de tarifas máximas autorizadas para 2025", oficio F00.07.UH/3851/2026 |
| 2026-10-14 | `https://www.engie.mx/` | NXDOMAIN |
| 2026-10-14 | `https://www.naturgy.com.mx/` | 200; sin página pública de tarifas localizada |

`gas_tarifas_vigentes` para distribuidores sin fuente verificada → `upstream_error`
(`implementado: false`). Mock solo con `PLUGINS_MX_MOCK=1`.
Test live: `PLUGINS_MX_LIVE=1 pytest mp_gas_natural_mx -m live`.
