# mp_cofepris_aviso_funcionamiento

Apertura giros B/C COFEPRIS — Aviso de Funcionamiento + responsable sanitario.

**Universo**: ~500k giros B/C MX (restaurantes, farmacias, consultorios, etc.).

## Tools

- `cofepris_clasificar_giro(actividad)` — A/B/C según catálogo.
- `cofepris_requisitos_aviso(actividad, estado)` — checklist + tiempo + costo.
- `cofepris_consultar_aviso(identificador)` — vigencia por RFC/folio.
- `cofepris_listar_giros()` — catálogo completo.

## Verticales desbloqueados

`restaurante-mx`, `salon-mx`, `clinica-salud-mx`, `geriatria-cuidado-mayor-mx`, `veterinaria-mx`.
