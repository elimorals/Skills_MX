"""Playwright real EdoMex — predial municipal + tenencia estatal.

REFACTORIZADO 2026-06-13: ya NO mantiene su propio dict PORTALES_PREDIAL.
Consulta `shared.catalogo_municipios_mx` en runtime. Eso evita duplicación y
asegura que cualquier hallazgo nuevo del script de discovery se propague
automáticamente a este MCP.

Patrón general:
1. `predial_real(municipio, cuenta)` → busca municipio en catálogo central.
2. Si está en catálogo y tiene URL + selectores → usa `consulta_portal()`.
3. Si no está o no tiene URL → UpstreamError con instrucción al usuario.

Tenencia estatal sigue siendo centralizada (SEF-EdoMex), se mantiene aparte.

⚠ Selectores marcados como "experimentales" — VALIDAR contra portal vigente
antes de uso producción. Cron de salud mensual recomendado.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.catalogo_municipios_mx import (  # noqa: E402
    buscar_portal_predial,
    get_municipio_config,
    listar_municipios_estado,
)
from shared.errors import UpstreamError  # noqa: E402
from shared.playwright_municipal_generic import (  # noqa: E402
    PortalConfig,
    consulta_portal,
)


# Tenencia estatal SEF-EdoMex sigue centralizada (no es un portal por municipio)
CONFIG_TENENCIA = PortalConfig(
    url="https://sfpya.edomexico.gob.mx/tenencia/",
    input_selectors=["input[name='placa']", "input#placa"],
    submit_selectors=["button:has-text('Consultar')", "button[type='submit']"],
    result_selector="table, .resultado",
    identificador_etiqueta="placa",
)


def _normalizar_clave_municipio(municipio: str) -> str:
    """Acepta 'Toluca', 'toluca', 'Toluca de Lerdo' → devuelve la clave del catálogo."""
    raw = municipio.lower().strip()
    # Reemplazos comunes
    raw = raw.replace(" ", "_")
    # Acentos
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        raw = raw.replace(a, b)
    # Algunos alias usuales que el usuario podría escribir
    alias = {
        "toluca_de_lerdo": "toluca",
        "ecatepec_de_morelos": "ecatepec",
        "naucalpan_de_juarez": "naucalpan",
        "tlalnepantla_de_baz": "tlalnepantla",
        "atizapan_de_zaragoza": "atizapan",
        "cuautitlan_izcalli": "cuautitlan_izcalli",
        "nezahualcoyotl": "nezahualcoyotl",
    }
    return alias.get(raw, raw)


def predial_real(municipio: str, cuenta_predial: str) -> dict[str, Any]:
    """Consulta predial de un municipio EdoMex usando el catálogo central.

    Args:
        municipio: nombre del municipio (case-insensitive). Acepta "Toluca",
            "toluca", "Toluca de Lerdo", etc.
        cuenta_predial: número/clave catastral a consultar.

    Returns:
        Dict con estructura estándar de `consulta_portal()`.

    Raises:
        UpstreamError si:
        - El municipio NO está en el catálogo (con sugerencia de claves válidas).
        - El municipio está pero su URL no fue verificada (validado=False).
        - El portal real falla durante la consulta.
    """
    mun_clave = _normalizar_clave_municipio(municipio)
    cfg_mun = get_municipio_config("edomex", mun_clave)

    if cfg_mun is None:
        soportados = listar_municipios_estado("edomex")
        raise UpstreamError(
            f"Municipio EdoMex '{municipio}' (clave='{mun_clave}') no está en el catálogo central. "
            f"Soportados: {soportados}",
            {"municipio": municipio, "clave_normalizada": mun_clave, "estado": "edomex"},
        )

    if not cfg_mun.portal_predial_url:
        raise UpstreamError(
            f"Municipio EdoMex '{cfg_mun.nombre}' no tiene URL de predial verificada. "
            f"Notas catálogo: {cfg_mun.notas}. "
            f"Correr `scripts/descubrir-portal-municipal.py` para intentar descubrir URL real.",
            {
                "municipio": cfg_mun.nombre,
                "validado": cfg_mun.validado,
                "notas": cfg_mun.notas,
            },
        )

    config = cfg_mun.to_predial_config()
    if config is None:
        raise UpstreamError(
            f"Municipio EdoMex '{cfg_mun.nombre}' tiene URL pero falló construcción de PortalConfig.",
            {"municipio": cfg_mun.nombre},
        )

    return consulta_portal(config, cuenta_predial)


def tenencia_real(placa: str, ejercicio: int = 2026) -> dict[str, Any]:
    """Consulta tenencia/refrendo vehicular EdoMex (portal SEF estatal centralizado)."""
    # SEF-EdoMex tenencia centralizada — no consulta el catálogo municipal
    config = PortalConfig(
        **{
            **CONFIG_TENENCIA.__dict__,
            "extra_inputs": {"input[name='ejercicio']": str(ejercicio)},
        }
    )
    return consulta_portal(config, placa)


def municipios_soportados() -> list[dict[str, Any]]:
    """Lista municipios EdoMex con estado de validación (para tool MCP de diagnóstico)."""
    soportados = []
    for mun_clave in listar_municipios_estado("edomex"):
        cfg = get_municipio_config("edomex", mun_clave)
        if cfg is None:
            continue
        soportados.append({
            "clave": mun_clave,
            "nombre": cfg.nombre,
            "tiene_url": bool(cfg.portal_predial_url),
            "validado": cfg.validado,
            "notas": cfg.notas[:120] if cfg.notas else None,
        })
    return soportados
