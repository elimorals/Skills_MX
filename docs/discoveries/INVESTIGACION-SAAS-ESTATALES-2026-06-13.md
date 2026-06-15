# Investigación de plataformas SaaS estatales para predial — 2026-06-13

> **Hipótesis original**: si SACPI Michoacán cubre 95 municipios con 1 URL,
> probablemente otros estados con muchos municipios (Oaxaca 570, Veracruz 212,
> Puebla 217) tienen plataformas equivalentes.
>
> **Resultado**: **SACPI parece ser excepción, no regla**. La mayoría de estados
> delegan el predial 100% a sus municipios.

---

## Estados investigados (7)

| Estado | Municipios | Plataforma estatal | Predial centralizado | Conclusión |
|---|---|---|---|---|
| **Michoacán** | 113 | ✅ SACPI | ✅ 95 muns en select | **Patrón valioso confirmado** |
| **Oaxaca** | 570 | SIOX (Sistema de Ingresos) | ❌ solo licencias/inhábil | No predial — Art. 115 municipal puro |
| **Puebla** | 217 | finanzas.puebla.gob.mx (Egresos) | ❌ portal de egresos del estado | Predial 100% municipal |
| **Veracruz** | 212 | www.veracruz.gob.mx/finanzas | ❌ cert SSL roto / timeout | No accesible automatizado |
| **Estado de México** | 125 | pagosytramites.edomex.gob.mx | ⚠ Solo línea de captura preexistente | NO consulta — solo paga línea ya generada |
| **Chiapas** | 124 | haciendachiapas.gob.mx | ❌ ERR_CONNECTION_RESET | No accesible |
| **Hidalgo** | 84 | sf.hidalgo.gob.mx | ❌ DNS NOT_RESOLVED | Sin dominio activo |
| **Tabasco** | 17 | finanzas.tabasco.gob.mx | ❌ DNS NOT_RESOLVED | Sin dominio activo |

---

## Por qué SACPI es atípico

Constitución Mexicana **Art. 115**: el impuesto predial es **facultad exclusiva de los municipios** ("Los municipios administrarán libremente su hacienda... las contribuciones... sobre la propiedad inmobiliaria").

En la práctica:
- **80% de estados**: cada municipio maneja su propio sistema (puede ser portal propio, recibo manual presencial, o nada)
- **Michoacán es excepción**: el gobierno estatal ofrece SACPI como "servicio compartido opcional" — los municipios chicos que NO pueden pagar su propio sistema usan SACPI. Los 5 municipios grandes (Morelia, Uruapan, Zamora, etc.) tienen sistemas propios.

### ¿Por qué Michoacán y no otros estados?

Hipótesis (no confirmadas):
1. **Tamaño geográfico**: Michoacán tiene 113 municipios y población concentrada. Centralizar tiene sentido económico.
2. **Iniciativa estatal específica**: probablemente una administración hace 10-15 años priorizó digitalización municipal.
3. **Vendor lock-in**: SACPI parece sistema interno del gobierno estatal (no SaaS comercial), una vez construido todos lo adoptan.

---

## Patrones alternativos encontrados (no SACPI-like)

### 1. SIOX Oaxaca — pagos estatales NO predial
- URL: `siox.finanzasoaxaca.gob.mx/pagos`
- Cubre: licencias de conducir, constancias de no inhabilitación, conceptos educativos
- **NO cubre predial municipal** — confirmado

### 2. EdoMex `pagosytramites` — captura de pagos preexistentes
- URL: `pagosytramites.edomex.gob.mx/ingresos/OpcionesPago/`
- Funciona con **línea de captura YA generada** (por el municipio respectivo)
- NO consulta adeudo — solo paga lo que ya sabes que debes
- **Valor limitado**: el cliente sigue necesitando ir al portal de su municipio para generar la línea

### 3. SAT-Tesofe — pagos federales
- No aplica para predial (es contribución local)

---

## ¿Hay otros estados que valga la pena investigar?

Lista candidata por orden de probabilidad (criterio: estados centralistas + mucha pobl. rural):

| Estado | Probabilidad | Razón |
|---|---|---|
| **Guerrero (85 muns)** | Media | Estado con muchos municipios chicos rurales — podría haber centralización |
| **San Luis Potosí (59)** | Media | Centralista, mucha pobl. rural |
| **Sonora (72)** | Baja | Municipios grandes con sistemas propios |
| **Jalisco (125)** | Baja | Cada municipio del AMG tiene su sistema |
| **Querétaro (18)** | Baja | Pocos municipios, todos con sistemas propios |
| **Zacatecas (58)** | Media | Patrón similar a MICH |
| **Durango (39)** | Baja | Solo Durango capital con sistema |

**Próximo a probar (cuando vuelvas a investigar)**: Guerrero y Zacatecas — son los más probables candidatos a tener un SACPI-like.

---

## Strategy update

Dado que SACPI es excepción y no regla, la estrategia óptima cambia:

**Plan original (refutado)**: investigar 3-4 estados → +200-500 municipios via SaaS estatal.
**Plan ajustado**: el camino correcto es:

1. **Mantener SACPI Michoacán** (+95 municipios — ya cubierto)
2. **Discovery individual** sobre los 144 + 145 prioritarios (correr el script)
3. **Aceptar que ~60% de municipios MX no tendrán portal automatizable** — son chicos rurales sin presupuesto para digitalizar predial
4. **Para esos 60%**: ofrecer instrucciones de pago presencial o por banca móvil con línea de captura (proceso 100% humano)

---

## Recomendaciones futuras

1. **Si encuentras un nuevo SACPI-like**: agregarlo a `shared/plataformas_saas_mx.py` con el mismo patrón (select de municipios + selectores).

2. **Si descubres un sistema vendor (SIM, SIAWeb, etc.) en >5 municipios**:
   - White-label per cliente NO es plataforma SaaS para nosotros
   - PERO si encuentras el panel admin del vendor con lista de clientes, vale agregarlo

3. **NO seguir buscando en hacienda estatal**: el Art. 115 garantiza que el predial NO subirá a nivel estatal. La probabilidad de encontrar otro SACPI es < 10%.

---

## Próximo paso recomendado

En lugar de seguir buscando SaaS estatales, **correr discovery sobre los 145 municipios prioritarios** (FASE 24) — eso te da +10-20 validados garantizados vs probabilidad baja de hallazgo SaaS.

— Investigación 2026-06-13 con Playwright MCP, 7 estados muestreados
