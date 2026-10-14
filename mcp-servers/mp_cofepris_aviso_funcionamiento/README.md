# mp_cofepris_aviso_funcionamiento

¿Licencia sanitaria o aviso de funcionamiento? Clasificación con fundamento en la Ley General de Salud.

**Universo**: ~500k establecimientos con giros regulados (restaurantes, farmacias, consultorios, etc.).

## Tools

- `cofepris_clasificar_giro(actividad)` — `licencia_sanitaria` (Art. 198) / `aviso_funcionamiento`
  (Art. 200 Bis) / `verificar_acuerdo_ssa`, con el fundamento de cada giro.
- `cofepris_requisitos_aviso(actividad, estado)` — datos del aviso (Art. 200 Bis fr. I-VI) y plazo
  de 30 días antes de operar; si el giro requiere licencia, lo dice.
- `cofepris_consultar_aviso(identificador)` — **handoff humano**: no existe consulta pública.
- `cofepris_listar_giros()` — catálogo con fundamentos.

## Estado real

Tipo: **cálculo normativo local** + handoff para la consulta.

Constantes verificadas contra la LGS vigente
(https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf, últimas reformas DOF 15-01-2026,
consultado 2026-10-14): Arts. 197 (definición de proceso, incluye expendio), 198 fr. I-VI (licencia),
200 Bis (aviso, 30 días, fracciones I-VI), 258 y 260 fr. IV (responsable sanitario de farmacias).

Lo que se eliminó por no tener sustento: la clasificación "giro A/B/C", los tiempos de resolución
(10-30 días hábiles) y la consulta de vigencia que decidía "vigente" con un hash del RFC.

Pendiente: la lista exacta de giros que obligan al aviso la fija el **Acuerdo de la SSA** previsto
en el Art. 200 Bis (por clave de actividad). No se cotejó giro por giro; por eso los giros sin
insumos de salud devuelven `verificar_acuerdo_ssa`.

Búsqueda de datos abiertos: `datos.gob.mx` CKAN `package_search?q=cofepris` → 0 datasets (2026-10-14).
