# clinica-salud-mx

Plugin para clínicas multiconsultorio (varios médicos compartiendo recursos).

> Score research: **8.3/10**. Extensión de `consultorio-especialista-mx`.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install clinica-salud-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `agenda-multi-medico` — agenda compartida con N médicos
2. `expedientes-compartidos-clinica` — accesibles por médicos autorizados con audit log
3. `facturacion-paciente-aseguradora` — facturación dual
4. `inventario-medicamentos-insumos` — control de existencias + caducidades
5. `dashboard-ejecutivo-clinica` — vista del director/administrador

## Comisión por médico

Modelo típico: clínica retiene 30-40%, médico recibe 60-70% del cobro de su consulta.

## ⚠ Compliance

Mismas reglas que `consultorio-especialista-mx` + responsabilidad solidaria de la clínica.
