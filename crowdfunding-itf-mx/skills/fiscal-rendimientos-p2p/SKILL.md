---
name: fiscal-rendimientos-p2p
description: Calcula el tratamiento fiscal de intereses cobrados por una persona física en plataformas de crowdfunding de deuda (IFC) - retención de ISR que la IFC hace en sustitución del solicitante (20% sobre intereses nominales, regla 3.16.13 RMF desde oct-2024), interés real acumulable (Cap. VI LISR), acreditamiento en la declaración anual con el CFDI de retenciones y tratamiento de créditos incumplidos. Usar cuando el usuario diga fiscal rendimientos p2p, fiscal_rendimientos_p2p, impuestos crowdfunding, ISR de intereses de préstamos P2P, cómo declaro mis intereses de crowdfunding, ayuda con fiscal rendimientos p2p.
allowed-tools: Read, Write
---

# ISR de rendimientos en crowdfunding de deuda (persona física)

## Reglas (confianza media: fuentes secundarias)

- Desde el 12-10-2024 las IFC **retienen y enteran el ISR** en sustitución de sus clientes solicitantes: **20% sobre los intereses nominales** pagados a PF y PM residentes en México; 35% a residentes en el extranjero (regla 3.16.13, 2.ª Resolución de Modificaciones RMF 2024, DOF 11-10-2024; tasas según IMCP y EY 2026). Verifica la numeración y texto en la RMF 2026.
- Regla 4.1.12: la IFC también retiene/entera IVA sobre intereses cuando aplica (verificar supuestos; muchos intereses están exentos por Art. 15 LIVA).
- La IFC informa al SAT y entrega **CFDI de retenciones** (o constancia) por los intereses e impuestos retenidos.
- La retención del 0.90% anual sobre capital (LIF 2026) es para el sistema financiero; no aplica a IFC salvo que la regla diga otra cosa (verificar).

## En la declaración anual

1. **Interés real** = intereses nominales − ajuste por inflación (Art. 134 LISR; si el ajuste supera al interés, hay pérdida deducible en los términos del Art. 134, verificar límites).
2. Se acumula a los demás ingresos y se aplica la tarifa Art. 152 (2026: Anexo 8 RMF 2026).
3. Se **acredita** la retención del 20% que conste en el CFDI de retenciones.
4. Si la retención excede el impuesto: saldo a favor.

Créditos incumplidos (default): la pérdida de capital no es automáticamente deducible para la PF; trátala como "verificar con contador" y documenta la gestión de cobranza de la IFC.

## Ejemplo

Intereses nominales cobrados en 2026: $10,000 sobre un saldo promedio de $100,000; retención IFC 20% = **$2,000**.
Si el ajuste por inflación estimado fuera $3,800 (inflación ~3.8% × saldo), interés real = **$6,200** acumulable; se acreditan los $2,000 retenidos.

## Output esperado

```json
{
  "operation": "fiscal-rendimientos-p2p",
  "data": {
    "ejercicio": 2026,
    "intereses_nominales_mxn": "10000.00",
    "isr_retenido_ifc_mxn": "2000.00",
    "ajuste_inflacionario_mxn": "3800.00",
    "interes_real_acumulable_mxn": "6200.00",
    "cfdi_retenciones_recibidos": true
  },
  "vigencia_validada": false
}
```

El ajuste de $3,800 es ilustrativo: calcúlalo con el INPC real (`banxico_get_inpc` del MCP `mp_banxico`) y el saldo de cada mes.

## Casos edge

- Inversionista PM: los intereses son ingreso acumulable; la retención es pago provisional.
- Plataforma no autorizada por la CNBV (skill `catalogo-ifc-autorizadas`): no habrá retención ni CFDI; el contribuyente declara por su cuenta.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (CFDI, RFC, mxn-formato); MCP `mp_banxico` (INPC)

Orientativo: valida con tu contador antes de presentar la anual.
