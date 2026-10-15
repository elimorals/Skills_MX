# airbnb-host-mx

Plugin para hosts de Airbnb y plataformas similares (Vrbo, Booking) en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install airbnb-host-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Cobertura

- 🏠 Tracking reservas + ocupación
- 💰 Fiscal: Art. 113-A LISR (4% ISR + 8% IVA retenido por plataforma), régimen 612 o 626
- 📋 ISH (Impuesto Sobre Hospedaje) estatal — varía por entidad (CDMX 3.5%, QRoo 5%, etc.)
- 🛏 Cumplimiento RAB CDMX (Registro de Anfitriones) — obligatorio desde 2025
- 🧾 CFDI al huésped si lo solicita
- 💸 Gastos deducibles: limpieza, mantenimiento, servicios

## Comandos

- `/airbnb:dashboard` — status del mes
- `/airbnb:reservas` — calendario + ocupación
- `/airbnb:fiscal` — cálculo Art. 113-A + ISH
- `/airbnb:cumplimiento` — RAB + reportes regulatorios

## ⚠ Compliance crítico

- **CDMX**: registro RAB obligatorio desde 2025; multas hasta $40k MXN
- **QRoo**: regulación estricta de alquiler turístico desde 2024
- **ISH**: declaración mensual al estado (separada de SAT federal)
- **Vecinos**: algunos condominios prohíben Airbnb (revisar reglamento)

## Score research: 8.2/10
