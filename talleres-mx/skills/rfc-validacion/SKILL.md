---
name: rfc-validacion
description: Valida estructuralmente Registro Federal de Contribuyentes (RFC) mexicano para personas físicas (13 caracteres) y personas morales (12 caracteres). Verifica formato regex, homoclave, fechas válidas, palabras inconvenientes prohibidas por SAT, y RFCs genéricos (XAXX010101000 nacional, XEXX010101000 extranjero). Útil antes de timbrar CFDI para detectar capturas erróneas, contrastar contra lista negra del SAT (69-B EFOS), y normalizar formato. Usar siempre que el usuario pegue un RFC para validar, capture datos de cliente, importe lista de contactos con RFCs, valide CFDI, validate RFC, check taxpayer ID Mexico. NO usar para CURP (es otra cosa, 18 caracteres distintos) ni para identificaciones de otros países.
allowed-tools: Read, Bash
---

# Validación de RFC

Validador estructural de RFC mexicano. Esta primera línea de defensa atrapa el 95% de errores de captura antes de mandar al PAC.

## Reglas de estructura

### Persona Moral (PM) — 12 caracteres
- **3 letras** derivadas del nombre/razón social: `ABC` (puede contener `&` o `Ñ`)
- **6 dígitos** de fecha de constitución `AAMMDD`
- **3 caracteres** homoclave alfanumérica: `XX9` (típicamente letra-letra-dígito)

Ejemplo: `IBM970131DRA` (IBM de México SA constituida 31 ene 1997, homoclave DRA).

### Persona Física (PF) — 13 caracteres
- **4 letras** derivadas del nombre completo (apellido paterno + materno + nombre)
- **6 dígitos** fecha de nacimiento `AAMMDD`
- **3 caracteres** homoclave alfanumérica

Ejemplo: `MAJG800101XYZ` (PF apellidos M-A, J de Jorge, nacido 1 ene 1980).

## Regex de validación

```
PM:  ^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$
PF:  ^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$
```

## Validaciones que aplica este skill

1. **Formato**: regex anterior. Si no matchea, RFC inválido por estructura.

2. **Fecha embebida válida**: los 6 dígitos centrales deben ser fecha real. `970230` no es válido (febrero no tiene 30). `001301` no es válido (mes 13).

3. **Año razonable**:
   - PF: fecha de nacimiento entre 1900-01-01 y hoy. RFC con fecha futura es inválido.
   - PM: fecha de constitución entre 1900-01-01 y hoy.

4. **Palabras inconvenientes prohibidas por SAT**: las primeras 3-4 letras no pueden formar palabras consideradas obscenas, ofensivas o malsonantes. El SAT publica un listado. Las más conocidas:
   ```
   BUEI, BUEY, CACA, CACO, CAGA, CAGO, CAKA, CAKO, COGE, COJA, COJE, COJI,
   COJO, CULO, FETO, GUEY, JOTO, KACA, KACO, KAGA, KAGO, KOGE, KOJO, KAKA,
   KULO, MAME, MAMO, MEAR, MEAS, MEON, MIAR, MION, MOCO, MULA, PEDA, PEDO,
   PENE, PUTA, PUTO, QULO, RATA, RUIN
   ```
   Si las 4 primeras letras forman una de estas, el SAT habría sustituido por una variante (típicamente cambia una letra por X). El RFC original NO existe y debe corregirse.

5. **Caracter `&` y `Ñ`**: válidos en PM (representan personas morales con esos caracteres en razón social). Algunos sistemas los rechazan por error; SAT sí los acepta.

6. **RFCs genéricos** (válidos pero con uso restringido):
   - `XAXX010101000` — público en general nacional. Solo válido con UsoCFDI `S01` y como receptor.
   - `XEXX010101000` — público en general extranjero. Solo válido como receptor con ResidenciaFiscal y NumRegIdTrib.

7. **No verifica homoclave matemáticamente** — el algoritmo del SAT para calcular la homoclave usa una tabla específica y módulo 11. Validar la homoclave requiere consultar la API de validación del SAT (gratuita, pero con rate limit). Este skill marca la homoclave como "estructura válida" pero NO confirma que sea la real del contribuyente.

## Verificación contra SAT (opcional)

El SAT expone un endpoint de validación masiva de RFC: `https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf` (consulta individual por web) y la **API de validación masiva** mediante el aplicativo "Validador de RFC" (descarga lote, requiere FIEL).

Si está disponible la integración, este skill puede:
- Confirmar que el RFC existe en el padrón
- Verificar que está **activo** (no cancelado)
- Detectar si está en el **listado 69-B** del SAT (Empresas que Facturan Operaciones Simuladas — EFOS). **Crítico**: si un cliente o proveedor está en 69-B, las facturas con él pueden ser desconocidas por el SAT.

En modo mock (sin integración), este skill solo aplica las validaciones estructurales 1-6.

## Salida esperada

```json
{
  "rfc_input": "majg800101xyz",
  "rfc_normalizado": "MAJG800101XYZ",
  "tipo": "PF",
  "valido_estructura": true,
  "fecha_embebida": "1980-01-01",
  "es_generico": false,
  "alertas": [],
  "verificacion_sat": {
    "consultada": false,
    "razon": "Integración SAT no configurada — solo validación estructural"
  }
}
```

Si inválido:
```json
{
  "rfc_input": "MAJG891332ABC",
  "valido_estructura": false,
  "errores": [
    "Fecha embebida inválida: el día 32 no existe en el mes 13"
  ]
}
```

## Casos edge

- RFCs con prefijo `XX` que parezcan genéricos pero no lo son: solo los dos publicados arriba son genéricos válidos.
- Sistemas legacy que separan PM en 3+6+3 con guiones (`IBM-970131-DRA`): normalizar quitando separadores antes de validar.
- Personas físicas que cambiaron de nombre legalmente: el RFC NO cambia (las letras derivan del nombre al momento del registro).

## Integración con otros skills

- Antes de invocar `cfdi-emision`, este skill debe correr sobre RFC del emisor y receptor.
- Útil en `compliance-lfpdppp` para validar registros de clientes en avisos de privacidad.
