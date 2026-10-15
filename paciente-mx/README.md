# paciente-mx

Plugin para el paciente / consumidor de salud en México.

> Consolida tres verticales originales: `paciente-mx` + `geriatria-mx` + `laboratorio-clinico-mx`.
> Score research: **7.5/10**.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install paciente-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills

1. `agenda-citas-personal` — citas con N médicos
2. `expediente-salud-personal` — tu copia, no la del médico
3. `tracking-medicamentos-recordatorios` — adherencia
4. `estudios-laboratorios` — resultados + interpretación
5. `cfdis-medicos-deducibles-acumulados` — para declaración anual

## Casos especiales

- Adultos mayores: tracking adicional (presión, glucosa, etc.)
- Pacientes crónicos: medicamentos diarios + cita seguimiento
- Pacientes nuevos: onboarding médico + GMM
