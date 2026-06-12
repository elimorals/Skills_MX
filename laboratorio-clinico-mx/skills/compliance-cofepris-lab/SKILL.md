---
name: compliance-cofepris-lab
description: Tracking de compliance regulatorio del laboratorio clínico ante COFEPRIS (Comisión Federal para Protección contra Riesgos Sanitarios) cumpliendo NOM-007-SSA3-2011 (laboratorios clínicos), Aviso de Funcionamiento vigente, Responsable Sanitario con cédula vigente (QFB que firma todos los resultados), Programa de Garantía de Calidad documentado con controles internos diarios y externos trimestrales (PEEC - Programas de Evaluación Externa de Calidad), bitácora de mantenimiento y calibración de equipos analíticos, control de inventario y caducidad de reactivos (los reactivos vencidos producen resultados inválidos), Manejo de Residuos Biológico-Infecciosos según NOM-087-ECOL-SSA1 con empresa autorizada de disposición final, y trazabilidad documental para inspecciones COFEPRIS (que pueden llegar sin previo aviso). Genera dashboard de cumplimiento por área crítica y alertas tempranas (renovación de cédula del responsable sanitario, próximos PEEC, renovación de licencia sanitaria). Usar cuando el usuario diga "compliance COFEPRIS lab", "auditoría sanitaria", "responsable sanitario", "NOM-007", "garantía calidad lab", "renovación licencia COFEPRIS". NO usar para compliance fiscal SAT ni para LFPDPPP.
allowed-tools: Read, Write, Edit
---

# Compliance COFEPRIS del laboratorio clínico

## Documentos obligatorios vigentes

| Documento | Vigencia | Renovación |
|---|---|---|
| Aviso de Funcionamiento COFEPRIS | Indefinida con actualización por cambios | Al modificar razón social, dirección, responsable |
| Responsable Sanitario (QFB) cédula | Indefinida | Activa siempre |
| Licencia Sanitaria | 5 años | 6 meses antes de vencer |
| Programa de Garantía Calidad | Vigente | Actualizado anualmente |
| Bitácoras equipos | Continua | Diaria |
| PEEC participación | Trimestral | Activa siempre |
| Convenio disposición RBI | Anual | Renovar 30 días antes |

## NOM-007-SSA3 — requisitos clave

1. **Áreas físicas separadas**: recepción ≠ procesamiento ≠ administrativo
2. **Iluminación + ventilación** según norma
3. **Lavabos** + materiales de bioseguridad
4. **Áreas de descontaminación** antes de descartar
5. **Bitácoras**: de temperatura del refrigerador (debe estar 2-8°C continuo)

## Programa de garantía de calidad

### Controles internos diarios

```yaml
fecha: 2026-06-12
analizador: Cobas 6000
controles_corridos:
  - nivel: Nivel 1 (normal)
    analito: glucosa
    valor_obtenido: 95
    valor_esperado: 92
    sd: 4
    cv_pct: 4.2
    aceptable: true  # dentro de 2SD
  - nivel: Nivel 2 (alto)
    analito: glucosa
    valor_obtenido: 285
    valor_esperado: 280
    aceptable: true
firma_qfb: Director Técnico
```

### PEEC trimestrales

Programa externo (típico: Sociedad Mexicana de Bioquímica Clínica):
- Trimestre 1: Q1 2026
- Resultados: aceptables
- Áreas de mejora: hematología — VCM con drift detectado

## Manejo de RBI (Residuos Biológico-Infecciosos)

| Categoría | Color | Disposición |
|---|---|---|
| Punzocortantes | Rojo | Contenedor rígido |
| Sangre/secreciones | Rojo | Bolsa con leyenda RBI |
| Cultivos microbiológicos | Amarillo + Rojo | Esterilizar antes |
| Tejidos | Amarillo | Refrigerar |

- Recolección por empresa autorizada COFEPRIS
- Manifiesto de generador + transportador + receptor
- Conservar 5 años para inspecciones

## Alertas automáticas

- 6 meses antes de vencer licencia sanitaria → tramitar renovación
- Mensual: confirmar PEEC trimestral entregado
- Diaria: revisar bitácora de temperatura del refrigerador (no debe salir 2-8°C)
- Caducidad de reactivos: lista de los que vencen este mes
- Convenio RBI: 60 días antes de vencer

## Validación pendiente

⚠ NOM-007-SSA3 vigente fecha. Posible actualización. Validar contra DOF.
⚠ Solicitud COFEPRIS de renovaciones cambia periodicamente — confirmar trámites vigentes.
