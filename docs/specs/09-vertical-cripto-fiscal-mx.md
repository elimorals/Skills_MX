---
spec: "vertical-cripto-fiscal-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [280, 450]
prioridad: "tier-1"
---

# Spec 09 — Vertical `cripto-fiscal-mx`

## 1. Propósito

Plugin para personas físicas mexicanas que **operan criptomonedas** (trading, holding, DeFi, NFTs). Mercado: ~5M+ mexicanos con wallets cripto (Statista 2024), de los cuales solo ~10% declara fiscalmente (gap masivo).

Cobertura urgente porque **CARF (Common Reporting Framework de OCDE) entra en vigor 2026**: TODO exchange con clientes mexicanos reportará saldos y operaciones al SAT. El gap "no declaro porque SAT no se entera" desaparece en 2026-2027.

## 2. Contexto y por qué es novedoso

- **Sin vertical cripto en repo**: hay `mp_bitso` pero solo expone API de un exchange — falta la capa fiscal completa
- **Reglas SAT 2026 ya vigentes**:
  - ISR sobre ganancia en venta cripto (Art. 119 LISR, enajenación de bienes)
  - Intercambio cripto-cripto = **permuta gravable** (al cambiar BTC por USDC, si BTC subió de valor, hay ganancia)
  - IVA 16% sobre comisión del exchange (Bitso emite CFDI por servicio)
  - Holdings reportables: > $200k MXN en Bitso = reporte automático al SAT desde 2021 (Ley Fintech)
- **CARF**: depósitos > $50k USD individuales activan reporte. Saldos > $200k MXN reportados anuales.
- **DeFi**: zona gris regulatoria — SAT exige tributar pero sin guías específicas (responsabilidad del contribuyente)

## 3. Alcance

**Dentro:**
- Tracking de operaciones por exchange (Bitso, Bitfinex, Binance, Coinbase, Kraken)
- Cálculo costo base por método FIFO (default SAT) — alternativa LIFO/promedio si justificado
- Permuta cripto-cripto (gravable)
- Staking + lending DeFi (rendimientos = ingreso por intereses)
- NFTs (compra-venta = enajenación bienes)
- Airdrops (ingreso al valor de mercado del día de recepción)
- Wallets self-custodied (descarga via API blockchain explorer)
- Cálculo ISR anual + provisional mensual si aplica
- Exposición al CARF 2026 — qué saldos serán reportados

**Fuera (decisión deliberada):**
- Mining (otra clasificación fiscal — actividad empresarial)
- Empresas (PM) operando cripto (otra escala)
- DeFi avanzado: yield farming complejo, LP tokens con impermanent loss (consultar contador)
- Stablecoins peg (USDC, USDT) — gravable cuando se intercambia
- Tax-loss harvesting agresivo (estrategias borderline)

## 4. Inputs / outputs / schemas

### Operación cripto

```python
class OperacionCripto(BaseModel):
    fecha_hora: datetime
    exchange: Literal["bitso", "binance", "coinbase", "kraken", "self_wallet"]
    tipo: Literal["compra", "venta", "permuta", "stake_recompensa", "airdrop", "transferencia_in", "transferencia_out", "lending_interes"]
    activo_dado: str | None     # ej. "BTC", "MXN"
    cantidad_dada: Decimal
    activo_recibido: str
    cantidad_recibida: Decimal
    valor_mxn_dia: Decimal      # valor en MXN para fines fiscales del activo principal el día
    fee_mxn: Decimal
    txid: str | None
    notas: str | None
```

### Cálculo anual

```python
class ResumenAnualCripto(BaseModel):
    rfc_hash: str
    ejercicio: int
    operaciones_count: int
    ingresos_acumulables_mxn: Decimal      # ganancias por venta + airdrops + staking
    gastos_deducibles_mxn: Decimal         # fees + comisiones
    utilidad_gravable_mxn: Decimal
    isr_estimado_mxn: Decimal
    saldos_31_dic_mxn: dict[str, Decimal]  # por exchange
    saldos_reportables_carf: list[str]     # exchanges que reportarán al SAT
    metodo_aplicado: Literal["FIFO", "promedio_ponderado"]
    vigencia_validada: bool
```

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `dashboard-cripto-portafolio` | Estado actual portafolio + ganancia/pérdida realizada y latente |
| `importar-operaciones-exchange` | CSV/API de Bitso + otros |
| `calcular-costo-base-fifo` | FIFO automático |
| `permuta-cripto-cripto-gravable` | Detectar intercambios gravables |
| `staking-y-airdrops-ingreso` | Tratamiento de rendimientos |
| `nft-enajenacion-bienes` | Operaciones NFT |
| `tracking-wallets-self-custody` | Blockchain explorer |
| `riesgo-carf-2026` | Qué saldos serán reportados |
| `isr-anual-cripto` | Cálculo final |
| `documento-pruebas-sat` | Generar reporte respaldo para SAT |

## 6. Comandos (5)

```
/cripto:dashboard
/cripto:importar
/cripto:calcular
/cripto:declarar
/cripto:riesgo-carf
```

## 7. Workflow

`workflow-declaracion-anual-cripto.md`:
1. Importar operaciones de todos los exchanges del año
2. Importar saldos finales 31-dic
3. Calcular costo base FIFO por cada activo
4. Identificar permutas gravables
5. Sumar ingresos por staking/airdrops/lending
6. Calcular utilidad gravable
7. Aplicar tarifa Art. 96 LISR (forma parte del ingreso PF anual)
8. Generar reporte para incluir en declaración anual
9. Documentar respaldo CSV exportable

## 8. Casos edge

| Caso | Acción |
|---|---|
| Cliente con saldos > $200k MXN en Bitso | Saldo será reportado al SAT — sí declarar |
| Permuta cripto-cripto en swap DEX | Gravable — calcular valor MXN del día |
| Stake con recompensa diaria pequeña | Sumar a ingreso del año — granular si > $5k MXN |
| Airdrop sin liquidez (no mercado) | Reportar al valor de mercado cuando se vuelve líquido |
| Self-custody wallet sin historial | Reconstruir con blockchain explorer (etherscan, etc.) |
| NFT comprado en ETH y vendido en USD | Calcular ganancia en MXN |
| Hard fork (BCH del BTC en 2017) | Recibido = ingreso al valor de mercado del día |
| Wallet hackeada / cripto robada | Pérdida deducible si se documenta (denuncia MP) |
| Trading con > $5M anuales en cripto | Considerar reclasificación a actividad empresarial 612 |
| Mexicano viviendo fuera del país | Validar régimen residencia fiscal |

## 9. Dependencias

- **MCPs**: `mp_bitso` (ya existe), `mp_banxico` (TC USD/MXN diario para valuación)
- **MCPs nuevos sugeridos** (V2):
  - `mp_binance_account` — API Binance (existe, requiere onboard)
  - `mp_coinbase_account` — API Coinbase
  - `mp_etherscan_explorer` — blockchain ETH self-custody
  - `mp_btc_explorer` — blockchain BTC
- **Skills `_shared/`**: cfdi-emision, mxn-formato, compliance-lfpdppp

## 10. Criterios de aceptación

- [ ] Plugin con 10 skills + 5 commands + workflow
- [ ] Importar CSV Bitso oficial sin errores
- [ ] Calcular FIFO correcto con > 100 operaciones
- [ ] Detectar 100% de permutas gravables
- [ ] Generar reporte SAT compatible (Excel/PDF)
- [ ] Documentación clara de cuáles operaciones son gravables vs exentas
- [ ] Tests con 10 fixtures (diferentes patrones)
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold + plugin.json**: 5-10h
- **Importadores CSV Bitso/Binance/Coinbase**: 30-50h
- **Cálculo FIFO automatizado**: 25-40h
- **Tratamiento permutas + staking + airdrops + NFTs**: 40-60h
- **TC histórico MXN/USD para valuación**: 15-25h
- **Self-custody wallet tracking (blockchain explorer)**: 30-50h
- **Cálculo CARF 2026 riesgo de reporte**: 20-30h
- **Generación reporte SAT presentable**: 20-30h
- **Tests + 10 fixtures**: 40-60h
- **Docs + guía**: 25-40h
- **Validación con contador especializado cripto**: 5-10h coordinación
- **TOTAL**: **255-405 horas** (~6-10 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Reglas cripto cambian en RMF | **Alta (anual)** | Crítico | Catálogo separado + revisión enero |
| TC histórico MXN incompleto | Media | Alto | `mp_banxico` series histórica completa |
| Volatilidad alta = errar valor | Media | Medio | Usar TC y precio del día (criterio FIFO oficial) |
| Cliente con auditoría SAT cripto | Alta | Crítico | Documentación exhaustiva + papel de trabajo |
| Hard forks no reconocidos por SAT | Baja | Medio | Documentar caso a caso |
| CARF 2026 reglas cambien | Media | Alto | Diseño modular |

## 13. Decisiones pendientes

- [ ] ¿Método FIFO obligatorio o permitir LIFO/promedio?
- [ ] ¿DeFi avanzado (LP, yield farming) en V1 o V2?
- [ ] ¿Integración Binance/Coinbase via API o solo CSV?
- [ ] ¿Pricing: $599 MXN/año por usuario o suscripción mensual?
- [ ] ¿Generar declaración anual lista para DeclaraSAT o solo PDF reporte?

## 14. Plan de implementación

### Fase 1: Foundation (15-25h)
1. plugin.json + README
2. Catálogo activos cripto principales (BTC, ETH, USDC, USDT, etc.)
3. Estructura base

### Fase 2: Importadores (30-50h)
1. CSV Bitso oficial
2. CSV Binance / Coinbase
3. Normalizador a schema común `OperacionCripto`

### Fase 3: Cálculos fiscales (60-100h)
1. FIFO automatizado
2. Permutas gravables
3. Staking + airdrops
4. NFTs
5. Self-custody con explorer

### Fase 4: Reportes (40-60h)
1. dashboard-cripto-portafolio
2. isr-anual-cripto
3. documento-pruebas-sat
4. riesgo-carf-2026

### Fase 5: Tests + docs (50-80h)

## 15. Links

- [Bitso - Cómo tributan criptos en México](https://blog.bitso.com/es-mx/blog/como-tributan-criptomonedas-mexico)
- [SAT - Guía cripto 2026](https://contarito.com.mx/blog/impuestos-criptomonedas-mexico-2026/)
- [BeInCrypto - Impuestos cripto SAT](https://es.beincrypto.com/aprende/impuestos-criptomonedas-mexico-guia-completa-sat/)
- [CARF (OCDE) - Common Reporting Framework Crypto](https://www.oecd.org/tax/exchange-of-tax-information/crypto-asset-reporting-framework-and-amendments-to-the-common-reporting-standard.htm)
- [Ley Fintech Art. 17 - reportes ITF](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf)
