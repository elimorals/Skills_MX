"""Drivers Playwright por banco MX.

⚠ ESQUELETO. Cada driver implementa la misma interfaz (`BancoPlaywrightDriver`)
pero los métodos `_real_*` están stubeados. Para activar el path real ver
`mcp-servers/mp_bancos_mx/SETUP_PLAYWRIGHT_REAL.md`.

Bancos cubiertos en este esqueleto:
- BBVA (México)
- Banamex / Citibanamex
- Santander México
- Banorte

Cada driver expone:
- `login()` — auth con usuario+password+2FA (asistido)
- `listar_movimientos()` — últimos N días
- `descargar_estado_cuenta()` — PDF/CSV mensual
- `verificar_pago_por_referencia()` — busca SPEI por clave
"""

from __future__ import annotations

from mp_bancos_mx.playwright_drivers.base import (
    BancoPlaywrightDriver,
    DriverMode,
    Movimiento,
    SesionExpiradaError,
)
from mp_bancos_mx.playwright_drivers.bbva import BbvaDriver
from mp_bancos_mx.playwright_drivers.banamex import BanamexDriver
from mp_bancos_mx.playwright_drivers.santander import SantanderDriver
from mp_bancos_mx.playwright_drivers.banorte import BanorteDriver


DRIVERS = {
    "bbva": BbvaDriver,
    "banamex": BanamexDriver,
    "santander": SantanderDriver,
    "banorte": BanorteDriver,
}


def get_driver(banco: str) -> type[BancoPlaywrightDriver] | None:
    """Retorna la clase del driver para el banco, o None si no soportado."""
    return DRIVERS.get(banco.lower())


__all__ = [
    "BancoPlaywrightDriver",
    "DriverMode",
    "Movimiento",
    "SesionExpiradaError",
    "BbvaDriver",
    "BanamexDriver",
    "SantanderDriver",
    "BanorteDriver",
    "DRIVERS",
    "get_driver",
]
