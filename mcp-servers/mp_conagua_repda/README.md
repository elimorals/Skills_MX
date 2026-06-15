# mp_conagua_repda

CONAGUA REPDA — permisos extracción y descarga + reportes semestrales + LFD.

**Universo**: ~50k industrias usuarias intensivas agua MX.

## Tools

- `repda_consultar_titular(identificador)` — permisos vigentes por RFC o num_titulo.
- `repda_estado_reporte(num_titulo, periodo)` — semestral presentado: bool.
- `repda_calcular_lfd(num_titulo, m3, zona_disponibilidad)` — cuota LFD MXN.
- `repda_vigencia(num_titulo)` — años restantes.
- `repda_requiere_medidor(volumen_anual_m3)` — umbral 150k m³.
- `repda_listar_tipos_uso()` — catálogo.
