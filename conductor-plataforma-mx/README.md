# conductor-plataforma-mx

Plugin para conductores de plataformas digitales (Uber, DiDi, Cabify, InDriver) en México.

## Cobertura fiscal

- **Régimen típico**: 626 RESICO PF (ingresos por servicio digital de transporte terrestre)
- **Art. 113-A LISR**: retención automática plataforma 8% ISR + 8% IVA del valor del viaje
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
