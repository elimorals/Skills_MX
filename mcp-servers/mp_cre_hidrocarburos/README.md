# mp_cre_hidrocarburos

Permisos de expendio de petrolíferos (CRE → CNE) + controles volumétricos (Anexo 30 SAT).

La CRE se extinguió en 2025; sus atribuciones pasaron a la Comisión Nacional de Energía
(CNE). Los permisos nuevos ya salen como `CNE/PL/.../EXP/ES/2025`.

## Tools

- `cre_consultar_permiso(identificador)` — **real**: busca en el padrón público de
  estaciones por permiso exacto o razón social. Solo cubre expendio en estaciones de
  servicio; no encontrarlo no prueba invalidez (devuelve handoff a la CNE).
- `cre_calendar_reporte(anio, mes_actual)` — 12 periodos mensuales; la fecha límite
  depende del título de permiso (`fecha_limite: null`, ya no se inventa "día 15").
- `cre_evaluar_anexo30(litros_mes_max, tiene_permiso_cre, gas_natural_gj_anio)` — obligación
  de controles volumétricos.
- `cre_reportar_zeros(num_permiso, periodo)` — **handoff humano**, nunca envía. Antes
  devolvía un folio y `reporte_aceptado: true` inventados.
- `cre_listar_tipos_permiso()` — catálogo.

## Estado real

- Upstream: `https://publicacionexterna.azurewebsites.net/publicaciones/places` (XML público
  del programa de precios, sin login ni CAPTCHA). Se cachea 24 h (`FileCache`).
- Mock solo con `PLUGINS_MX_MOCK=1`; upstream caído → `UpstreamError`.

| Fecha | URL | Status | Resultado |
|---|---|---|---|
| 2026-10-14 | GET .../publicaciones/places | 200 | 3.18 MB, 15,046 estaciones (14,250 `PL/N/EXP/ES`, 433 `CNE/PL/...`, 359 `ESA`) |
| 2026-10-14 | `consultar_permiso("PL/658/EXP/ES/2015")` (test live) | 200 | ESTACION HIPODROMO SA DE CV |

Fixture: `tests/fixtures/places.xml` (recorte real). Live: `PLUGINS_MX_LIVE=1 pytest mp_cre_hidrocarburos -k live`.

## Constantes

- 75,714 L de petrolíferos en al menos un mes / 5,000 GJ anuales de gas natural (sujetos
  sin permiso, regla 2.6.1.2 RMF con Art. 28 fr. I-B CFF). Cotejado contra el resumen de
  PwC México "Controles volumétricos" (25-nov-2025). **No cotejado** contra el texto de la
  RMF 2026 (DOF 28-12-2025): el PDF del SAT no se pudo descargar el 2026-10-14.
