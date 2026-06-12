---
spec: "vertical-importadores-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elías Rashid Morales Mendoza"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [400, 700]
prioridad: "tier-1"
---

# Spec 12 — Vertical `importadores-mx`

## 1. Propósito

Plugin para PyMEs y comerciantes mexicanos que **importan mercancía** del extranjero (China, USA, Asia general). Mercado: ~50k importadores activos con padrón vigente.

Cubre el ciclo completo:
- Cotización pre-importación (cálculo de costos con IGI + IVA + DTA + prevalidación)
- Selección de agente aduanal + INCOTERMS
- Pedimento + clasificación arancelaria
- IMMEX (programa de importación temporal — exenta IVA si exporta producto terminado)
- Pago de impuestos vía banca electrónica + acreditación IVA en CFDI
- Tracking de embarques + customs clearance
- Compliance con padrón importadores SAT

## 2. Contexto y por qué es novedoso

- **Sin vertical de comercio internacional**: `ecommerce-mx` cubre comercio digital (ML, Shopify, Amazon MX) pero NO importación física
- **Reglas Generales de Comercio Exterior 2026** publicadas en DOF 27 dic 2025
- **Padrón Importadores**: registro obligatorio en SAT (Art. 59 fr. IV Ley Aduanera)
- **IMMEX** (Industria Manufacturera Maquiladora y de Servicios de Exportación): programa para importar temporalmente sin IVA si reexportas
- **Pedimento**: documento aduanal único con campos formato fijo (clave A1, F4, V1, etc.)
- **INCOTERMS 2020** vigentes: FOB, CIF, EXW, DDP, etc. — cambian quién paga qué
- **Aranceles cambian frecuentemente**: TIGIE (Tarifa de Importación y Exportación) — depende fracción arancelaria

## 3. Alcance

**Dentro:**
- Cotizador pre-importación: producto + país origen + valor → IGI + IVA + DTA + total
- Catálogo TIGIE básico (top 200 fracciones comunes)
- Selector de agente aduanal del padrón
- Cálculo INCOTERMS (FOB/CIF/CFR/EXW/DDP) con desglose
- Tracking de pedimentos pendientes
- Cumplimiento IMMEX (si aplica): control de inventario en/sale
- Acreditación IVA en CFDI de proveedor extranjero (mediante pedimento)
- Compliance padrón importadores SAT (renovación + sectoriales)
- Reportes mensuales: importaciones realizadas, IVA acreditado

**Fuera (decisión deliberada):**
- Exportación (espejo, vertical aparte)
- Clasificación arancelaria automática completa (requiere expertise — usar agente aduanal)
- Logística internacional (FCL/LCL, freight forwarders) — usar 3PL
- T-MEC reglas de origen (caso especializado — abogado comercial)
- Importación de armas, productos controlados (regulación específica SEDENA)

## 4. Inputs / outputs / schemas

### Setup importador

```python
class ImportadorPerfil(BaseModel):
    rfc: str
    razon_social: str
    padron_importadores: bool
    padron_importadores_sectorial: list[str]  # ej. ["acero", "textiles"]
    immex_certificado: bool
    immex_modalidad: Literal["servicios", "manufactura", "albergue"] | None
    immex_numero_programa: str | None
    agente_aduanal_default_rfc: str | None
```

### Cotización pre-importación

```python
class CotizacionImportacion(BaseModel):
    producto: str
    fraccion_arancelaria: str       # 8 dígitos TIGIE
    pais_origen: str
    valor_factura_proveedor_usd: Decimal
    incoterm: Literal["EXW", "FOB", "CFR", "CIF", "DDP", "DAP"]
    peso_kg: Decimal
    flete_internacional_usd: Decimal
    seguro_usd: Decimal | None
    incrementables_otros_usd: Decimal

    # Cálculos resultado
    valor_aduana_usd: Decimal       # base para IGI
    igi_porcentaje: Decimal         # de TIGIE
    igi_usd: Decimal
    iva_16_pct_usd: Decimal
    dta_usd: Decimal                # Derecho de Trámite Aduanero
    prevalidacion_usd: Decimal
    total_impuestos_usd: Decimal
    total_costo_landing_usd: Decimal
    total_costo_landing_mxn: Decimal
    tc_aplicado: Decimal
```

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `cotizador-pre-importacion` | Cálculo costo total antes de importar |
| `catalogo-tigie-busqueda` | Buscar fracción arancelaria por producto |
| `comparador-incoterms` | Costos por INCOTERM |
| `agente-aduanal-selector` | Padrón + ranking |
| `pedimento-tracker` | Status pedimento (clave + fecha) |
| `acreditacion-iva-importacion` | CFDI del proveedor extranjero |
| `compliance-padron-importadores` | Vigencia + renovación |
| `immex-control-inventario` | Si IMMEX activo |
| `reporte-mensual-importaciones` | Para contabilidad |
| `t-mec-origen-validator` | Si producto de USA/Canadá |

## 6. Comandos (5)

```
/import:cotizar
/import:fraccion
/import:pedimento
/import:acreditar-iva
/import:reporte
```

## 7. Workflow

`workflow-ciclo-importacion-completa.md`:
1. Recibir cotización proveedor extranjero
2. Validar fracción arancelaria (TIGIE)
3. Calcular costo landing total (IGI + IVA + DTA + flete + seguro)
4. Comparar INCOTERMS
5. Elegir agente aduanal del padrón
6. Iniciar trámite pedimento
7. Pagar impuestos (banca + DTA)
8. Recibir mercancía
9. Acreditar IVA en próximo cierre fiscal
10. Si IMMEX: descontar inventario virtual

## 8. Casos edge

| Caso | Acción |
|---|---|
| Importador sin padrón | BLOQUEAR — registrar primero en SAT |
| Producto en lista de control | Validar permiso SE / SENER / etc. antes |
| Mercancía detenida en aduana | Protocolo escalación a agente aduanal |
| Pedimento rechazado por documentación | Re-subir + nueva fecha |
| IVA acreditado sin pedimento físico | NO permitido — esperar pedimento |
| Importación regalo / muestra | Procedimientos simplificados (< $1k USD) |
| T-MEC: producto USA con > 50% componentes asiáticos | NO aplica preferencia arancelaria |
| Importador IMMEX con mercancía no exportada en plazo | Pagar IVA retroactivo + recargos |
| TC fluctuó entre orden y entrega | Usar TC del pedimento (no del pago) |

## 9. Dependencias

- **MCPs**: `mp_facturama_extendido` (CFDI con pedimento), `mp_banxico` (TC histórico), `mp_sat_portal` (padrón + 69-B agente aduanal)
- **MCPs nuevos sugeridos**:
  - `mp_sat_padron_importadores` — consulta vigencia
  - `mp_sat_pedimento_consulta` — verificación pedimento por clave
  - `mp_tigie_arancel` — catálogo arancelario (scraping DOF cada Anexo 22)
- **Skills `_shared/`**: cfdi-emision, mxn-formato

## 10. Criterios de aceptación

- [ ] Plugin completo
- [ ] Cotizador con cálculo correcto IGI + IVA + DTA + prevalidación
- [ ] Comparador INCOTERMS muestra diferencia clara
- [ ] Pedimento tracker con clave A1/F4/V1/etc.
- [ ] Acreditación IVA en CFDI con campo `NumPedimentoAduana`
- [ ] Soporte IMMEX básico (control inventario)
- [ ] Tests con 5 fixtures (importación normal, IMMEX, T-MEC, muestra, detenida)
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **Catálogo TIGIE básico (top 200 fracciones)**: 30-50h
- **Cotizador pre-importación**: 40-60h
- **Comparador INCOTERMS**: 25-40h
- **Tracking pedimentos**: 40-60h
- **Acreditación IVA + CFDI con pedimento**: 30-50h
- **Compliance padrón importadores**: 25-40h
- **IMMEX control inventario (básico)**: 50-80h
- **T-MEC origen validator**: 30-50h
- **Tests + 5 fixtures**: 40-60h
- **Docs + guía**: 30-50h
- **Validación con agente aduanal**: 10-15h coordinación
- **TOTAL**: **355-565 horas** (~9-14 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| TIGIE cambia (publicación DOF anual) | **Alta** | Alto | Anexo 22 RGCE — refresh anual + alerta cambios |
| Reglas IMMEX cambian | Media | Alto | Diseño modular |
| Mercancía detenida = costo enorme | Media | Crítico | Workflow alerta proactiva |
| Clasificación errónea = multa + impuestos | Alta | Alto | Asesoría agente aduanal — NO automatizar 100% |
| TC fluctúa mucho entre orden y pago | Alta | Medio | Reserva TC promedio + buffer |
| Aranceles T-MEC mal aplicados | Media | Alto | Validador con asesoría |

## 13. Decisiones pendientes

- [ ] ¿Integración con Microsoft Dynamics / SAP (sistemas grandes importadores)?
- [ ] ¿API directa con agentes aduanales (CAAAREM, etc.)?
- [ ] ¿Soporte exportación en V2 o vertical aparte?
- [ ] ¿Pricing: $1,999 MXN/mes para PyME importadora?

## 14. Plan de implementación

### Fase 1: Scaffold + catálogos (40-60h)
### Fase 2: Cotizador + INCOTERMS (60-100h)
### Fase 3: Pedimento + acreditación IVA (60-100h)
### Fase 4: IMMEX + compliance (80-130h)
### Fase 5: T-MEC + tests + docs (115-175h)

## 15. Links

- [KPMG - RGCE 2026 + Reforma LIGIE](https://kpmg.com/mx/es/tendencias/2026/01/flash-reglas-generales-de-comercio-exterior-para-2026.html)
- [SAT - Anexo 22 RGCE 2026](https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/anexos/Anexo22delasRGCEpara2026.pdf)
- [Garcia & Asociados - Importación 2026 PyMEs](https://www.garciayasociados.net/proceso-de-importacion-en-mexico-2026-guia-paso-a-paso-para-pymes)
- [Camtom - IMMEX 2026](https://www.camtomx.com/en/blog/regimen-importacion-temporal-immex-2026)
- [PwC - RGCE 2026](https://www.pwc.com/mx/es/impuestos/novedades-fiscales/reglas-generales-de-comercio-exterior-para-2026.html)
- [Ley Aduanera vigente](https://www.diputados.gob.mx/LeyesBiblio/pdf/LAdua.pdf)
