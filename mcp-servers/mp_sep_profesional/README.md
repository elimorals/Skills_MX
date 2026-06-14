# mp_sep_profesional

MCP standalone para validación de cédulas profesionales SEP (Registro Nacional de Profesionistas).

**Portal**: https://cedulaprofesional.sep.gob.mx/ — **SIN CAPTCHA**, automatizable 100%.

## Por qué importa

- **Único portal federal MX de validación profesional que se puede automatizar end-to-end** (sin humano en loop).
- Desbloquea verticales que por ley requieren validar cédula:
  - **`telemedicina-mx`** (NOM-004-SSA3-2012 + Acuerdo COFEPRIS 28-mar-2024)
  - **`consultorio-especialista-mx`**, `clinica-salud-mx`, `psicoterapia-mx`
  - **`despacho-legal-mx`** (Ley General de Profesiones Art. 26)
  - **`despacho-contable-mx`** (LISR firma dictamen)
  - `inmobiliaria-mx` (arquitectos firma de planos)

## Tools expuestas

| Tool | Modo | Para qué |
|------|------|----------|
| `sep_consultar_cedula` | Por número | Validar cédula que el cliente proporcionó |
| `sep_consultar_por_datos` | Por nombre+apellidos | Cuando no se tiene el número |
| `sep_validar_medico_para_consulta` | Compuesto | Telemedicina-mx: ¿este médico puede dar consulta? |
| `sep_listar_profesiones_reguladas` | Catálogo | Saber qué profesiones requieren validación |

## Flujo `sep_validar_medico_para_consulta` (NOM-004 + COFEPRIS 2024)

```
input: cedula="1234567", cedula_especialidad="7654321"
   │
   ├─→ Valida cédula general:
   │    - debe existir en RNP
   │    - debe estar vigente
   │    - debe ser de salud (Médico Cirujano u homólogo)
   │
   ├─→ Si especialidad: valida también
   │    - debe estar vigente
   │
   └─→ Resultado:
        - puede_dar_consulta = cédula_general_ok
        - puede_recetar_controlados = cédula_general_ok AND cédula_especialidad_ok
        - cumple_nom_004 = puede_dar_consulta
        - cumple_cofepris_2024 = puede_dar_consulta
```

## Modos

| Variable | Default | Efecto |
|----------|---------|--------|
| `PLUGINS_MX_MOCK=1` | ✅ | Datos simulados, no toca SEP |
| `MP_PLAYWRIGHT_PUBLIC=1` | — | Activa Playwright real contra `cedulaprofesional.sep.gob.mx` |

## Caché

30 días por cédula. Los datos del RNP cambian raramente (correcciones, defunciones).

## Bitácora

Las cédulas y CURP se hashean antes de loggearse (datos personales).

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_sep_profesional/tests/ -v
```
