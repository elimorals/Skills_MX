# conductor-plataforma-mx

Plugin para conductores de plataformas digitales (Uber, DiDi, Cabify, InDriver) en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install conductor-plataforma-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Cobertura fiscal

- **Régimen típico**: 626 RESICO PF (ingresos por servicio digital de transporte terrestre)
- **Art. 113-A LISR**: retención automática de la plataforma: ISR 2.1% (transporte y entrega) + IVA 8% (50% del IVA, Art. 18-M LIVA)
- **CFDI de retención**: las plataformas emiten CFDI tipo I (ingreso para conductor) automáticamente
- **IMSS-PIA**: opción de afiliarse al Programa Incorporación Anticipada con tarifa fija

## Skills

1. **dashboard-conductor** — ingresos semana + retenciones acumuladas
2. **ingresos-multi-plataforma** — suma ingresos de Uber + DiDi + Cabify + otros
3. **calculo-fiscal-conductor** — ISR neto a pagar adicional (si gana mucho)
4. **deducciones-conductor** — gasolina, mantenimiento, comisiones
5. **imss-pia-conductor** — alta IMSS-PIA + cuota mensual

## Comandos

- `/conductor:dashboard`
- `/conductor:ingresos-semana`
- `/conductor:calcular-fiscal`
- `/conductor:deducciones`

## ⚠ Compliance

- Art. 113-A LISR vigente desde 2020 — validar reformas anuales
- Las plataformas retienen pero el conductor SÍ presenta declaración anual
- IMSS-PIA voluntario pero recomendado (acceso a salud + retiro)

## Score research: 8.8/10
