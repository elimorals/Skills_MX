# nomina-pymes-mx

Plugin para PyMEs mexicanas que pagan **sueldos régimen 605**.

> Spec: `docs/specs/08-vertical-nomina-pymes-mx.md`
> Mercado: ~600k PyMEs con empleados.

## Cobertura

- ✅ **CFDI Nómina 4.0 + Complemento 1.2 Revisión E** (vigente desde 29 dic 2025)
- ✅ Art. 99 LISR (sin excepción para timbrar)
- ✅ IMSS obrero-patronales (5 ramos)
- ✅ INFONAVIT 5%
- ✅ Subsidio para el empleo
- ✅ Aguinaldo (Art. 87 LFT — 15 días mínimo)
- ✅ PTU (Art. 117 LFT — 10% utilidad fiscal)
- ✅ Vacaciones (reforma 2023: 12 días año 1, +2/año hasta 32)
- ✅ Archivo SUA para envío IDSE

## Fuera de scope

- PyMEs > 50 empleados (otra escala — Aspel NOI o SAP)
- Sindicato (CCT — requiere negociación)
- Asimilados a salarios (caso edge)
- Extranjeros (visados + retenciones especiales)

## Comandos (6)

```
/nomina:dashboard
/nomina:alta-empleado
/nomina:correr-nomina
/nomina:cfdi-mes
/nomina:aguinaldo
/nomina:sua-export
```

## ⚠ Compliance crítico

- Errar CFDI Nómina = multa SAT
- Errar SUA = capital constitutivo IMSS (puede quebrar PyME pequeña)
- Hook `pre-timbrado-validation` lo está cubriendo en parte
- Validación con contador especializado nómina recomendada antes de producción
