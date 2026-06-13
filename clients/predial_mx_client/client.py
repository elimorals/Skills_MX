"""Cliente Python standalone para consulta predial municipal MX.

Wrapper sobre mcp-servers/mp_predial_mx/client.py + manejo de errores
ergonómico + soporte async opcional.

Diseñado para integrarse en apps externas (web, móviles, CLIs) que NO
usan Claude Code/MCP.

Modos:
- "mock": respuestas simuladas (default si MP_PLAYWRIGHT_PUBLIC != 1)
- "real": consultas reales vía Playwright (requiere playwright instalado)
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Bootstrap: agregar mcp-servers/ al path si está en repo plugins-mx
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent  # clients/predial_mx_client/ → repo root
_MCP_SERVERS = _REPO_ROOT / "mcp-servers"
if _MCP_SERVERS.exists() and str(_MCP_SERVERS) not in sys.path:
    sys.path.insert(0, str(_MCP_SERVERS))


# Importar componentes del core
try:
    from mp_predial_mx.client import PredialMxClient as _CoreClient
    from shared.errors import McpError, UpstreamError, ValidationError
except ImportError as e:
    raise ImportError(
        f"No se pudo importar el core mp_predial_mx. "
        f"Asegúrate de que mcp-servers/ esté accesible. Error: {e}"
    ) from e


# ============================================================
# Exceptions específicas del cliente (más ergonómicas que McpError)
# ============================================================

class PredialClientError(Exception):
    """Base exception del cliente."""


class NoSoportadoError(PredialClientError):
    """Municipio no soportado en el catálogo."""


class PortalCaidoError(PredialClientError):
    """Portal del municipio no respondió o falló."""


class CaptchaRequeridoError(PredialClientError):
    """Portal requiere CAPTCHA humano — no automatizable.

    Atributos:
        url_consulta_manual: URL para que el cliente complete a mano.
    """
    def __init__(self, mensaje: str, url_consulta_manual: str = ""):
        super().__init__(mensaje)
        self.url_consulta_manual = url_consulta_manual


# ============================================================
# Data classes ergonómicas
# ============================================================

@dataclass
class PredialResponse:
    """Respuesta estructurada de consulta predial."""
    estado: str
    municipio: str
    municipio_nombre: str
    estatus: str  # "al_corriente" | "con_adeudo"
    adeudo_total_mxn: float
    bimestres_pendientes: int = 0
    conceptos: list[dict] = field(default_factory=list)
    url_consultada: str = ""
    simulated: bool = True
    raw: dict = field(default_factory=dict)

    @property
    def al_corriente(self) -> bool:
        return self.estatus == "al_corriente"

    @property
    def es_real(self) -> bool:
        return not self.simulated

    @classmethod
    def from_raw(cls, raw: dict) -> PredialResponse:
        return cls(
            estado=raw.get("estado", ""),
            municipio=raw.get("municipio") or raw.get("municipio_codigo", ""),
            municipio_nombre=raw.get("municipio_nombre", ""),
            estatus=raw.get("estatus", "desconocido"),
            adeudo_total_mxn=float(raw.get("adeudo_total_mxn", 0) or 0),
            bimestres_pendientes=int(raw.get("bimestres_pendientes", 0) or 0),
            conceptos=raw.get("conceptos", []) or [],
            url_consultada=raw.get("url_consultada", ""),
            simulated=bool(raw.get("simulated", True)),
            raw=raw,
        )


@dataclass
class MunicipioInfo:
    """Info compacta de un municipio en el catálogo."""
    estado: str
    clave: str
    nombre: str
    validado: bool
    tiene_url: bool
    tiene_saas: bool
    poblacion_aprox: int = 0


# ============================================================
# Cliente principal
# ============================================================

class PredialMxClient:
    """Cliente Python standalone para consulta predial MX.

    Args:
        modo: "mock" (default) | "real". "real" requiere MP_PLAYWRIGHT_PUBLIC=1
              env var + playwright instalado.
    """

    def __init__(self, modo: str = "mock"):
        if modo not in ("mock", "real"):
            raise ValueError(f"modo debe ser 'mock' o 'real', recibí '{modo}'")
        self.modo = modo
        if modo == "real":
            os.environ["MP_PLAYWRIGHT_PUBLIC"] = "1"
        self._core = _CoreClient()

    # ============================================================
    # Tools de consulta
    # ============================================================

    def consultar(
        self,
        estado: str,
        municipio: str,
        cuenta: str,
        tipo: str = "urbano",
        direccion: Optional[str] = None,
    ) -> PredialResponse:
        """Consulta predial de un municipio.

        Args:
            estado: clave estado ("cdmx", "jal", "mich", ...)
            municipio: clave municipio (ej. "guadalajara") o nombre ("Guadalajara")
            cuenta: clave catastral del municipio
            tipo: "urbano" | "rustico" (solo SACPI MICH)
            direccion: requerido para Mérida (busca por calle+numero)

        Returns:
            PredialResponse con .adeudo_total_mxn, .al_corriente, etc.

        Raises:
            NoSoportadoError: municipio no en catálogo o sin URL verificada
            CaptchaRequeridoError: portal requiere CAPTCHA (Puebla)
            PortalCaidoError: portal no respondió o falló
        """
        try:
            raw = self._core.consultar(
                estado=estado,
                municipio=municipio,
                cuenta_predial=cuenta,
                tipo=tipo,
                direccion=direccion,
            )
        except ValidationError as e:
            raise NoSoportadoError(str(e)) from e
        except UpstreamError as e:
            msg = str(e)
            if "CAPTCHA" in msg or "captcha" in msg.lower():
                # Extraer URL si está en el contexto
                url = e.context.get("url_consulta_manual", "") if hasattr(e, "context") else ""
                raise CaptchaRequeridoError(msg, url_consulta_manual=url) from e
            raise PortalCaidoError(msg) from e
        except McpError as e:
            raise PredialClientError(str(e)) from e

        return PredialResponse.from_raw(raw)

    # ============================================================
    # Tools de exploración del catálogo
    # ============================================================

    def listar_municipios(
        self,
        estado: Optional[str] = None,
        solo_validados: bool = False,
    ) -> list[MunicipioInfo]:
        """Lista municipios soportados.

        Args:
            estado: filtrar por estado (opcional)
            solo_validados: solo los que tienen URL real verificada

        Returns:
            Lista plana de MunicipioInfo.
        """
        raw = self._core.listar_municipios(estado=estado, solo_validados=solo_validados)
        out = []
        for estado_clave, muns in raw.get("por_estado", {}).items():
            for m in muns:
                out.append(MunicipioInfo(
                    estado=estado_clave,
                    clave=m["clave"],
                    nombre=m["nombre"],
                    validado=m["validado"],
                    tiene_url=m["tiene_url"],
                    tiene_saas=m["tiene_saas"],
                    poblacion_aprox=m.get("poblacion_aprox", 0),
                ))
        return out

    def listar_validados(self, estado: Optional[str] = None) -> list[MunicipioInfo]:
        """Atajo: solo municipios validados con URL real."""
        return self.listar_municipios(estado=estado, solo_validados=True)

    def buscar(self, query: str) -> list[MunicipioInfo]:
        """Búsqueda fuzzy de municipios por nombre o clave parcial."""
        raw = self._core.buscar_municipio(query)
        return [
            MunicipioInfo(
                estado=m["estado"],
                clave=m["clave"],
                nombre=m["nombre"],
                validado=m["validado"],
                tiene_url=True,  # asumimos sí — buscar_municipio no devuelve estos flags
                tiene_saas=False,
                poblacion_aprox=m.get("poblacion_aprox", 0),
            )
            for m in raw
        ]

    def estadisticas(self) -> dict[str, Any]:
        """Estadísticas del catálogo (total, validados, cobertura poblacional)."""
        return self._core.estadisticas_catalogo()

    # ============================================================
    # Helpers
    # ============================================================

    def es_soportado(self, estado: str, municipio: str) -> bool:
        """¿Este municipio está en el catálogo (validado o no)?"""
        try:
            from shared.catalogo_municipios_mx import get_municipio_config
            return get_municipio_config(estado, municipio) is not None
        except Exception:
            return False

    def es_validado(self, estado: str, municipio: str) -> bool:
        """¿Este municipio tiene URL real verificada?"""
        try:
            from shared.catalogo_municipios_mx import get_municipio_config
            cfg = get_municipio_config(estado, municipio)
            return bool(cfg and cfg.validado)
        except Exception:
            return False
