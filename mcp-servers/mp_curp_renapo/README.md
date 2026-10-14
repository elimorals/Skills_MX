# mp_curp_renapo — Validación CURP + consulta RENAPO

MCP server para validar Claves Únicas de Registro de Población (CURP) y opcionalmente consultar el padrón oficial RENAPO. Crítico para verticales que identifican personas físicas por CURP: colegios, salud, migración, RH.

## Filosofía

**La capa estructural (7 de 10 tools) es 100% local y siempre real** — no toca red, valida en microsegundos. Si tu agente puede resolver el problema sin pegarle a RENAPO, no hace falta Playwright ni CAPTCHA.

La capa RENAPO (consulta + descarga de constancia) devuelve un **handoff humano**: el portal exige reCAPTCHA Enterprise y un challenge anti-bot, y este MCP no los evade.

## Lo que cubre

| Capa | Cobertura | Estado |
|---|---|---|
| Estructural | Regex por posición, dígito verificador, fecha embebida, derivación de sexo/estado/siglo | ✅ Real |
| Pseudo-CURP | Detección de CURPs temporales (XEXX...) para extranjeros | ✅ Real |
| Palabras inconvenientes | Alerta si la CURP no tuvo el reemplazo X de RENAPO | ✅ Real |
| Generación reversa | Construye la CURP esperada desde datos personales | ✅ Real |
| Batch | Validar lotes de hasta 500 CURPs (limpieza de bases) | ✅ Real |
| Consulta padrón | Verifica existencia en RENAPO | Handoff humano (CAPTCHA) |
| Constancia oficial | Descarga PDF | Handoff humano (CAPTCHA) |

## Tools expuestos

| Tool | Tipo | Descripción |
|---|---|---|
| `curp_validar_estructura` | read-local | Validación full con regex + dígito + fecha |
| `curp_derivar_fecha_nacimiento` | read-local | Extrae fecha de chars 5-10 + siglo del char 17 |
| `curp_derivar_sexo` | read-local | H o M del char 11 |
| `curp_derivar_estado` | read-local | Código y nombre del estado de los chars 12-13 |
| `curp_validar_lote` | read-local | Hasta 500 CURPs en bloque |
| `curp_generar_desde_datos` | read-local | Genera la CURP esperada desde apellidos + nombre + fecha + sexo + estado |
| `curp_consultar_renapo` | read-remoto | Verifica padrón por CURP. Handoff humano (solver opt-in, ver Estado real). |
| `curp_consultar_renapo_por_datos` | read-remoto | Busca la CURP por nombre, apellidos, fecha, sexo y entidad. Handoff humano; nunca se cachea. |
| `curp_descargar_constancia_renapo` | read-remoto | PDF oficial. Handoff humano. |
| `curp_listar_catalogos` | read-offline | Discovery de estados + códigos de sexo |

## Anatomía CURP (referencia rápida)

```
AABB CCDDEE F GGGGG HH I
├──┘ ├────┘ │ │ ├─┘ │ │
│    │      │ │ │   │ └── Dígito verificador
│    │      │ │ │   └── Char homonimia (digit=1900s, letter=2000s)
│    │      │ │ └── 3 consonantes interiores (paterno, materno, nombre)
│    │      │ └── 2 letras código estado
│    │      └── H o M
│    └── Fecha AAMMDD
└── 4 letras: 1ra apellido paterno, 1ra vocal interior paterno, 1ra materno, 1ra nombre
```

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://www.gob.mx/curp/` (httpx/curl) | 200 "Challenge Validation" (Akamai, proveedor `crypto`: proof-of-work en JS) |
| 2026-10-14 | `GET https://www.gob.mx/v1/renapoCURP/consulta` (httpx/curl) | 200 mismo challenge de Akamai: la API también queda detrás |
| 2026-10-14 | `GET https://consultas.curp.gob.mx/CurpSP/` | 302 a `www.gob.mx/curp/` (mismo challenge) |
| 2026-10-14 | `www.gob.mx/curp/` en navegador real + bundle `assets/tramite-curp-*.js` | Contrato de la consulta (abajo); sin enviar datos de personas |

Contrato descubierto (bundle Ember del portal):

- `POST https://www.gob.mx/v1/renapoCURP/consulta`, JSON.
  - Por CURP: `{"curp", "tipoBusqueda": "curp", "ip": "127.0.0.1", "token"}`.
  - Por datos: `{"nombres", "primerApellido", "segundoApellido", "diaNacimiento",
    "mesNacimiento", "selectedYear", "fechaNacimiento": "dd/mm/aaaa", "sexo": H|M|X,
    "claveEntidad", "tipoBusqueda": "datos", "ip", "token"}` (texto en mayúsculas sin acentos).
  - Respuesta: `{"codigo": "01" (éxito) | "02".."13" | "180001"/"190001", "mensaje", "registros": [{curp, nombres,
    primerApellido, segundoApellido, sexo, fechaNacimiento, nacionalidad, entidad, statusCurp,
    docProbatorio, datosDocProbatorio{anioReg, foja, tomo, libro, numActa, crip, entidadRegistro, municipioRegistro, ...}}]}`.
- reCAPTCHA **Enterprise** score-based: sitekey `6Lfi0jcpAAAAAPfBiQkGzQR3gv8mDRkqPDHAy8hS`,
  action **`CONSULTA`** (la página también ejecuta `CARGA` al abrir); el token va en el body como `token`.

Estado:

- **Solver apagado** (default): **handoff humano**, igual que antes. `curp_consultar_renapo`,
  `curp_consultar_renapo_por_datos` y `curp_descargar_constancia_renapo` devuelven
  `requiere_humano: true`, la URL, los pasos y los datos prellenados.
- **Solver opt-in** (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`): código de
  consulta real implementado (token Enterprise → POST → parseo; token rechazado → reintento con
  `con_token`, luego `UpstreamError`), probado solo con respx. **En la práctica sigue en handoff**:
  hace un GET previo y, si aparece el challenge de Akamai (hoy siempre), devuelve el handoff con
  `bloqueo_antibot: "akamai"` sin gastar captcha. No se agrega stealth, proxies ni generación de
  sensores Akamai. Si Akamai deja de estar delante, la consulta real se activa sola.
- **Sin validar en vivo**: falta llave de 2captcha y, sobre todo, Akamai bloquea httpx.
- La constancia PDF (`consultas.curp.gob.mx/CurpSP/pdfgobmx`) sigue en handoff.
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).
- Tests live (`-m live`): portal sigue exigiendo captcha; y `test_live_solver_renapo`
  (requiere `TWOCAPTCHA_API_KEY` y `CURP_LIVE` con la CURP propia).

## Seguridad

- **PII en bitácora**: las CURPs se **hashean** (SHA-256) antes de loggear. Nunca se persiste la CURP en claro en el audit log.
- **Cache**: solo las respuestas mock se guardan (90 días). Las respuestas reales de RENAPO **no se cachean** (datos personales de terceros); la consulta por datos tampoco. La bitácora de la búsqueda por datos guarda solo un hash.
- **Aviso de privacidad**: toda respuesta real incluye `aviso_privacidad` (uso con base legal LFPDPPP).
- **Pseudo-CURPs**: cuando detecta CURPs `XEXX...` (extranjeros sin CURP definitivo), marca alerta para que el agente no asuma identidad confirmada.

## Verticales que lo consumen

- `colegios-mx`: identificación de alumnos + emisión CFDI colegiaturas
- `salud-mx` (paciente / clínica / consultorio): expedientes médicos NOM-004
- `migracion-extranjeros-mx`: inscripción SAT con pseudo-CURP

## Tests

```bash
.venv/bin/pytest mp_curp_renapo/tests -v
```

68 tests cubren: catálogos (estados, char→num), validación estructural (positivos, negativos, edge cases como 31-feb), derivaciones (fecha/sexo/estado), generación reversa, batch, cliente RENAPO mock + handoff humano + solver opt-in (respx), y tools FastMCP end-to-end.
