# mp_no_antecedentes_penales_mx

MCP para verificación de Constancia de No Antecedentes Penales. Top 15 #14.

v1 cubre **CDMX + EdoMex** (40% del mercado nacional). Otros estados (Jalisco,
Nuevo León, Puebla, Querétaro, Guanajuato) pendientes de discovery.

## Por qué importa

- **Universo**: RRHH (contratación masiva), conductor-plataforma (Uber/DiDi
  exigen no antecedentes), didi-partners, security clearance, leasing.
- **Caso de uso RRHH**: candidato sube PDF de su constancia → empresa extrae
  folio + CURP → MCP verifica autenticidad y vigencia.

## Importante

Este MCP **NO emite** la constancia — eso requiere:
- CDMX: cuenta Llave CDMX SSO del propio ciudadano + $77 MXN
- EdoMex: tramite digital + $87 MXN

El MCP **verifica autenticidad** de una constancia ya emitida.

## Tools

### `noantecedentes_verificar_constancia(curp, folio, entidad)`
Verifica una constancia. Devuelve estado, vigencia, si tiene antecedentes.

### `noantecedentes_verificar_apto(curp, folio, entidad)`
Decisión binaria RRHH. Devuelve `apto_para_contratacion: bool` + razón.

## Estados de la constancia

| Estado | Acción |
|---|---|
| `VIGENTE` (sin antecedentes) | Apto ✅ |
| `VIGENTE` (con antecedentes) | Decisión RRHH/legal — la constancia es real, pero tiene flags |
| `EXPIRADA` | Solicitar nueva (vigencia típica 6 meses) |
| `ANULADA` | NO contratar — investigar |
| `NO_ENCONTRADA` | Folio falso o inexistente — ALERTA fraude |

## Configuración

| Env var | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | unset | `1` = mock determinístico (`simulated: true`). |

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `https://noantecedentes.cdmx.gob.mx/` | Redirige a la ficha del trámite 872 en cdmx.gob.mx; sin verificador público por folio/CURP |
| 2026-10-14 | `https://carta-no-antecedentes.edomex.gob.mx/verificar` | DNS no resuelve (`ERR_NAME_NOT_RESOLVED`) |

- Estado: **handoff humano** (sin verificador público consultable).
- En modo real las tools devuelven `requiere_humano: true`, `estado: "DESCONOCIDO"`,
  `es_apta_para_contratacion: null` y pasos para validar el PDF (QR, firma digital,
  confirmación con la fiscalía). Nunca se inventa un estado.
- Test live (`-k live`) avisa cuando el verificador EdoMex vuelva a resolver DNS.

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_no_antecedentes_penales_mx/tests -v
```
