"""Helper genérico para portales municipales de predial / tenencia / multas.

Todos los portales municipales mexicanos siguen un patrón similar:
1. Carga página con formulario
2. Llena input con cuenta predial o placa
3. Click en botón "Consultar"
4. Espera tabla de resultados
5. Parsea filas: concepto / bimestre / monto

Este módulo encapsula ese patrón con configuración por municipio.

USO:
    from shared.playwright_municipal_generic import consulta_portal, PortalConfig

    config = PortalConfig(
        url="https://recaudacion.queretaro.gob.mx/predial",
        input_selectors=["input[name='cuenta']", "input#cuenta"],
        submit_selectors=["button[type='submit']", "button:has-text('Consultar')"],
        result_selector="table.resultados",
        identificador_etiqueta="cuenta_predial",
    )
    resultado = consulta_portal(config, identificador="12345678")

⚠ Selectores CSS varían por portal. Cada municipal/playwright_real.py debe
proveer su PortalConfig específico. El helper hace fallback graceful si los
selectores no matchean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from shared.errors import UpstreamError
from shared.playwright_real import (
    playwright_session,
    safe_text,
    parse_precio_mxn,
)


@dataclass
class PortalConfig:
    """Configuración de un portal municipal para scraping genérico."""
    url: str
    """URL del formulario de consulta."""

    input_selectors: list[str] = field(default_factory=list)
    """Lista de selectores CSS para el input principal (primero que matchee gana)."""

    submit_selectors: list[str] = field(default_factory=list)
    """Lista de selectores CSS para el botón submit."""

    result_selector: str = "table"
    """Selector CSS del contenedor de resultados."""

    identificador_etiqueta: str = "identificador"
    """Cómo llamar al input en la respuesta (cuenta_predial, placa, etc.)."""

    timeout_ms: int = 20000
    """Timeout esperando resultados después del submit."""

    columna_concepto: int = 0
    """Índice de la columna con el nombre del concepto/bimestre."""

    columna_monto: int = -1
    """Índice de la columna con el monto (negativo para contar desde el final)."""

    extra_inputs: dict[str, str] = field(default_factory=dict)
    """Inputs adicionales (ej. ejercicio: "2026", municipio: "Toluca") — selector → valor."""


def consulta_portal(
    config: PortalConfig,
    identificador: str,
    extra_log: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Ejecuta el flujo genérico de consulta sobre un portal municipal.

    Returns:
        dict con: {identificador_etiqueta, estatus, adeudo_total_mxn, conceptos, url}

    Raises:
        UpstreamError si el portal no responde o cambió de estructura.
    """
    with playwright_session() as page:
        try:
            page.goto(config.url, wait_until="domcontentloaded")
        except Exception as e:
            raise UpstreamError(
                f"No se pudo cargar portal {config.url}: {e}",
                {"url": config.url},
            )

        # Llenar input principal
        filled = False
        for sel in config.input_selectors:
            try:
                page.locator(sel).first.fill(identificador)
                filled = True
                break
            except Exception:
                continue
        if not filled:
            raise UpstreamError(
                f"No se encontró input principal en {config.url} "
                f"(intentados: {config.input_selectors})",
                {"identificador_truncado": identificador[:5] + "***"},
            )

        # Llenar inputs extra si aplica (ej. ejercicio, municipio)
        for sel, value in config.extra_inputs.items():
            try:
                page.locator(sel).first.fill(value)
            except Exception:
                # No fatal — algunos portales hacen estos opcionales
                pass

        # Submit
        submitted = False
        for sel in config.submit_selectors:
            try:
                page.locator(sel).first.click()
                submitted = True
                break
            except Exception:
                continue
        if not submitted:
            page.keyboard.press("Enter")

        # Esperar resultados
        try:
            page.wait_for_selector(config.result_selector, timeout=config.timeout_ms)
        except Exception as e:
            raise UpstreamError(
                f"Timeout esperando resultados en {config.url}: {e}",
                {"identificador_truncado": identificador[:5] + "***"},
            )

        # Parsear tabla
        conceptos = []
        rows = page.locator(f"{config.result_selector} tr").all()
        for row in rows[:50]:
            celdas = row.locator("td").all()
            if len(celdas) < 2:
                continue

            concepto = safe_text(celdas[config.columna_concepto])
            idx_monto = config.columna_monto if config.columna_monto >= 0 else len(celdas) + config.columna_monto
            if 0 <= idx_monto < len(celdas):
                monto_txt = safe_text(celdas[idx_monto])
                monto = parse_precio_mxn(monto_txt)
            else:
                monto = None

            if concepto and monto is not None and monto > 0:
                conceptos.append({
                    "concepto": concepto,
                    "monto_mxn": monto,
                })

        adeudo_total = sum(c["monto_mxn"] for c in conceptos)
        estatus = "al_corriente" if adeudo_total == 0 else "con_adeudo"

        return {
            config.identificador_etiqueta: identificador,
            "estatus": estatus,
            "adeudo_total_mxn": adeudo_total,
            "conceptos_pendientes": len(conceptos),
            "conceptos": conceptos,
            "url_consultada": config.url,
        }
