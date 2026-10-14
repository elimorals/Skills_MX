# mp_ish_mx

Impuesto sobre Hospedaje (ISH) 2026 — las 32 entidades. Cálculo local.

## Tools

- `ish_calcular(estado, monto_hospedaje, plataforma_digital=false)` → ISH, tasa, fuentes y confianza.
- `ish_info_estado(estado)`, `ish_listar_estados(solo_aplicables)`, `ish_comparar_estados([...], monto)`.

## Estado real (2026-10-14)

No consulta portales. Tasas revisadas contra fuentes secundarias 2026; no se abrió
el texto legal primario de ningún estado (confianza máxima "media"):

- El Contribuyente, tabla ISH 2026: https://www.elcontribuyente.mx/impuesto-sobre-hospedaje/
- Airbnb, estados donde recauda: https://es-l.airbnb.com/help/article/2288
- BHR ene-2026 (Yucatán, EdoMex) y El Contribuyente feb-2026.

Correcciones frente al catálogo anterior: EdoMex, Coahuila, Chihuahua, Tamaulipas
y Tlaxcala SÍ cobran ISH (antes 0%); CDMX y Querétaro tienen tasa de 5% para
plataformas, Quintana Roo 6%; Yucatán 4.5%; Nayarit y BC 5%; Guanajuato, SLP,
Guerrero, BCS 4%; Morelos 3.75%.

Confianza baja (fuentes en conflicto): JAL (4% vs 5%), HGO (2.5% vs 3%), OAX,
VER (vigencia), CHIH, DGO, TLAX.
