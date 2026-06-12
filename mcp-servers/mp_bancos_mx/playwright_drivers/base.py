"""Base class para drivers Playwright bancarios.

Cada banco hereda esta clase. Mock/real lo decide `get_mode()`. Si está en mock
o blocked, retorna data sintética con flag `real_implementation_pending: true`.

Patrón shared con `mp_sat_portal.playwright_client` — pero como cada banco tiene
auth distinta (token físico Banamex, app push BBVA, biométrico Santander, SMS
Banorte) cada subclass implementa `_real_login()` específico.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from shared.bitacora import Bitacora
from shared.errors import AuthError, ConfigError, McpError, UpstreamError


class DriverMode(str, Enum):
    MOCK = "mock"
    BLOCKED = "blocked"
    REAL = "real"


class SesionExpiradaError(AuthError):
    code = "sesion_expirada"


class CredencialesIncompletasError(ConfigError):
    code = "credenciales_incompletas"


@dataclass
class Movimiento:
    """Movimiento bancario normalizado entre los 4 bancos."""

    fecha: date
    tipo: str  # "deposito" | "retiro" | "transferencia" | "comision" | ...
    concepto: str
    referencia_numerica: str | None
    clave_rastreo_spei: str | None
    monto: Decimal
    saldo_resultante: Decimal | None = None
    rfc_ordenante: str | None = None
    banco_ordenante: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "fecha": self.fecha.isoformat(),
            "tipo": self.tipo,
            "concepto": self.concepto,
            "referencia_numerica": self.referencia_numerica,
            "clave_rastreo_spei": self.clave_rastreo_spei,
            "monto": str(self.monto),
            "saldo_resultante": str(self.saldo_resultante) if self.saldo_resultante is not None else None,
            "rfc_ordenante": self.rfc_ordenante,
            "banco_ordenante": self.banco_ordenante,
        }


@dataclass
class DriverConfig:
    usuario: str | None = None
    password: str | None = None
    extra: dict[str, str] = field(default_factory=dict)  # 2FA, TOTP seed, etc.

    def is_complete(self) -> bool:
        return bool(self.usuario and self.password)


class BancoPlaywrightDriver(ABC):
    """Base abstracta. Cada banco implementa los `_real_*` específicos."""

    BANCO_CODIGO: str = "abstract"
    BANCO_NOMBRE: str = "Abstract Bank"
    PORTAL_URL: str = ""
    SESION_TTL_MINUTOS: int = 15
    ENV_USUARIO: str = ""   # ej. "BBVA_USUARIO"
    ENV_PASSWORD: str = ""  # ej. "BBVA_PASSWORD"
    ENV_EXTRAS: tuple[str, ...] = ()

    def __init__(
        self,
        *,
        config: DriverConfig | None = None,
        bitacora: Bitacora | None = None,
        headless: bool = False,  # default headed por 2FA asistido
    ) -> None:
        self.config = config or self._config_from_env()
        self.bitacora = bitacora or Bitacora(f"bancos_mx_{self.BANCO_CODIGO}")
        self.headless = headless
        self._sesion_iniciada_en: datetime | None = None

    @classmethod
    def from_env(cls) -> "BancoPlaywrightDriver":
        return cls(config=cls._config_from_env())

    @classmethod
    def _config_from_env(cls) -> DriverConfig:
        usuario = os.environ.get(cls.ENV_USUARIO, "").strip() or None
        password = os.environ.get(cls.ENV_PASSWORD, "") or None
        extras = {k: os.environ.get(k, "") for k in cls.ENV_EXTRAS if os.environ.get(k)}
        return DriverConfig(usuario=usuario, password=password, extra=extras)

    # ---------- mode detection ----------

    def get_mode(self) -> DriverMode:
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            return DriverMode.MOCK
        if not self.config.is_complete():
            return DriverMode.MOCK
        if os.environ.get("PLUGINS_MX_PLAYWRIGHT_REAL") != "1":
            return DriverMode.BLOCKED
        try:
            import playwright  # noqa: F401
        except ImportError:
            return DriverMode.BLOCKED
        return DriverMode.REAL

    # ---------- public API ----------

    def listar_movimientos(self, cuenta: str, dias: int = 30) -> dict[str, Any]:
        return self._dispatch("listar_movimientos", {"cuenta": cuenta, "dias": dias}, self._real_listar_movimientos)

    def descargar_estado_cuenta(
        self, cuenta: str, ejercicio: int, mes: int, formato: str = "csv"
    ) -> dict[str, Any]:
        params = {"cuenta": cuenta, "ejercicio": ejercicio, "mes": mes, "formato": formato}
        return self._dispatch("descargar_estado_cuenta", params, self._real_descargar_estado_cuenta)

    def verificar_pago_por_referencia(self, referencia: str, monto: float | str) -> dict[str, Any]:
        params = {"referencia": referencia, "monto": str(monto)}
        return self._dispatch("verificar_pago_por_referencia", params, self._real_verificar_pago_por_referencia)

    # ---------- dispatch ----------

    def _dispatch(self, op: str, params: dict[str, Any], real_impl) -> dict[str, Any]:
        mode = self.get_mode()
        safe = self._summarize_params(params)
        try:
            if mode in (DriverMode.MOCK, DriverMode.BLOCKED):
                result = self._mock_response(op, params, blocked=mode == DriverMode.BLOCKED)
                self.bitacora.log(op, success=True, params_summary=safe, result_summary={"mode": mode.value, "banco": self.BANCO_CODIGO})
                return result
            result = real_impl(params)
            self.bitacora.log(op, success=True, params_summary=safe, result_summary={"mode": "real", "banco": self.BANCO_CODIGO})
            return result
        except McpError as exc:
            self.bitacora.log(op, success=False, params_summary=safe, error=exc.to_dict())
            raise
        except Exception as exc:
            wrapped = UpstreamError(f"{self.BANCO_CODIGO}.{op} falló: {type(exc).__name__}")
            self.bitacora.log(op, success=False, params_summary=safe, error=wrapped.to_dict())
            raise wrapped from exc

    def _summarize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in params.items():
            if k == "cuenta" and isinstance(v, str):
                out["cuenta_hash"] = Bitacora.hash_sensitive(v)
            elif k == "referencia" and isinstance(v, str):
                out["referencia_hash"] = Bitacora.hash_sensitive(v)
            else:
                out[k] = v
        return out

    def _mock_response(self, op: str, params: dict[str, Any], *, blocked: bool) -> dict[str, Any]:
        notes = [f"mock — driver {self.BANCO_CODIGO} sin Playwright real"]
        if blocked:
            notes.append("credenciales detectadas pero falta PLUGINS_MX_PLAYWRIGHT_REAL=1 o playwright no instalado")

        today = datetime.now(timezone.utc).date()
        if op == "listar_movimientos":
            movs = [
                Movimiento(
                    fecha=today - timedelta(days=2),
                    tipo="deposito",
                    concepto="SPEI MOCK PROVEEDOR",
                    referencia_numerica="MOCK-001",
                    clave_rastreo_spei=f"{self.BANCO_CODIGO.upper()}-MOCK-001",
                    monto=Decimal("10000.00"),
                    saldo_resultante=Decimal("25000.00"),
                ).to_dict(),
                Movimiento(
                    fecha=today - timedelta(days=1),
                    tipo="comision",
                    concepto="COMISION MENSUAL",
                    referencia_numerica=None,
                    clave_rastreo_spei=None,
                    monto=Decimal("-150.00"),
                    saldo_resultante=Decimal("24850.00"),
                ).to_dict(),
            ]
            data = {"cuenta_hash": Bitacora.hash_sensitive(params["cuenta"]), "movimientos": movs, "total": len(movs)}
        elif op == "descargar_estado_cuenta":
            data = {
                "cuenta_hash": Bitacora.hash_sensitive(params["cuenta"]),
                "ejercicio": params["ejercicio"],
                "mes": params["mes"],
                "formato": params["formato"],
                "ruta_local": None,
            }
        elif op == "verificar_pago_por_referencia":
            data = {
                "referencia_hash": Bitacora.hash_sensitive(params["referencia"]),
                "encontrado": False,
                "monto_esperado": params["monto"],
            }
        else:
            data = {}

        return {
            "operation": op,
            "banco": self.BANCO_CODIGO,
            "data": data,
            "simulated": True,
            "real_implementation_pending": True,
            "notes": notes,
        }

    # ---------- to be overridden ----------

    @abstractmethod
    def _real_login(self) -> None:
        """Implementación del login real (varía por banco)."""

    def _real_listar_movimientos(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._mock_response("listar_movimientos", params, blocked=False)

    def _real_descargar_estado_cuenta(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._mock_response("descargar_estado_cuenta", params, blocked=False)

    def _real_verificar_pago_por_referencia(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._mock_response("verificar_pago_por_referencia", params, blocked=False)
