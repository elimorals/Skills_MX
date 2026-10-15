---
name: cumplimiento-rab-cdmx
description: Cumplimiento del registro de anfitriones de hospedaje temporal en CDMX (Padrón de Personas Anfitrionas de la Ley de Turismo de la CDMX, reforma 2024; el usuario suele llamarlo "RAB"). Cubre inscripción del anfitrión y de cada inmueble en el padrón (portal estanciaeventual.cdmx.gob.mx), constancia y folio que deben aparecer en cada anuncio de Airbnb/Vrbo/Booking, límite de inmuebles por anfitrión, reporte semestral de ocupación y tope de ocupación anual. Aplica solo a CDMX. Usar cuando el usuario diga RAB CDMX, registro anfitriones, padrón anfitriones, regulación airbnb cdmx, cumplimiento, folio airbnb cdmx.
allowed-tools: Read, Write
---

# Cumplimiento del registro de anfitriones — CDMX

Confianza media: el marco está en la reforma a la Ley de Turismo de la CDMX (publicada en abril de 2024) y en notas de prensa de 2026; no se revisó el texto vigente de los lineamientos en la Gaceta Oficial. Fuentes: Expansión 2024-03-25 y 2026-05-21; Holland & Knight; GT Law (abril 2024).

## Qué es

Las personas anfitrionas que ofrecen hospedaje temporal en CDMX a través de plataformas deben inscribirse e inscribir cada inmueble en el Padrón del Gobierno de la CDMX. Las plataformas también deben registrarse en su propio padrón. En mayo de 2026 el gobierno abrió el registro en **estanciaeventual.cdmx.gob.mx** con un plazo de 30 días (la nota da como fecha límite el 20 o el 30 de junio de 2026; verificar si hubo prórroga).

## Requisitos de inscripción (según la reforma)

- Datos del anfitrión, RFC y constancia de situación fiscal
- Documento que acredite la propiedad o posesión del inmueble (si eres inquilino: autorización del propietario)
- Alta de cada inmueble en el padrón
- La constancia y el folio se registran en cada plataforma donde anuncias

## Reglas operativas

| Regla | Detalle | Confianza |
|---|---|---|
| Inmuebles por anfitrión | Hasta 3 inscritos como persona anfitriona; con 4 o más debes registrarte como establecimiento mercantil donde el uso de suelo lo permita | media |
| Reporte de ocupación | Semestral | media |
| Tope de ocupación | Coeficiente máximo de ocupación de 50% anual por unidad (reforma aprobada por el Congreso CDMX en 2024) | **verificar** vigencia y forma de cómputo |
| Multas | El monto no aparece en las fuentes consultadas | **verificar** |

## Output

```json
{
  "padron_status": "inscrito",
  "folio_padron": "<folio de la constancia>",
  "propiedad": "Roma Norte 1A",
  "fecha_inscripcion": "2026-06-10",
  "inmuebles_inscritos_del_anfitrion": 1,
  "proximo_reporte_semestral": "verificar fecha en el portal",
  "noches_ocupadas_anio": 90,
  "ocupacion_pct_anio": 24.7,
  "alertas": [
    "Tope de ocupación 50% anual pendiente de verificar en Gaceta Oficial"
  ],
  "folio_visible_en_anuncios": true,
  "vigencia_validada": false
}
```

`ocupacion_pct_anio` = noches ocupadas / 365 (90 / 365 = 24.7%).

## Cómo registrarse (lo hace el humano)

1. Entrar a https://estanciaeventual.cdmx.gob.mx (la Secretaría de Turismo CDMX anunció módulos de apoyo).
2. Capturar datos del anfitrión y del inmueble; subir RFC, constancia de situación fiscal y acreditación de propiedad/posesión.
3. Descargar la constancia con folio.
4. **Registrar el folio en TODAS las publicaciones** (Airbnb, Vrbo, Booking).
5. Agendar el reporte semestral de ocupación.

## Casos edge

| Caso | Acción |
|---|---|
| Propietario fuera de CDMX | Puede gestionarlo un representante con poder |
| Rentas un cuarto de tu casa | Revisa en el portal si aplica el mismo registro |
| 4 o más inmuebles | Registro como establecimiento mercantil; revisar uso de suelo |
| Condominio | Revisa que el reglamento del condominio no prohíba hospedaje temporal |

## ⚠ Compliance

- Verifica en la Gaceta Oficial de la CDMX los lineamientos vigentes, el tope de ocupación y las sanciones antes de asesorar.
- Otros estados (Quintana Roo, Jalisco) tienen reglas distintas: no extrapolar.
- Valida con abogado o gestor local.
