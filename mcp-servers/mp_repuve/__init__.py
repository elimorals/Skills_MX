"""mp_repuve — MCP para REPUVE (Registro Público Vehicular).

Permite consultar si un vehículo tiene reporte de robo activo en el padrón
nacional. Universo principal:
  - Aseguradoras (cotización + suscripción de pólizas auto)
  - Plataformas de movilidad (Uber/DiDi — verificar autos de socios)
  - Compraventas usadas (Kavak, Clutch, etc.)
  - Despachos de leasing automotriz
  - RRHH (autos de empleados con uso de empresa)

Portal: https://www2.repuve.gob.mx:8443/ciudadania/
Stack:  Angular SPA + reCAPTCHA v3 — requiere Playwright para path real.
"""
__all__: list[str] = []
