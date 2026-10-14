# mp_curp_renapo — Validación CURP + consulta RENAPO

MCP server para validar Claves Únicas de Registro de Población (CURP) y opcionalmente consultar el padrón oficial RENAPO. Crítico para verticales que identifican personas físicas por CURP: colegios, salud, migración, RH.

## Filosofía

**La capa estructural (8 de 9 tools) es 100% local y siempre real** — no toca red, valida en microsegundos. Si tu agente puede resolver el problema sin pegarle a RENAPO, no hace falta Playwright ni CAPTCHA.

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
| `curp_consultar_renapo` | read-remoto | Verifica padrón. Mock por default. Cache 90 días. |
| `curp_descargar_constancia_renapo` | read-remoto | PDF oficial. Mock por default. Cache 90 días. |
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
| 2026-10-14 | `GET https://www.gob.mx/curp/` | 200 "Challenge Validation" (Akamai `/_sec/verify`) + `recaptcha/enterprise.js` |

- Estado: **handoff humano**. `curp_consultar_renapo` y
  `curp_descargar_constancia_renapo` devuelven `requiere_humano: true`, la URL,
  los pasos y la CURP prellenada junto con su validación local.
- No hay CAPTCHA solver ni evasión del challenge, por diseño (regla del repo).
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).
- Test live (`-m live`) verifica que el portal siga exigiendo CAPTCHA; si deja
  de hacerlo, revisar si hay endpoint consultable.

## Seguridad

- **PII en bitácora**: las CURPs se **hashean** (SHA-256) antes de loggear. Nunca se persiste la CURP en claro en el audit log.
- **Cache**: las respuestas RENAPO se guardan 90 días bajo la CURP-en-claro como key — viven solo en disco local del usuario, no se transmiten.
- **Pseudo-CURPs**: cuando detecta CURPs `XEXX...` (extranjeros sin CURP definitivo), marca alerta para que el agente no asuma identidad confirmada.

## Verticales que lo consumen

- `colegios-mx`: identificación de alumnos + emisión CFDI colegiaturas
- `salud-mx` (paciente / clínica / consultorio): expedientes médicos NOM-004
- `migracion-extranjeros-mx`: inscripción SAT con pseudo-CURP

## Tests

```bash
.venv/bin/pytest mp_curp_renapo/tests -v
```

58 tests cubren: catálogos (estados, char→num), validación estructural (positivos, negativos, edge cases como 31-feb), derivaciones (fecha/sexo/estado), generación reversa, batch, cliente RENAPO mock + handoff humano, y tools FastMCP end-to-end.
