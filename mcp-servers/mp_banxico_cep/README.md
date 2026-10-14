# mp_banxico_cep — CEP + CLABE (conciliación bancaria SPEI)

MCP server para cerrar el ciclo de cobranza: **cliente paga SPEI → este MCP confirma el pago contra Banxico → el flujo marca el CFDI como cobrado**. Cubre validación CLABE local + consulta CEP (Constancia de Pago Electrónico).

## Filosofía: capa local + capa Banxico real

Las **4 herramientas locales** (CLABE, clave de rastreo, catálogo) no usan red.
Las **4 herramientas remotas** consultan el portal CEP de Banxico con `httpx`
(sin Playwright). Mock solo con `PLUGINS_MX_MOCK=1` (respuestas `simulated: true`).

## Tools expuestos

| Tool | Capa | Descripción |
|---|---|---|
| `banxico_cep_validar_clabe` | Local-real | 18 dígitos + dígito de control con pesos cíclicos 3,7,1 |
| `banxico_cep_decodificar_clabe` | Local-real | Extrae banco / plaza / cuenta interna |
| `banxico_cep_parsear_clave_rastreo` | Local-real | Heurística por prefijo (MBAN→BBVA, MERPAGO→MP, etc.) |
| `banxico_cep_lookup_banco` | Local-real | Código 3 dígitos → nombre |
| `banxico_cep_generar_cep` | Remoto / mock | Datos completos + URL del PDF (cache 90 días) |
| `banxico_cep_validar_cep` | Remoto / mock | Check liviano de existencia (cache 30 días) |
| `banxico_cep_descargar_pdf` | Remoto / mock | PDF firmado por Banxico |
| `banxico_cep_consultar_pago_por_clave` | Remoto / mock | Variante con solo clave (en real exige más datos) |
| `banxico_cep_listar_bancos` | Catálogo | ~80 bancos + casas de bolsa + fintechs |
| `banxico_cep_listar_catalogos` | Catálogo | Tipos operación SPEI + estados CEP |

## Anatomía CLABE (referencia rápida)

```
BBB PPP CCCCCCCCCCC D
├─┘ ├─┘ ├─────────┘ │
│   │   │           └── Dígito de control (módulo 10, pesos cíclicos 3,7,1)
│   │   └── Cuenta interna del banco (11 dígitos)
│   └── Código de plaza (3 dígitos)
└── Código de banco (3 dígitos) — ver catálogo
```

Ejemplos de códigos de banco más usados:
- `002` Banamex • `012` BBVA México • `014` Santander • `021` HSBC
- `044` Scotiabank • `058` Banregio • `072` Banorte
- `127` Banco Azteca • `137` BanCoppel • `646` STP • `722` Mercado Pago

## Flujo de conciliación típico

```
1. cfdi_emision genera CFDI con clave PUE/PPD
2. Cliente paga vía SPEI (puede ser días después si era PPD)
3. Cliente manda clave de rastreo por WhatsApp ("MBAN0100123456789012")
4. Agente llama banxico_cep_parsear_clave_rastreo → identifica BBVA emisor
5. Agente pide al cliente fecha + monto exacto (o lo lee del CFDI)
6. Agente llama banxico_cep_generar_cep → recibe constancia oficial
7. Si el monto en el CEP coincide con el CFDI → marcar cobrado en bitácora
8. Si era PPD → emitir CFDI de Pagos (REP)
```

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://www.banxico.org.mx/cep/` | 200, CAPTCHA oculto (`captcha=c` precargado por el portal) |
| 2026-10-14 | `GET https://www.banxico.org.mx/cep/instituciones.do?fecha=10-10-2026` | 200 JSON, catálogo SPEI |
| 2026-10-14 | `POST https://www.banxico.org.mx/cep/valida.do` (tipoConsulta=0, clave inexistente) | 200, "Operación no encontrada" |
| 2026-10-14 | `POST .../valida.do` (SPEI de 2019) | 200, "[BE] No se encontró ningún pago" |

- Estado: **real validado** para consulta de estado y respuestas "no encontrado".
  El camino de un SPEI existente (`descarga.do?formato=XML|PDF` y parseo de
  `SPEI_Tercero`) está implementado pero **no validado en vivo**: no hay una
  clave de rastreo pública de prueba. Validar con un SPEI propio.
- Endpoints (leídos de `js/cep-min.js`): `instituciones.do` (JSON), `valida.do`
  (form), `descarga.do`. Ver `spei.py`.
- CAPTCHA: si el portal vuelve a mostrar la imagen de seguridad, las tools
  devuelven un handoff humano (`requiere_humano: true`, URL, pasos y campos
  prellenados). Nunca se resuelve el CAPTCHA.
- Errores del portal → `UpstreamError`. Nunca hay fallback a mock.
- `generar_cep`/`descargar_pdf` exigen `cuenta_beneficiaria`; `validar_cep`
  exige `fecha_operacion`, `banco_emisor` y `banco_receptor`.
- Horario de consulta del portal: 09:30–23:00.

Test live: `PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_banxico_cep -m live`.

## Seguridad

- **PII en bitácora**: las claves de rastreo SPEI se **hashean** (SHA-256) antes de loggear. Nunca se persiste en claro.
- **Cuentas bancarias**: en las respuestas las cuentas se devuelven enmascaradas (`**** XXXX` últimos 4).
- **Cache**: respuestas CEP viven solo en disco local del usuario.

## Verticales que lo consumen

- `core-mexico` — universal, todos los verticales tienen cobros SPEI
- `freelancers-mx` — `cobranza-seguimiento` + `cierre-fiscal-mensual`
- `arrendador-residencial-mx` — `cobranza-renta`, `verificar-cobros-renta-mes`
- `colegios-mx` — confirmar pagos de colegiaturas mensuales

## Tests

```bash
.venv/bin/pytest mp_banxico_cep/tests -v
```

53 tests cubren: catálogos (7 bancos top + fintechs), algoritmo CLABE (positivos, negativos, banco desconocido, normalización), parseo claves rastreo (BBVA, MP, STP, prefijos desconocidos), cliente CEP mock (determinismo, cache, hashing de claves) + tools FastMCP end-to-end.
