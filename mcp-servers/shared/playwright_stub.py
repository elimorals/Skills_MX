"""Helpers compartidos para MCPs basados en Playwright.

Los MCPs Playwright (mp_bancos_mx, mp_imss_patronal, mp_cdmx_municipal, etc.)
comparten un patrón:
1. Path mock por default (sin credenciales)
2. Path real implementaría scraping con Playwright + headless browser
3. Path real bloqueado hasta tener credenciales + tests específicos

Este módulo centraliza esa lógica para que cada MCP la herede sin duplicación.

⚠ El path Playwright real NO está implementado en este monorepo. Los portales
gubernamentales y bancarios cambian con frecuencia y construir parsers
robustos requiere semanas por portal + ser mantenidos contra breakages.
"""

from __future__ import annotations

import os
from typing import Any

from shared.errors import UpstreamError
from shared.mock import is_mock_mode, mark_simulated


def detectar_modo_playwright(credential_env_vars: list[str]) -> str:
    """Decide qué modo usar para un MCP Playwright.

    Retorna:
        "mock"      — sin credenciales o PLUGINS_MX_MOCK=1
        "real"      — credenciales presentes y PLUGINS_MX_PLAYWRIGHT_REAL=1
        "blocked"   — credenciales presentes pero PLUGINS_MX_PLAYWRIGHT_REAL no setado

    El estado "blocked" es deliberado: sin pruebas específicas contra el portal,
    el path Playwright puede romper silenciosamente. Forzar al usuario a optar
    explícitamente con PLUGINS_MX_PLAYWRIGHT_REAL=1 reduce riesgo de bugs en
    producción.
    """
    if os.environ.get("PLUGINS_MX_MOCK") == "1":
        return "mock"

    tiene_credenciales = any(
        os.environ.get(v, "").strip() for v in credential_env_vars
    )

    if not tiene_credenciales:
        return "mock"

    if os.environ.get("PLUGINS_MX_PLAYWRIGHT_REAL") == "1":
        return "real"

    return "blocked"


def mock_response_playwright(
    payload: dict[str, Any],
    portal: str,
    nota_extra: str | None = None,
) -> dict[str, Any]:
    """Marca una respuesta de Playwright MCP como simulada con nota estándar.

    Útil para que las respuestas tengan metadata consistente.
    """
    nota = (
        f"Mock — path Playwright real no implementado para {portal}. "
        f"Setear PLUGINS_MX_PLAYWRIGHT_REAL=1 + credenciales tras validar parser."
    )
    if nota_extra:
        nota = f"{nota} {nota_extra}"
    return mark_simulated(payload, nota)


def raise_playwright_real_no_implementado(portal: str) -> None:
    """Lanza UpstreamError consistente cuando alguien pide path real sin tenerlo.

    Para clientes B2B que prefieren un dict honesto (en lugar de excepción), usar
    `respuesta_real_no_implementada(portal, tool)` directamente.
    """
    raise UpstreamError(
        f"Path Playwright real para {portal} no implementado. "
        f"Setear PLUGINS_MX_MOCK=1 para forzar mock, o esperar a que se construya "
        f"el scraper con tests específicos contra el portal vigente.",
        {"portal": portal, "estado": "no_implementado"},
    )


def respuesta_real_no_implementada(portal: str, tool: str) -> dict[str, Any]:
    """Respuesta honesta cuando hay credenciales pero el path real aún no se implementa.

    Devuelve dict con checklist + siguiente paso en lugar de lanzar excepción.
    Útil para clientes B2B que activaron `PLUGINS_MX_PLAYWRIGHT_REAL=1` y quieren
    seguir operando contra mock + recibir el flag explícito.
    """
    return {
        "simulated": False,
        "real_implementado": False,
        "portal": portal,
        "tool": tool,
        "estado": "no_implementado",
        "razon": (
            f"El path Playwright real para {portal} no está implementado todavía. "
            f"Setear PLUGINS_MX_MOCK=1 para forzar respuesta mock, o cotizar "
            f"implementación específica con elimoralsmendox@gmail.com."
        ),
        "siguiente_paso": "Ver SETUP_PLAYWRIGHT_REAL.md del MCP correspondiente.",
        "credenciales_detectadas": True,
    }


def info_path_real() -> dict[str, str]:
    """Documentación standard sobre cómo activar el path Playwright real.

    Útil para devolver en tools tipo `*_status` o como parte de respuestas mock.
    """
    return {
        "como_activar_real": (
            "1. pip install playwright + playwright install chromium. "
            "2. Configurar credenciales env vars del portal. "
            "3. Setear PLUGINS_MX_PLAYWRIGHT_REAL=1. "
            "4. Validar parser contra portal vigente (puede haber cambiado)."
        ),
        "advertencia": (
            "Portales gubernamentales y bancarios cambian con frecuencia (3-6 meses). "
            "Cada path real requiere mantenimiento mensual (~4-8h por portal)."
        ),
    }
