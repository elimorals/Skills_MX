---
spec: "vertical-sucesion-empresa-familiar-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [320, 540]
prioridad: "tier-2"
---

# Spec 13 — Vertical `sucesion-empresa-familiar-mx`

## 1. Propósito

Plugin para **familias mexicanas con patrimonio significativo** (> $5M MXN) que necesitan planificar sucesión hereditaria y/o estructurar gobierno familiar. Mercado: ~500k familias con patrimonio en este rango (CONEVAL + Forbes México).

Resuelve los **3 dolores no resueltos** del patriarca/matriarca mexicano:
1. Sucesión sin testamento → procedimiento sucesorio largo (1-3 años) + impuestos no optimizados
2. Donaciones en vida mal estructuradas (donaciones a familiares no directos = ISR a tasa normal)
3. Empresa familiar sin protocolo familiar → conflictos generacionales típicos (3-5 años para quebrar)

## 2. Contexto y por qué es novedoso

- **No hay vertical de patrimonio/sucesión**: aunque `freelancers-mx` toca fiscal individual, no cubre planificación intergeneracional
- **Reglas fiscales sucesión MX 2026 vigentes**:
  - Herencia/legado: **EXENTA del ISR** (Art. 93 LISR) — pero requiere proceso sucesorio
  - Donación entre cónyuges: 100% exenta sin límite
  - Donación ascendientes → descendientes (padres → hijos): 100% exenta sin límite
  - Donación entre hermanos/primos/tíos: gravable ISR como ingreso (tarifa Art. 96)
  - Exención $600k MXN/año por donaciones recibidas de no-familiares directos
- **Empresa familiar**: estructuras (S.A. de C.V., S. de R.L., trust offshore) — cada una con implicaciones distintas
- **Reformas fiscales 2025-2026**: aún no hay impuesto federal a herencias (algunos estados sí lo tienen tipo testamentaria — bajo, < 5% típico)

## 3. Alcance

**Dentro:**
- Diagnóstico patrimonial (inventario bienes + valuación)
- Simulador estructura óptima (donación vs herencia vs trust vs sociedad familiar)
- Cálculo ISR donaciones según relación familiar
- Calendario sucesorio (cuándo donar, cuándo testar, cuándo crear sociedad)
- Protocolo familiar básico (template editable)
- Plan testamentario (qué legar, a quién, condiciones)
- Tracking de bienes (inmuebles, acciones, cuentas, propiedades intelectuales)
- Sucesión testamentaria post-mortem (asistencia heredero ejecutor)
- Exención $600k/año donativos no-familiares

**Fuera (decisión deliberada):**
- Trusts offshore (Gibraltar, Bahamas, Delaware) — abogado fiscalista especializado
- Empresa familiar > 100M MXN (escala distinta, family office)
- Litigios sucesorios (abogado litigante)
- Estados con impuesto sucesión local (Yucatán, Tabasco) — caso específico
- Sucesión internacional (heredero en USA o EU) — derecho internacional privado

## 4. Inputs / outputs / schemas

### Patrimonio

```python
class PatrimonioFamiliar(BaseModel):
    titular_rfc: str
    titular_nombre: str
    estado_civil: Literal["casado_sgc", "casado_separacion", "soltero", "viudo", "divorciado"]
    bienes: list[Bien]
    valor_total_estimado_mxn: Decimal
    deudas_total_mxn: Decimal
    patrimonio_neto_mxn: Decimal
    herederos_designados: list[Heredero]
    tiene_testamento: bool
    fecha_testamento: date | None
    notario_testamento: str | None
```

### Bien

```python
class Bien(BaseModel):
    tipo: Literal["inmueble", "vehiculo", "acciones_pm", "cuenta_bancaria", "afore_retiro", "joya", "obra_arte", "propiedad_intelectual", "otros"]
    descripcion: str
    valor_estimado_mxn: Decimal
    porcentaje_propiedad: float  # 1.0 = propiedad total, 0.5 = co-propiedad cónyuge
    fecha_adquisicion: date | None
    documento_legal: str  # escritura, factura, etc.
```

### Heredero

```python
class Heredero(BaseModel):
    rfc: str | None
    nombre: str
    relacion: Literal["conyuge", "hijo", "nieto", "padre", "hermano", "sobrino", "amigo", "ong"]
    porcentaje_asignado: float
    bienes_especificos: list[str]  # IDs de bienes
    es_menor_edad: bool
```

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `diagnostico-patrimonial` | Inventario inicial |
| `simulador-donacion-vs-herencia` | Compara estructuras |
| `calculo-isr-donaciones` | Por relación familiar |
| `calendario-sucesorio` | Plan a 5 años |
| `protocolo-familiar-empresa` | Template + asesoría |
| `plan-testamentario` | Distribución óptima |
| `tracking-bienes-anual` | Revalorización + actualización |
| `asistencia-sucesion-post-mortem` | Si causante falleció |
| `exencion-600k-donativos-anual` | Tracking exención no-familiar |
| `compliance-impuesto-sucesion-estatal` | Yucatán, Tabasco, etc. |

## 6. Comandos (5)

```
/sucesion:diagnostico
/sucesion:simulador
/sucesion:plan-testamento
/sucesion:donaciones-año
/sucesion:asistencia-fallecimiento
```

## 7. Workflow

`workflow-planificacion-sucesion-completa.md`:
1. Diagnóstico patrimonial inicial
2. Identificar relación con cada heredero potencial
3. Calcular impacto fiscal cada escenario
4. Simular escenarios: 100% testamento vs 50% donación en vida + 50% testamento vs trust
5. Generar plan óptimo según objetivos del titular
6. Calendarizar acciones (qué hacer este año, próximo, etc.)
7. Recomendar especialistas: notario para testamento, abogado fiscalista, contador familiar

## 8. Casos edge

| Caso | Acción |
|---|---|
| Cónyuge en sociedad conyugal | 50% del patrimonio común ya es del cónyuge — solo distribuir el 50% propio |
| Hijo único | Toda herencia para él (libre disposición legítima 50%) |
| Hijos en distintas etapas (uno casado, otro estudiante) | Distribución equitativa pero condicionada |
| Empresa familiar con hijos en distintas posiciones | Acciones con voto vs sin voto |
| Bien inmueble heredado entre 5 hijos | Recomendación: vender + repartir efectivo (evita co-propiedad conflictiva) |
| Donación > $600k de no-familiar | Gravable como ingreso |
| Estado con impuesto sucesión local | Calcular adicional |
| Sucesión sin testamento (intestada) | Procedimiento más largo + costos notariales mayores |
| Heredero menor de edad | Tutor / curador legalmente designado |
| Cónyuge segunda nupcia con hijos previos | Planificar legítima para hijos del primer matrimonio |

## 9. Dependencias

- **MCPs**: `mp_sat_portal` (RFC herederos), `mp_banxico` (UMA, INPC para revalorización), `mp_facturama_extendido` (CFDI donaciones si aplica)
- **MCPs nuevos sugeridos**: `mp_registro_publico_propiedad` (RPP — consulta inmuebles a nombre del titular)
- **Skills `_shared/`**: rfc-validacion, mxn-formato, compliance-lfpdppp

## 10. Criterios de aceptación

- [ ] Plugin completo
- [ ] Diagnóstico patrimonial con valuación
- [ ] Simulador con al menos 4 escenarios (testar todo, donar parte, trust, sociedad)
- [ ] Cálculo ISR donaciones por relación familiar
- [ ] Calendario sucesorio con hitos
- [ ] Protocolo familiar template básico
- [ ] Lint passing
- [ ] Disclaimer obligatorio: "NO sustituye asesoría legal — consultar notario + abogado fiscalista"

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **10 skills**: 100-160h
- **Workflow planificación + simulador**: 50-80h
- **Cálculo ISR donaciones (tabla)**: 30-50h
- **Protocolo familiar template**: 25-40h
- **Plan testamentario generator**: 30-50h
- **Asistencia post-mortem**: 30-50h
- **Tests + 5 fixtures**: 30-50h
- **Docs + compliance legal**: 25-40h
- **Validación con notario + abogado fiscalista**: 15-25h coordinación
- **TOTAL**: **340-555 horas** (~9-14 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Cliente actúa sin asesoría legal real | Media | Crítico | Disclaimers visibles + recomendar notario siempre |
| Cálculo donación incorrecto = ISR sorpresa | Baja | Alto | `vigencia_validada: false` + revisión contador |
| Cambios fiscales (probable impuesto herencias futuro) | Media | Alto | Diseño modular |
| Cliente con bienes en USA/Europa | Media | Alto | Marcar "consultar abogado internacional" |
| Privacidad — info muy sensible patrimonial | Alta | Crítico | Cifrado en reposo + acceso restringido titular |

## 13. Decisiones pendientes

- [ ] ¿Producto consumer ($5,999 MXN/año) vs B2B abogados/notarios ($24k MXN/año)?
- [ ] ¿Incluir simulador trust offshore (riesgo regulatorio)?
- [ ] ¿Compatibilidad estados con impuesto local (Yucatán, Tabasco)?
- [ ] ¿Templates protocolo familiar por industria (manufactura, restaurantes, etc.)?

## 14. Plan de implementación

### Fase 1: Scaffold (5-10h)
### Fase 2: Diagnóstico patrimonial (50-80h)
### Fase 3: Simulador ISR donaciones (50-80h)
### Fase 4: Plan testamentario + calendario (60-100h)
### Fase 5: Protocolo familiar + asistencia post-mortem (60-100h)
### Fase 6: Tests + docs + validación legal (115-185h)

## 15. Links

- [Russell Bedford - Donativos PF tratamiento fiscal](https://russellbedford.mx/fiscal/donativos-personas-fisicas-y-su-tratamiento-fiscal/)
- [Konta - Donativos familiares ante SAT](https://konta.com/blog/donativos-familiares-como-se-manejan-ante-el-sat)
- [UNAM - Leyes herencias y donaciones](https://archivos.juridicas.unam.mx/www/bjv/libros/6/2791/12.pdf)
- [Art. 93 LISR - Exención herencia/legado](https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf)
- [Notaria 230 - Donación consecuencias](https://www.notaria230.com.mx/consecuencias-fiscales-de-la-donacion/)
- [Calculadora ISR Donación y Herencia 2026](https://cotizadorhipotecario.mx/impuestos/calculadora-donaciones/)
