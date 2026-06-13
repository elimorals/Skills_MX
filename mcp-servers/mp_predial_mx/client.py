"""Cliente unificado para consulta predial multi-municipio MX.

Consulta CUALQUIER municipio del catálogo central + plataformas SaaS (SACPI MICH)
con una sola interfaz. Reemplaza los 8 MCPs municipales (mp_cdmx_municipal,
mp_edomex_municipal, etc.) — los cuales se mantienen por backward compat.

Auto-routing por (estado, municipio):
1. ¿Tiene plataforma_saas en catálogo? → invocar shared.plataformas_saas_mx
2. ¿Tiene portal_predial_url? → invocar shared.playwright_municipal_generic.consulta_portal
3. Ninguno → ValidationError con instrucciones

Modo mock por default (sin Playwright real). Activar real con MP_PLAYWRIGHT_PUBLIC=1.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.catalogo_municipios_mx import (  # noqa: E402
    MUNICIPIOS,
    MunicipioConfig,
    estadisticas,
    get_municipio_config,
    listar_estados,
    listar_municipios_estado,
    listar_municipios_validados,
)
from shared.errors import McpError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.playwright_municipal_generic import consulta_portal  # noqa: E402
from shared.playwright_real import (  # noqa: E402
    is_public_real_enabled,
    with_real_or_fallback,
)
from shared.plataformas_saas_mx import (  # noqa: E402
    consulta_sacpi,
    codigo_municipio_sacpi,
    plataforma_para_municipio,
    SACPI_MICHOACAN,
)

NAMESPACE = "predial_mx"


def _normalizar_clave(s: str) -> str:
    """'Toluca de Lerdo' → 'toluca_de_lerdo'."""
    out = s.lower().strip()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                  ("ñ", "n"), (" ", "_"), (",", ""), (".", ""),
                  ("(", ""), (")", "")):
        out = out.replace(a, b)
    return out


class PredialMxClient:
    """Cliente predial unificado MX."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        # Hash de cuenta para bitácora (no exponer)
        safe = dict(params)
        if "cuenta_predial" in safe:
            safe["cuenta_hash"] = Bitacora.hash_sensitive(str(safe.pop("cuenta_predial")))
        self._bitacora.log(op, success=True, params_summary=safe)

    # ============================================================
    # Tools principales
    # ============================================================

    def consultar(
        self,
        estado: str,
        municipio: str,
        cuenta_predial: str,
        tipo: str = "urbano",
        direccion: Optional[str] = None,
    ) -> dict[str, Any]:
        """Consulta predial unificado para cualquier municipio del catálogo.

        Args:
            estado: clave estado (2-5 letras): "cdmx", "jal", "mich", etc.
            municipio: clave municipio normalizada o nombre. Acepta "Toluca", "toluca".
            cuenta_predial: clave catastral.
            tipo: "urbano" | "rustico" (solo para SACPI).
            direccion: opcional, requerido para Mérida (busca por calle+numero).

        Returns:
            Dict con estructura estándar de consulta_portal o consulta_sacpi.

        Raises:
            ValidationError si estado/municipio no están en catálogo.
            UpstreamError si el portal falla o no hay URL verificada.
        """
        estado_norm = _normalizar_clave(estado)
        mun_norm = _normalizar_clave(municipio)

        self._log("consultar", {
            "estado": estado_norm,
            "municipio": mun_norm,
            "cuenta_predial": cuenta_predial,  # se hashea en _log
            "tipo": tipo,
        })

        if estado_norm not in listar_estados():
            raise ValidationError(
                f"Estado '{estado}' no en catálogo. "
                f"Válidos: {listar_estados()[:5]}..."
            )

        cfg = get_municipio_config(estado_norm, mun_norm)
        if cfg is None:
            soportados = listar_municipios_estado(estado_norm)
            raise ValidationError(
                f"Municipio '{municipio}' (clave='{mun_norm}') no encontrado en {estado_norm}. "
                f"Soportados: {soportados[:10]}{'...' if len(soportados) > 10 else ''}"
            )

        # Mock mode si no está habilitado Playwright público
        if not is_public_real_enabled():
            return mark_simulated(self._mock_response(estado_norm, mun_norm, cuenta_predial, cfg))

        # ROUTING 1: ¿Plataforma SaaS?
        if cfg.plataforma_saas == "SACPI":
            codigo = cfg.codigo_saas or codigo_municipio_sacpi(cfg.nombre)
            if not codigo:
                raise UpstreamError(
                    f"Municipio {cfg.nombre} marcado SACPI pero sin código asignado.",
                    {"municipio": cfg.nombre},
                )
            tipo_codigo = "1" if tipo == "urbano" else "2"
            return with_real_or_fallback(
                real_fn=lambda: consulta_sacpi(codigo, cuenta_predial, tipo=tipo_codigo),
                fallback_fn=lambda: self._mock_response(estado_norm, mun_norm, cuenta_predial, cfg),
                portal="sacpi_michoacan",
            )

        # ROUTING 2: ¿Portal directo en catálogo?
        if cfg.portal_predial_url and cfg.selectores_predial:
            portal_cfg = cfg.to_predial_config()
            if portal_cfg is None:
                raise UpstreamError(
                    f"Municipio {cfg.nombre} con URL pero falló PortalConfig.",
                    {},
                )
            # Caso especial Mérida: busca por dirección, no cuenta
            identificador = direccion if (estado_norm == "yuc" and mun_norm == "merida" and direccion) else cuenta_predial
            return with_real_or_fallback(
                real_fn=lambda: consulta_portal(portal_cfg, identificador),
                fallback_fn=lambda: self._mock_response(estado_norm, mun_norm, cuenta_predial, cfg),
                portal=f"{estado_norm}_{mun_norm}",
            )

        # ROUTING 3: Sin URL ni SaaS — no automatizable
        raise UpstreamError(
            f"Municipio {cfg.nombre} ({estado_norm}/{mun_norm}) no tiene URL verificada ni plataforma SaaS. "
            f"Notas: {cfg.notas}. "
            f"Correr scripts/descubrir-portal-municipal.py para intentar descubrir, "
            f"o consultar manualmente en el municipio.",
            {
                "estado": estado_norm,
                "municipio": mun_norm,
                "validado": cfg.validado,
                "notas": cfg.notas,
            },
        )

    def listar_municipios(
        self,
        estado: Optional[str] = None,
        solo_validados: bool = False,
    ) -> dict[str, Any]:
        """Lista municipios soportados (opcionalmente filtrado por estado).

        Returns:
            {
              "total": N,
              "por_estado": {estado: [{clave, nombre, validado, tiene_url, tiene_saas}]}
            }
        """
        self._log("listar_municipios", {"estado": estado, "solo_validados": solo_validados})

        resultado: dict[str, Any] = {"total": 0, "por_estado": {}}

        estados_iter = [estado] if estado else listar_estados()
        for estado_clave in estados_iter:
            if estado_clave not in MUNICIPIOS:
                continue
            municipios_lista = []
            for mun_clave, cfg in MUNICIPIOS[estado_clave].items():
                if solo_validados and not cfg.validado:
                    continue
                municipios_lista.append({
                    "clave": mun_clave,
                    "nombre": cfg.nombre,
                    "validado": cfg.validado,
                    "tiene_url": bool(cfg.portal_predial_url),
                    "tiene_saas": bool(cfg.plataforma_saas),
                    "poblacion_aprox": cfg.poblacion_aprox,
                })
            if municipios_lista:
                resultado["por_estado"][estado_clave] = municipios_lista
                resultado["total"] += len(municipios_lista)

        return resultado

    def estadisticas_catalogo(self) -> dict[str, Any]:
        """Devuelve métricas del catálogo: total municipios, validados, cobertura poblacional."""
        from shared.plataformas_saas_mx import estadisticas_saas
        stats = estadisticas()
        stats_saas = estadisticas_saas()
        return {
            **stats,
            "saas": stats_saas,
            "cobertura_efectiva": stats["municipios_validados"] + stats_saas["municipios_cubiertos_via_saas"],
        }

    def buscar_municipio(self, query: str) -> list[dict[str, Any]]:
        """Búsqueda fuzzy de municipios por nombre.

        Ejemplo: buscar_municipio("merida") → [{estado: 'yuc', clave: 'merida', ...}]
        """
        query_norm = _normalizar_clave(query)
        resultados = []
        for estado_clave, muns in MUNICIPIOS.items():
            for mun_clave, cfg in muns.items():
                if query_norm in mun_clave or query_norm in _normalizar_clave(cfg.nombre):
                    resultados.append({
                        "estado": estado_clave,
                        "clave": mun_clave,
                        "nombre": cfg.nombre,
                        "validado": cfg.validado,
                        "poblacion_aprox": cfg.poblacion_aprox,
                    })
        return resultados[:20]

    # ============================================================
    # Mock response (fallback cuando MP_PLAYWRIGHT_PUBLIC=0)
    # ============================================================

    def _mock_response(
        self,
        estado: str,
        municipio: str,
        cuenta: str,
        cfg: MunicipioConfig,
    ) -> dict[str, Any]:
        """Respuesta mock realista para desarrollo sin browser."""
        cuenta_hash = cuenta[:4] + "*" * max(0, len(cuenta) - 4)
        # Generar adeudo pseudoaleatorio basado en hash de cuenta para consistencia
        seed = sum(ord(c) for c in cuenta) % 100
        adeudo_simulado = (seed * 137.5) if seed > 30 else 0
        return {
            "estado": estado,
            "municipio": municipio,
            "municipio_nombre": cfg.nombre,
            "cuenta_predial_hash": cuenta_hash,
            "estatus": "al_corriente" if adeudo_simulado == 0 else "con_adeudo",
            "adeudo_total_mxn": round(adeudo_simulado, 2),
            "bimestres_pendientes": max(0, (seed - 30) // 20),
            "conceptos": [
                {"concepto": f"Bimestre {i+1} 2026", "monto_mxn": round(adeudo_simulado / 3, 2)}
                for i in range(min(3, max(0, (seed - 30) // 20)))
            ] if adeudo_simulado > 0 else [],
            "url_consultada": cfg.portal_predial_url or "mock://no-url",
            "plataforma": cfg.plataforma_saas or "directo",
        }
