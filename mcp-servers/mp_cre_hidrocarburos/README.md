# mp_cre_hidrocarburos

CRE permisionarios + Anexo 30 SAT controles volumétricos.

**Universo**: ~13k permisionarios CRE + high-volume users hidrocarburos.

## Tools

- `cre_consultar_permiso(identificador)` — vigencia + tipo.
- `cre_calendar_reporte(anio, mes_actual)` — calendario obligaciones primeros 10 días hábiles.
- `cre_evaluar_anexo30(litros_mes_max, tiene_permiso_cre)` — aplica: bool.
- `cre_reportar_zeros(num_permiso, periodo)` — reportar sin actividad.
- `cre_listar_tipos_permiso()` — 6 tipos catálogo.
