# mp_banxico_cep — CEP + CLABE (conciliación bancaria SPEI)

MCP server para cerrar el ciclo de cobranza: **cliente paga SPEI → este MCP confirma el pago contra Banxico → el flujo marca el CFDI como cobrado**. Cubre validación CLABE local + consulta CEP (Constancia de Pago Electrónico).

## Filosofía: capa local 100% real, capa Banxico mock-friendly

Igual que `mp_curp_renapo`, la mayor parte del valor está en las **4 herramientas locales** que validan CLABE, parsean claves de rastreo y miran el catálogo de bancos. Estas son siempre reales — sin red, sin credenciales, instantáneas.

Las **4 herramientas remotas** (generar CEP, validar CEP, descargar PDF, consultar pago) arrancan en **mock determinístico** porque Banxico no tiene API REST. Para modo real hace falta Playwright + parseo HTML (todavía no implementado, ver "Integración real" abajo).

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

## Configuración

### Modo mock (default)

Sin envs, las 4 tools locales funcionan reales y las 4 remotas devuelven respuestas plausibles **determinísticas** (mismo input → mismo output). Útil para desarrollo, demos y tests del flujo de conciliación sin tocar Banxico.

Heurística: validar_cep usa el primer hex char del SHA-256 de la clave — par = existe, impar = no encontrado. Predecible y testeable.

### Integración real (todavía no implementada)

```bash
export BANXICO_CEP_PLAYWRIGHT=1
```

Esto activa el camino real. Pero las tools remotas devolverán `not_implemented_error` con guía. Para integrar:

1. `pip install playwright && playwright install chromium`
2. Implementar el flujo POST a `https://www.banxico.org.mx/cep/` con los datos del SPEI
3. Parsear el HTML de respuesta — extraer hora, ordenante enmascarado, beneficiario, monto, etc.
4. Descargar el PDF firmado si hace falta
5. Reemplazar los `_NotImplementedError` en `client.py` con la lógica Playwright

Las 4 tools locales no requieren nada de esto.

## Seguridad

- **PII en bitácora**: las claves de rastreo SPEI se **hashean** (SHA-256) antes de loggear. Nunca se persiste en claro.
- **Cuentas bancarias**: en las respuestas (real y mock) las cuentas se devuelven enmascaradas (`**** XXXX` últimos 4).
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
