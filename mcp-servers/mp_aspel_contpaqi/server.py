"""mp_aspel_contpaqi — MCP para integraciones contables Aspel COI / ContPAQi.

9 tools:
- aspel_listar_polizas
- aspel_get_poliza
- aspel_obtener_balanza
- aspel_obtener_catalogo_cuentas
- aspel_obtener_estado_resultados
- aspel_obtener_balance_general
- aspel_parsear_export_csv (utility — parsea CSV pasado en línea)
- aspel_obtener_instrucciones_configuracion
- aspel_listar_catalogos

⚠ Aspel y ContPAQi son ERPs locales sin API REST pública. Modo real
requiere agente local + exports CSV en ASPEL_EXPORTS_DIR. Sin esa
configuración corre 100% mock.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_aspel_contpaqi.catalogos import (  # noqa: E402
    CODIGO_AGRUPADOR_SAT,
    CONCEPTOS_GASTOS,
    CONCEPTOS_INGRESOS,
    METODOS_EXPORTACION_ASPEL,
    METODOS_EXPORTACION_CONTPAQI,
    NATURALEZA_CUENTA,
    TIPO_POLIZA,
)
from mp_aspel_contpaqi.client import AspelContpaqiClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("aspel_contpaqi_mcp")
_client = AspelContpaqiClient()


# ---------- input models ----------


class PeriodoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ejercicio: int = Field(..., ge=2014, le=2100)
    mes: int = Field(..., ge=1, le=12)
    tipo: Optional[Literal[
        "DIARIO", "INGRESOS", "EGRESOS", "AJUSTE", "CIERRE", "APERTURA", "TRASPASO"
    ]] = None


class PeriodoSimpleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ejercicio: int = Field(..., ge=2014, le=2100)
    mes: int = Field(..., ge=1, le=12)


class PolizaIdInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    numero: str = Field(..., description="Número de póliza.", min_length=1, max_length=50)


class ParsearExportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Literal["polizas", "balanza", "catalogo_cuentas"] = Field(
        ..., description="Tipo del CSV."
    )
    contenido_csv: str = Field(
        ...,
        description="Contenido del archivo CSV como string.",
        min_length=1,
        max_length=10_000_000,  # 10 MB cap
    )


class InstruccionesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    erp: Literal["aspel_coi", "contpaqi"] = Field(
        ..., description="Cuál ERP usa el cliente."
    )


# ---------- tools ----------


@mcp.tool(
    annotations={
        "title": "Listar pólizas del periodo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def aspel_listar_polizas(args: PeriodoInput) -> dict:
    """Lista pólizas del periodo (ejercicio+mes) filtradas opcionalmente por tipo.

    Modo mock retorna 3 pólizas demo. Modo real lee `polizas_YYYYMM.csv` desde
    ASPEL_EXPORTS_DIR (genera tu ERP el export por lotes).
    """
    try:
        return _client.listar_polizas(args.ejercicio, args.mes, args.tipo)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Detalle de póliza por número",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def aspel_get_poliza(args: PolizaIdInput) -> dict:
    """Detalle de una póliza específica con todas sus líneas (cuenta/debe/haber)."""
    try:
        return _client.get_poliza(args.numero)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Balanza de comprobación del periodo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def aspel_obtener_balanza(args: PeriodoSimpleInput) -> dict:
    """Balanza de comprobación: por cuenta el saldo_inicial, cargos, abonos, saldo_final.

    Base para cualquier estado financiero (P&L, Balance General).
    """
    try:
        return _client.obtener_balanza_comprobacion(args.ejercicio, args.mes)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Catálogo completo de cuentas contables",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def aspel_obtener_catalogo_cuentas() -> dict:
    """Catálogo completo del plan de cuentas (incluye codigo SAT agrupador)."""
    try:
        return _client.obtener_catalogo_cuentas()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Estado de Resultados (Pérdidas y Ganancias) del periodo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def aspel_obtener_estado_resultados(args: PeriodoSimpleInput) -> dict:
    """Estado de Resultados calculado desde balanza (mock o export real).

    Agrega por prefijo SAT: 400=ingresos, 500=costos, 600=gastos, etc.
    """
    try:
        return _client.obtener_estado_resultados(args.ejercicio, args.mes)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Balance General del periodo",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def aspel_obtener_balance_general(args: PeriodoSimpleInput) -> dict:
    """Balance General calculado desde balanza.

    Verifica ecuación contable: Activo = Pasivo + Capital.
    """
    try:
        return _client.obtener_balance_general(args.ejercicio, args.mes)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Parsear CSV de export Aspel/ContPAQi (utility local)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def aspel_parsear_export_csv(args: ParsearExportInput) -> dict:
    """Parsea contenido CSV pasado en línea (sin red).

    Útil cuando el usuario pega un export directamente sin guardarlo en disco.
    Tipos: 'polizas', 'balanza', 'catalogo_cuentas'.
    """
    try:
        return _client.parsear_export(args.tipo, args.contenido_csv)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Instrucciones para configurar exportación en Aspel COI o ContPAQi",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def aspel_obtener_instrucciones_configuracion(
    args: InstruccionesInput,
) -> dict:
    """Devuelve instrucciones paso a paso para que el cliente configure su
    ERP a fin de generar los exports CSV que este MCP consume.
    """
    if args.erp == "aspel_coi":
        return {
            "erp": "aspel_coi",
            "pasos": [
                "1. Abrir Aspel COI 9.x o superior",
                "2. Menú Reportes → Pólizas → Lista de Pólizas",
                "3. Seleccionar rango de fechas del periodo",
                "4. Exportar a CSV (botón Exportar → CSV con encabezados)",
                "5. Guardar como 'polizas_YYYYMM.csv' (ej. polizas_202603.csv)",
                "6. Para balanza: Reportes → Estados Financieros → Balanza de Comprobación → Exportar CSV",
                "7. Guardar como 'balanza_YYYYMM.csv'",
                "8. Para catálogo: Catálogos → Cuentas → Imprimir/Exportar → CSV → 'catalogo_cuentas.csv'",
                "9. Colocar todos los CSVs en una carpeta (ej. C:\\exports\\)",
                "10. Configurar ASPEL_EXPORTS_DIR=C:\\exports\\ en el .env del MCP",
            ],
            "metodos_disponibles": METODOS_EXPORTACION_ASPEL,
            "automatizacion_sugerida": (
                "Crear un macro de Aspel o un script Python con pyodbc para "
                "automatizar la exportación diaria/mensual sin intervención manual."
            ),
        }
    if args.erp == "contpaqi":
        return {
            "erp": "contpaqi",
            "pasos": [
                "1. Abrir ContPAQi 14.x o superior",
                "2. Para pólizas: Reportes → Pólizas → Lista → Exportar a Excel",
                "3. Guardar Excel como CSV (Archivo → Guardar Como → CSV)",
                "4. Renombrar a 'polizas_YYYYMM.csv'",
                "5. Para balanza: Estados Financieros → Balanza → Exportar Excel → CSV",
                "6. Para catálogo: Catálogo de Cuentas → Imprimir → Exportar CSV",
                "7. (Opcional automation) Usar API ADD .NET COM de ContPAQi para "
                "exports automáticos. Requiere .NET y ContPAQi instalado.",
                "8. Configurar ASPEL_EXPORTS_DIR apuntando al directorio.",
            ],
            "metodos_disponibles": METODOS_EXPORTACION_CONTPAQI,
            "automatizacion_sugerida": (
                "ContPAQi expone su API ADD vía COM. Hay ejemplos en C# y VB.NET "
                "para exportar automáticamente. Más complejo que Aspel pero más robusto."
            ),
        }


@mcp.tool(
    annotations={
        "title": "Catálogos contables: tipos póliza, naturaleza, código agrupador SAT",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def aspel_listar_catalogos() -> dict:
    """Discovery offline: tipos de póliza, código agrupador SAT, conceptos típicos."""
    return {
        "tipo_poliza": TIPO_POLIZA,
        "naturaleza_cuenta": NATURALEZA_CUENTA,
        "codigo_agrupador_sat": CODIGO_AGRUPADOR_SAT,
        "conceptos_ingresos_tipicos": CONCEPTOS_INGRESOS,
        "conceptos_gastos_tipicos": CONCEPTOS_GASTOS,
        "metodos_exportacion_aspel": METODOS_EXPORTACION_ASPEL,
        "metodos_exportacion_contpaqi": METODOS_EXPORTACION_CONTPAQI,
        "nota": (
            "Código agrupador SAT (Anexo 24 RMF) es OBLIGATORIO para contabilidad "
            "electrónica. Cada cuenta auxiliar del contribuyente debe colgar de un "
            "código SAT padre. Verificar vigencia contra RMF 2026."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
