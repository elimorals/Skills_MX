# constructora-mx

Plugin para constructoras, ferreterías de obra, desarrolladores inmobiliarios PyME y transportistas de materiales en México. Construido sobre `core-mexico` + `nomina-pymes-mx`.

## Skills propios (5)

| Skill | Propósito |
|---|---|
| `cfdi-carta-porte` | CFDI con complemento Carta Porte 3.x (autotransporte federal) |
| `cfdi-estimacion-obra` | CFDI por estimación de avance con anexo + retención garantía |
| `retenciones-repse` | Retención 6% IVA a subcontratistas REPSE + validación padrón |
| `contrato-obra-precio-alzado` | Lump sum con calendario + penalización + vicios ocultos |
| `dispersion-cuadrilla` | Raya semanal SPEI + CFDI Nómina + IMSS retención |

## Comandos (4)

- `/constructora:emitir-carta-porte`
- `/constructora:emitir-estimacion`
- `/constructora:calcular-retenciones-repse`
- `/constructora:dispersar-cuadrilla`

## Compliance crítico

- **SAT autotransporte**: Carta Porte 3.x obligatorio (multas hasta $99k MXN por CFDI sin complemento si aplica)
- **REPSE**: subcontratistas DEBEN estar en padrón vigente — si no, gastos no deducibles
- **IMSS clase IV-V**: riesgo construcción típico — primas más altas
- **LFT Art. 17**: pago semanal mínimo en construcción
- **PROFECO**: penalización por demora regulada en contratos de obra residencial

## Validación pendiente

⚠ Score honesto: 4.5/9 inicial. Para producción-grade:
- Abogado especializado construcción debe revisar `contrato-obra-precio-alzado`
- Validar Carta Porte 3.x contra anexos SAT vigentes
- Confirmar tasa REPSE 6% IVA vigencia (puede haber cambiado)
- Partner constructora pequeña/mediana para validación operativa

## Ver también

- `nomina-pymes-mx/README.md` — dependencia para dispersar cuadrilla
- `docs/specs/` (pendiente spec constructora)
