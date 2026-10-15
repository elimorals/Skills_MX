# laboratorio-clinico-mx

Plugin para laboratorios clínicos pequeños y medianos (≤50 muestras/día típico PyME) en México. Score research: **7.3/10**, mercado: ~10k laboratorios privados. Construido sobre `core-mexico` + `clinica-salud-mx`.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install laboratorio-clinico-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills propios (5)

| Skill | Propósito |
|---|---|
| `recepcion-muestra` | Etiquetado + cadena de custodia + pre-analítica |
| `tracking-procesamiento` | Etapas + QC interno + valores de pánico |
| `entrega-resultados` | PDF firmado QFB + interpretación + rangos demográficos |
| `integracion-medico-referente` | Comisiones por referencia + CFDI honorarios |
| `compliance-cofepris-lab` | NOM-007-SSA3 + licencia + PEEC + RBI NOM-087 |

## Compliance crítico

- **NOM-007-SSA3** (laboratorios clínicos)
- **NOM-087-ECOL-SSA1** (residuos biológico-infecciosos)
- **COFEPRIS Aviso Funcionamiento + Licencia Sanitaria**
- **Responsable Sanitario QFB con cédula vigente**
- **PEEC trimestral** (Programa Evaluación Externa Calidad)

## Validación pendiente

⚠ NOM-007 versión vigente fecha. Confirmar trámites COFEPRIS actuales.
⚠ Comisiones a médicos: zona gris COFEPRIS — revisar con asesor sanitario.
⚠ Partner: laboratorio PyME con responsable sanitario para dogfooding.
