"""Cliente orquestador para Aspel COI / ContPAQi.

Estrategia:
- NO hay API REST pública. Aspel y ContPAQi son ERPs LOCALES en SQL Server
  y .NET COM respectivamente. Acceso real requiere:
  1) Agente local (corriendo en la red del cliente)
  2) Conexión ODBC al SQL Server (Aspel)
  3) Componentes ADD .NET COM (ContPAQi, solo Windows)

- Path real: parsear EXPORTS que el ERP genera (CSV/Excel/XML).
- Path mock: respuestas plausibles para development.

Este MCP expone tools que:
- En modo mock: retornan datos demo
- Con `ASPEL_EXPORTS_DIR` configurado: leen exports CSV del directorio

⚠ Para producción real lo correcto es un agente local en la red del cliente
que exponga estos exports vía HTTPS al MCP. Fuera del alcance default.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Make shared/ importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, UpstreamError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

from mp_aspel_contpaqi import export_parser, mock_data  # noqa: E402


NAMESPACE = "aspel_contpaqi_mcp"

CRED_ENV_VARS = ["ASPEL_EXPORTS_DIR", "CONTPAQI_AGENT_URL"]


class AspelContpaqiClient:
    """Cliente con dos modos:
    - mock: respuestas demo
    - exports: parsea archivos CSV en ASPEL_EXPORTS_DIR
    """

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._exports_dir = os.environ.get("ASPEL_EXPORTS_DIR", "").strip()

    def _mock(self) -> bool:
        return is_mock_mode(CRED_ENV_VARS)

    def _exports_path(self) -> Path | None:
        if not self._exports_dir:
            return None
        p = Path(self._exports_dir).expanduser()
        return p if p.exists() else None

    def _log(self, op: str, payload: dict[str, Any], *, success: bool = True) -> None:
        self._bitacora.log(op, success=success, params_summary=payload)

    def _read_export_file(self, filename: str) -> str | None:
        """Lee un archivo de export desde ASPEL_EXPORTS_DIR. None si no existe."""
        root = self._exports_path()
        if not root:
            return None
        p = root / filename
        if not p.exists():
            return None
        try:
            return p.read_text(encoding="utf-8-sig")  # tolerate BOM
        except (OSError, UnicodeDecodeError):
            return None

    # ---------- tools ----------

    def listar_polizas(
        self, ejercicio: int, mes: int, tipo: str | None = None
    ) -> dict[str, Any]:
        """Lista pólizas del periodo. Mock o parseo de export."""
        self._log("listar_polizas", {"ejercicio": ejercicio, "mes": mes, "tipo": tipo})

        if self._mock():
            return mark_simulated(
                mock_data.mock_polizas(ejercicio, mes, tipo),
                "Modo mock — no hay export real disponible.",
            )

        filename = f"polizas_{ejercicio}{mes:02d}.csv"
        contenido = self._read_export_file(filename)
        if contenido is None:
            return mark_simulated(
                mock_data.mock_polizas(ejercicio, mes, tipo),
                f"Archivo de export '{filename}' no encontrado en ASPEL_EXPORTS_DIR. "
                f"Usando demo.",
            )

        polizas = export_parser.parsear_csv_polizas(contenido)
        if tipo:
            polizas = [p for p in polizas if p.get("tipo", "").upper() == tipo.upper()]
        return {
            "ejercicio": ejercicio,
            "mes": mes,
            "tipo_filtrado": tipo,
            "total_polizas": len(polizas),
            "polizas": polizas,
            "fuente": str(self._exports_dir),
            "simulated": False,
        }

    def get_poliza(self, numero: str) -> dict[str, Any]:
        """Detalle de póliza por número."""
        self._log("get_poliza", {"numero": numero})

        if self._mock():
            return mark_simulated(mock_data.mock_poliza_detalle(numero))

        # En modo real, buscar en todos los archivos polizas_*.csv (search lineal)
        root = self._exports_path()
        if not root:
            raise UpstreamError(
                "ASPEL_EXPORTS_DIR no configurado. Define la ruta a los exports CSV."
            )
        for f in sorted(root.glob("polizas_*.csv")):
            try:
                polizas = export_parser.parsear_csv_polizas(f.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            for p in polizas:
                if p.get("numero") == numero:
                    return {**p, "fuente": f.name, "simulated": False}
        raise NotFoundError(f"Póliza {numero} no encontrada en exports.")

    def obtener_balanza_comprobacion(
        self, ejercicio: int, mes: int
    ) -> dict[str, Any]:
        """Balanza de comprobación del periodo."""
        self._log("obtener_balanza", {"ejercicio": ejercicio, "mes": mes})

        if self._mock():
            return mark_simulated(mock_data.mock_balanza(ejercicio, mes))

        filename = f"balanza_{ejercicio}{mes:02d}.csv"
        contenido = self._read_export_file(filename)
        if contenido is None:
            return mark_simulated(
                mock_data.mock_balanza(ejercicio, mes),
                f"Archivo '{filename}' no encontrado — usando demo.",
            )

        cuentas = export_parser.parsear_csv_balanza(contenido)
        return {
            "ejercicio": ejercicio,
            "mes": mes,
            "fecha_corte": None,
            "cuentas": cuentas,
            "total_cuentas": len(cuentas),
            "fuente": filename,
            "simulated": False,
        }

    def obtener_catalogo_cuentas(self) -> dict[str, Any]:
        """Catálogo completo de cuentas contables."""
        self._log("obtener_catalogo_cuentas", {})

        if self._mock():
            return mark_simulated(mock_data.mock_catalogo_cuentas())

        contenido = self._read_export_file("catalogo_cuentas.csv")
        if contenido is None:
            return mark_simulated(
                mock_data.mock_catalogo_cuentas(),
                "catalogo_cuentas.csv no encontrado — usando demo.",
            )

        cuentas = export_parser.parsear_csv_catalogo_cuentas(contenido)
        return {
            "total_cuentas": len(cuentas),
            "cuentas": cuentas,
            "fuente": "catalogo_cuentas.csv",
            "simulated": False,
        }

    def obtener_estado_resultados(
        self, ejercicio: int, mes: int
    ) -> dict[str, Any]:
        """Estado de resultados (P&L) calculado desde balanza."""
        self._log("obtener_estado_resultados", {"ejercicio": ejercicio, "mes": mes})

        if self._mock():
            return mark_simulated(mock_data.mock_estado_resultados(ejercicio, mes))

        # En modo real, calcular desde balanza
        balanza = self.obtener_balanza_comprobacion(ejercicio, mes)
        return self._calcular_estado_resultados_de_balanza(balanza, ejercicio, mes)

    def obtener_balance_general(
        self, ejercicio: int, mes: int
    ) -> dict[str, Any]:
        """Balance general calculado desde balanza."""
        self._log("obtener_balance_general", {"ejercicio": ejercicio, "mes": mes})

        if self._mock():
            return mark_simulated(mock_data.mock_balance_general(ejercicio, mes))

        balanza = self.obtener_balanza_comprobacion(ejercicio, mes)
        return self._calcular_balance_de_balanza(balanza, ejercicio, mes)

    # ---------- utilidades de parseo (sin red) ----------

    def parsear_export(
        self, tipo: str, contenido_csv: str
    ) -> dict[str, Any]:
        """Parsea contenido CSV pasado directamente. Sin red.

        tipo ∈ {polizas, balanza, catalogo_cuentas}
        """
        tipo_norm = tipo.lower().strip()
        if tipo_norm == "polizas":
            data = export_parser.parsear_csv_polizas(contenido_csv)
            return {"tipo": "polizas", "total": len(data), "data": data}
        if tipo_norm == "balanza":
            data = export_parser.parsear_csv_balanza(contenido_csv)
            return {"tipo": "balanza", "total": len(data), "data": data}
        if tipo_norm in ("catalogo_cuentas", "catalogo", "cuentas"):
            data = export_parser.parsear_csv_catalogo_cuentas(contenido_csv)
            return {"tipo": "catalogo_cuentas", "total": len(data), "data": data}
        raise McpError(
            f"Tipo desconocido: {tipo}. Usar: polizas, balanza, catalogo_cuentas.",
            {"received": tipo},
        )

    # ---------- helpers de cálculo ----------

    def _calcular_estado_resultados_de_balanza(
        self, balanza: dict[str, Any], ejercicio: int, mes: int
    ) -> dict[str, Any]:
        """Agrega cuentas de resultados según prefijo SAT (400/500/600/700/800)."""
        from decimal import Decimal

        ingresos = Decimal("0")
        costo_ventas = Decimal("0")
        gastos = Decimal("0")
        otros_ingresos = Decimal("0")
        otros_gastos = Decimal("0")

        for cuenta in balanza.get("cuentas", []):
            saldo = Decimal(cuenta.get("saldo_final", "0"))
            codigo = cuenta.get("cuenta", "")
            prefijo = codigo.split("-")[0] if "-" in codigo else codigo[:3]
            if prefijo.startswith("4"):
                # Cuentas acreedoras → saldo negativo = ingreso
                ingresos += abs(saldo)
            elif prefijo.startswith("5"):
                costo_ventas += abs(saldo)
            elif prefijo.startswith("6"):
                gastos += abs(saldo)
            elif prefijo.startswith("7"):
                otros_ingresos += abs(saldo)
            elif prefijo.startswith("8"):
                otros_gastos += abs(saldo)

        utilidad_bruta = ingresos - costo_ventas
        utilidad_operacion = utilidad_bruta - gastos
        utilidad_antes_impuestos = utilidad_operacion + otros_ingresos - otros_gastos
        return {
            "ejercicio": ejercicio,
            "mes": mes,
            "ingresos": str(ingresos),
            "costo_ventas": str(costo_ventas),
            "utilidad_bruta": str(utilidad_bruta),
            "gastos_generales": str(gastos),
            "utilidad_operacion": str(utilidad_operacion),
            "otros_ingresos": str(otros_ingresos),
            "otros_gastos": str(otros_gastos),
            "utilidad_antes_impuestos": str(utilidad_antes_impuestos),
            "impuestos": "0.00",
            "utilidad_neta": str(utilidad_antes_impuestos),
            "simulated": False,
        }

    def _calcular_balance_de_balanza(
        self, balanza: dict[str, Any], ejercicio: int, mes: int
    ) -> dict[str, Any]:
        """Agrega cuentas de balance por prefijo SAT (100/200/300)."""
        from decimal import Decimal

        activo = Decimal("0")
        pasivo = Decimal("0")
        capital = Decimal("0")

        for cuenta in balanza.get("cuentas", []):
            saldo = Decimal(cuenta.get("saldo_final", "0"))
            codigo = cuenta.get("cuenta", "")
            prefijo = codigo.split("-")[0] if "-" in codigo else codigo[:3]
            if prefijo.startswith("1"):
                activo += saldo
            elif prefijo.startswith("2"):
                pasivo += abs(saldo)
            elif prefijo.startswith("3"):
                capital += abs(saldo)

        ecuacion_cuadra = activo == (pasivo + capital)
        return {
            "ejercicio": ejercicio,
            "mes": mes,
            "activo": {"total": str(activo)},
            "pasivo": {"total": str(pasivo)},
            "capital": {"total": str(capital)},
            "total_pasivo_capital": str(pasivo + capital),
            "ecuacion_contable_cuadra": ecuacion_cuadra,
            "simulated": False,
        }
