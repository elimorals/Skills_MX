# migracion-extranjeros-mx

Plugin para extranjeros viviendo en México con trámites migratorios.

> Score research: **7.5/10**. Mercado ~1.5M extranjeros con residencia.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install migracion-extranjeros-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Status migratorios cubiertos

- Visitante (180 días)
- Residente temporal (1-4 años, renovable)
- Residente permanente
- Refugiado/asilado
- Estudiante
- Trabajador temporal

## Skills

1. `tramites-residencia-inm`
2. `renovacion-vigencias-migra` (anual / trianual)
3. `regularizacion-migratoria` (para irregulares)
4. `dashboard-tramite-migratorio`
5. `asesoria-laboral-extranjero` (permiso trabajo)
