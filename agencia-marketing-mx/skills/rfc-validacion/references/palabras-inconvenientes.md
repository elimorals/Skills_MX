# Palabras inconvenientes en RFC — listado SAT

El SAT mantiene un listado de combinaciones de letras que no se permiten como inicio de RFC por considerarse obscenas, ofensivas o malsonantes. Si las primeras 3 letras (PM) o 4 letras (PF) caerían en alguna de estas, el SAT sustituye automáticamente la cuarta letra por **X**.

## Lista oficial (vigente)

```
BACA   BAKA   BUEI   BUEY   CACA   CACO   CAGA   CAGO   CAKA   CAKO
COGE   COGI   COJA   COJE   COJI   COJO   COLA   CULO   FALO   FETO
GETA   GUEI   GUEY   JETA   JOTO   KACA   KACO   KAGA   KAGO   KAKA
KAKO   KOGE   KOGI   KOJA   KOJE   KOJI   KOJO   KOLA   KULO   LILO
LOCA   LOCO   LOKA   LOKO   MAME   MAMO   MEAR   MEAS   MEON   MIAR
MION   MOCO   MOKO   MULA   MULO   NACA   NACO   PEDA   PEDO   PENE
PIPI   PITO   POPO   PUTA   PUTO   QULO   RATA   ROBA   ROBE   ROBO
RUIN   SENO   TETA   VACA   VAGA   VAGO   VAKA   VUEI   VUEY   WUEI
WUEY
```

## Cómo lo aplica el SAT

Si tu nombre real generaría un RFC que empieza con alguna de estas combinaciones, el SAT sustituye la cuarta letra (para PF) o la tercera letra (para PM) por X.

**Ejemplo**:
- Nombre: Pedro Penagos Espinoza → letras esperadas: `PEPE`
- `PEPE` no está en lista, RFC normal
- Pero si fuera: Pedro Putos Espinoza → letras esperadas: `PUPE`
- `PUTO` está en lista → sustituye 4ta letra → resultado: `PUPX...`

## Implicación para validación

Si un RFC capturado por usuario tiene las 4 primeras letras EXACTAMENTE en esta lista (ej. el RFC empieza con `PUTO`, `PEDA`, `MOCO`, etc.), es **muy probable que sea inválido** porque el SAT habría sustituido la cuarta letra. El skill debe:

1. Detectar el prefijo problemático.
2. Alertar al usuario: "RFC sospechoso: las primeras 4 letras forman una palabra que el SAT habría sustituido. Verifica que sea el RFC real del contribuyente."
3. **No bloquear**, solo advertir — porque podría ser un caso real raro o un RFC corrupto.

## Casos donde NO alertar

- RFCs genéricos `XAXX010101000` y `XEXX010101000`: válidos por excepción, no aplican estas reglas.
- PMs que inician con razones sociales que coincidentalmente empiezan con alguna combinación: las primeras 3 letras del RFC de PM se calculan distinto que de PF.

## Referencia

El listado lo publica el SAT en la guía de cálculo del RFC. Puede ampliarse en revisiones futuras. Verificar contra la fuente oficial periódicamente.
