# Workflows ejecutables (pf-anual-mx)

Ver `core-mexico/workflows/README.md` para el patrón estándar.

## Workflows de este vertical

| Archivo | Disparador típico |
|---|---|
| `pf-anual-completa.workflow.js` | `/pf-anual:completa` o cron temporada anual (febrero) |

## Cómo correr

```
# Via skill Workflow
Workflow({
  scriptPath: "pf-anual-mx/workflows/pf-anual-completa.workflow.js",
  args: {
    rfc: "MAJG800101XYZ",
    ejercicio: 2025,
    regimen: "PFAE_612",
    incluir_bancos: true
  }
})
```

Resultado esperado: 8 fases ejecutadas, PDF de borrador generado, JSON de resultado con alertas críticas + recomendaciones.

## Validación pendiente

⚠ El workflow marca `vigencia_validada: false` hasta que un contador certifique:
- Tarifa Art. 152 LISR ejercicio
- Topes Art. 151 LISR (deducciones personales)
- Decreto de colegiaturas por nivel educativo
- Tasas RESICO PF si aplica

Ver `docs/consultorias/brief-contador-freelance-tax-pf-anual-2026.md`.

**NO presentar declaración basándose solo en este workflow sin revisión humana.**
