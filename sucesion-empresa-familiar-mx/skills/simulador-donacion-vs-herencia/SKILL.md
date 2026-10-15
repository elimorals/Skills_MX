---
name: simulador-donacion-vs-herencia
description: Compara 4 escenarios para transmitir el patrimonio o la empresa familiar - testamento (herencia exenta de ISR, Art. 93 fr. XXII LISR), donación en vida (exenta en línea recta, con costo fiscal heredado), fideicomiso (testamentario o de administración) y sociedad/holding familiar - con su impacto en ISR al recibir y al vender después (Art. 124), impuestos locales de traslado, gastos notariales y control. Usar cuando el usuario diga simulador donación vs herencia, simulador_donacion_vs_herencia, ¿conviene donar o heredar?, pasar la empresa a mis hijos, heredar en vida, fideicomiso familiar, holding familiar, ayuda con simulador donación vs herencia.
allowed-tools: Read, Write
---

# Simulador donación vs. herencia

## Reglas fiscales base (LISR vigente)

- **Herencia o legado**: exento de ISR para el heredero (Art. 93 fr. XXII). Si sus ingresos totales del año superan $500,000 debe declararlo en la anual como ingreso exento (Art. 150).
- **Donación**: exenta entre cónyuges y en línea recta (Art. 93 fr. XXIII); otros, solo hasta 3 UMA anuales ($128,454.45 en 2026). Ver skill `calculo-isr-donaciones`.
- **Costo fiscal** (Art. 124): en herencia, legado o donación exenta, el adquirente conserva **el costo y la fecha de adquisición del autor de la sucesión o donante**. Si la donación pagó ISR, el costo es el avalúo usado.
- **Al vender después**: ganancia = precio − costo heredado actualizado; casa habitación puede quedar exenta hasta 700,000 UDIS si fue casa del vendedor y cumple requisitos (Art. 93 fr. XIX; verificar).
- **Impuestos locales**: ISAI o traslado de dominio, derechos de registro y honorarios notariales varían por entidad; algunas entidades tratan distinto herencia y donación (verificar ley de hacienda estatal).

## Escenarios

| Escenario | ISR al recibir | Control del titular | Puntos críticos |
|---|---|---|---|
| 1. Testamento | Exento | Total hasta el fallecimiento | Juicio sucesorio o trámite notarial; tiempo y costos; puede impugnarse |
| 2. Donación en vida (con reserva de usufructo) | Exento en línea recta/cónyuges | Conserva uso y frutos con el usufructo | Es irrevocable salvo causas legales; ISAI local; costo fiscal heredado |
| 3. Fideicomiso (de administración o testamentario) | Depende de la estructura (verificar con fiscalista) | Alto, vía instrucciones al fiduciario | Honorarios fiduciarios; diseño fiscal específico |
| 4. Sociedad / holding familiar | Transmisión de acciones: exenta si es donación/herencia en línea recta | Vía estatutos y protocolo familiar | Aportar bienes a la sociedad puede causar ISR (enajenación) salvo esquemas autorizados; avisos de beneficiario controlador (Art. 32-B Ter CFF) |

## Entradas del simulador

```python
class Activo(BaseModel):
    tipo: Literal["inmueble", "acciones", "cuenta", "otro"]
    valor_mercado: Decimal
    costo_fiscal_titular: Decimal
    fecha_adquisicion: date
    entidad_federativa: str | None
```

Para cada escenario calcula: ISR al recibir, impuestos locales estimados (o "verificar"), costos notariales/fiduciarios (rangos que dé el usuario), y ISR estimado si el heredero vende en N años.

## Output esperado

```json
{
  "operation": "simulador-donacion-vs-herencia",
  "data": {
    "escenarios": [
      {"nombre": "testamento", "isr_al_recibir": "0.00", "isr_si_vende": "<calculado>", "impuestos_locales": "verificar"},
      {"nombre": "donacion_usufructo", "isr_al_recibir": "0.00", "isr_si_vende": "<calculado>", "impuestos_locales": "verificar"},
      {"nombre": "fideicomiso", "isr_al_recibir": "verificar", "costos_fiduciarios": "<entrada usuario>"},
      {"nombre": "holding_familiar", "isr_al_recibir": "verificar", "isr_aportacion": "verificar"}
    ],
    "recomendacion": "comparativo, no asesoría"
  },
  "vigencia_validada": false
}
```

## Casos edge

- Receptores que no son cónyuge ni línea recta: la donación grava sobre 3 UMA anuales; la herencia no.
- Bienes en el extranjero o herederos no residentes: fuera de alcance, derivar a especialista.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (RFC, mxn-formato); skills `calculo-isr-donaciones`, `diagnostico-patrimonial-familiar`

⚠ Planeación patrimonial: el resultado es un comparativo orientativo. Requiere validación de notario, abogado y fiscalista.
