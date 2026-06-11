# mp_curp_renapo — Validación CURP + consulta RENAPO

MCP server para validar Claves Únicas de Registro de Población (CURP) y opcionalmente consultar el padrón oficial RENAPO. Crítico para verticales que identifican personas físicas por CURP: colegios, salud, migración, RH.

## Filosofía

**La capa estructural (8 de 9 tools) es 100% local y siempre real** — no toca red, valida en microsegundos. Si tu agente puede resolver el problema sin pegarle a RENAPO, no hace falta Playwright ni CAPTCHA.

La capa RENAPO (consulta + descarga de constancia) está en modo mock por default y requiere integración Playwright para modo real. Diseñado así porque RENAPO no expone API pública y meter Playwright + CAPTCHA es una decisión que cada usuario debe tomar.

## Lo que cubre

| Capa | Cobertura | Estado |
|---|---|---|
| Estructural | Regex por posición, dígito verificador, fecha embebida, derivación de sexo/estado/siglo | ✅ Real |
| Pseudo-CURP | Detección de CURPs temporales (XEXX...) para extranjeros | ✅ Real |
| Palabras inconvenientes | Alerta si la CURP no tuvo el reemplazo X de RENAPO | ✅ Real |
| Generación reversa | Construye la CURP esperada desde datos personales | ✅ Real |
| Batch | Validar lotes de hasta 500 CURPs (limpieza de bases) | ✅ Real |
| Consulta padrón | Verifica existencia en RENAPO | 🚧 Mock (Playwright pendiente) |
| Constancia oficial | Descarga PDF | 🚧 Mock (Playwright pendiente) |

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

## Configuración

### Modo mock (default)

Sin envs, todo lo estructural funciona real, y RENAPO devuelve respuestas plausibles derivadas de la propia CURP. La heurística determinística: CURPs cuyo dígito verificador es 4 simulan estado `DUPLICADO`; el resto, `VIGENTE`.

### Modo "real" (estructural real, RENAPO no implementado todavía)

```bash
export CURP_RENAPO_PLAYWRIGHT=1
```

Esto activa el camino que llama a RENAPO. Pero como Playwright + CAPTCHA todavía no están integrados, `consultar_renapo` y `descargar_constancia_renapo` devuelven `not_implemented_error` con guía de qué hace falta.

Para integrar Playwright real necesitas:
1. `pip install playwright && playwright install chromium`
2. Decidir bypass CAPTCHA: servicio externo (2captcha, anti-captcha) o intervención humana
3. Implementar el flujo en `mp_curp_renapo/renapo.py` reemplazando el branch `not_implemented_error`

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

58 tests cubren: catálogos (estados, char→num), validación estructural (positivos, negativos, edge cases como 31-feb), derivaciones (fecha/sexo/estado), generación reversa, batch, cliente RENAPO mock + branch `not_implemented_error`, y tools FastMCP end-to-end.
