# mp_conagua_repda

CONAGUA REPDA (Registro Público de Derechos de Agua) + derecho sobre agua (LFD).

**Universo**: ~50k industrias usuarias intensivas de agua en MX.

## Tools

- `repda_consultar_titular(identificador)` — inscripciones REPDA por nombre del titular
  (parcial) o número de título completo. **Real.** La consulta pública no busca por RFC.
- `repda_vigencia(num_titulo)` — ¿el título está inscrito? **Real.** El portal no publica
  la fecha de vencimiento (`vigencia_publicada: false`).
- `repda_estado_reporte(num_titulo, periodo T1-T4)` — fecha límite de la declaración
  trimestral (Art. 226 LFD) + handoff humano: no existe consulta pública del cumplimiento.
- `repda_calcular_lfd(num_titulo, m3, zona_disponibilidad 1-4, fuente)` — derecho sobre
  agua régimen general, Art. 223 apartado A LFD, cuotas RMF 2026.
- `repda_requiere_medidor(volumen_anual_m3, tipo_uso?)` — Art. 225 LFD: medición
  obligatoria para todo contribuyente (no hay umbral de 150k m³).
- `repda_listar_tipos_uso()` — usos del catálogo del REPDA.

## Estado real

- Upstream: `https://app.conagua.gob.mx/consultarepda.aspx` (ASP.NET WebForms, sin CAPTCHA,
  sin login). GET para `__VIEWSTATE`, POST con `txtTitular`/`txtTitulo`. Resultados en la
  tabla `ContentPlaceHolder1_GVRepda`, 100 por página (se devuelve la primera).
- Mock solo con `PLUGINS_MX_MOCK=1`. Error HTTP o cambio de formulario → `UpstreamError`.

| Fecha | Consulta | Status | Resultado |
|---|---|---|---|
| 2026-10-14 | POST titular="COMISION FEDERAL DE ELECTRICIDAD" | 200 | 265 registros (corte de la BD: 30-sep-2026) |
| 2026-10-14 | POST título="11CHS158257/30EMDA26" | 200 | 1 registro |
| 2026-10-14 | POST titular inexistente | 200 | 0 registros |

Fixture: `tests/fixtures/repda_cfe.html` (recorte de la respuesta real).
Live: `PLUGINS_MX_LIVE=1 pytest mp_conagua_repda -k live`.

## Constantes verificadas

Ley Federal de Derechos, texto vigente en
https://www.diputados.gob.mx/LeyesBiblio/pdf/LFD.pdf (última reforma DOF 07-11-2025;
"Cantidades actualizadas por Resolución Miscelánea Fiscal DOF 28-12-2025"), consultado 2026-10-14:

| Zona (Art. 231) | Superficial $/m³ | Subterránea $/m³ |
|---|---|---|
| 1 | 23.6460 | 31.8622 |
| 2 | 10.8860 | 12.3333 |
| 3 | 3.5694 | 4.2944 |
| 4 | 2.7295 | 3.1215 |

Corregido respecto a la versión mock: había 9 zonas con cuotas inventadas, un "reporte
semestral" que la LFD no establece (la declaración es trimestral, Art. 226) y un umbral de
medidor de 150,000 m³/año que no existe (Art. 225).
