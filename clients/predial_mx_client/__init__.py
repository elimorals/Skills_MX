"""predial_mx_client — cliente Python standalone para consulta predial MX.

NO requiere Claude Code ni MCPs — librería pura usable desde cualquier
app Python (Django, FastAPI, scripts CLI, notebooks, etc.).

USO:
    from predial_mx_client import PredialMxClient

    client = PredialMxClient(modo="mock")  # o "real" con MP_PLAYWRIGHT_PUBLIC=1
    resultado = client.consultar(estado="jal", municipio="guadalajara", cuenta="U12345678")
    print(resultado["adeudo_total_mxn"])

    # Listar municipios soportados
    print(client.listar_validados())

    # Búsqueda fuzzy
    print(client.buscar("guadal"))
"""

from predial_mx_client.client import (
    PredialMxClient,
    PredialResponse,
    MunicipioInfo,
    NoSoportadoError,
    PortalCaidoError,
    CaptchaRequeridoError,
)

__version__ = "0.1.0"
__all__ = [
    "PredialMxClient",
    "PredialResponse",
    "MunicipioInfo",
    "NoSoportadoError",
    "PortalCaidoError",
    "CaptchaRequeridoError",
]
