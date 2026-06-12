#!/usr/bin/env python3
"""Valida que las credenciales de Facturama estén configuradas y funcionen.

Uso:
    python scripts/validar_facturama_credenciales.py
    python scripts/validar_facturama_credenciales.py --env sandbox
    python scripts/validar_facturama_credenciales.py --env production

Variables de entorno requeridas:
    FACTURAMA_USER          o   FACTURAMA_API_KEY
    FACTURAMA_PASSWORD       (si usas FACTURAMA_USER)
    FACTURAMA_ENV           (sandbox|production, default: sandbox)

Pasos del script:
    1. Detecta variables de entorno presentes y reporta cuáles faltan
    2. Determina el endpoint correcto (sandbox vs production)
    3. Hace un GET de health-check al endpoint /api-lite/products
       (endpoint público que requiere auth válida)
    4. Reporta éxito o el error específico (auth/network/etc.)

Este script NO timbra CFDIs. Solo verifica que las credenciales son válidas.
Para un timbrado de prueba real, usar el comando /core:timbrar-cfdi en
Claude Code con FACTURAMA_ENV=sandbox.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from typing import Literal

try:
    import httpx
except ImportError:
    print("✗ httpx no instalado. Ejecutar: pip install httpx", file=sys.stderr)
    sys.exit(1)


SANDBOX_URL = "https://apisandbox.facturama.mx"
PROD_URL = "https://api.facturama.mx"
HEALTH_ENDPOINT = "/api-lite/products"  # endpoint barato que requiere auth


def fmt_status(ok: bool, label: str, detail: str = "") -> str:
    icon = "✓" if ok else "✗"
    color = "\033[92m" if ok else "\033[91m"
    reset = "\033[0m"
    line = f"{color}{icon}{reset} {label}"
    if detail:
        line += f": {detail}"
    return line


def check_env_vars() -> tuple[str | None, str | None]:
    """Detecta credenciales en env vars. Retorna (user, password)."""
    user = os.environ.get("FACTURAMA_USER") or os.environ.get("FACTURAMA_API_KEY")
    password = os.environ.get("FACTURAMA_PASSWORD")
    return user, password


def check_endpoint(
    user: str,
    password: str,
    env: Literal["sandbox", "production"],
) -> tuple[bool, str]:
    """Hace una petición HTTP autenticada para verificar credenciales."""
    base_url = SANDBOX_URL if env == "sandbox" else PROD_URL
    url = f"{base_url}{HEALTH_ENDPOINT}"
    creds = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {creds}",
        "Accept": "application/json",
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=headers)
    except httpx.TimeoutException:
        return False, "Timeout — endpoint no respondió en 15s"
    except httpx.RequestError as exc:
        return False, f"Network error: {exc.__class__.__name__}"

    if resp.status_code == 200:
        return True, f"HTTP 200 — credenciales válidas en {env}"
    if resp.status_code == 401:
        return False, "HTTP 401 — usuario/password rechazados por Facturama"
    if resp.status_code == 403:
        return False, "HTTP 403 — credenciales válidas pero sin permisos"
    if resp.status_code == 404:
        return False, f"HTTP 404 — endpoint {HEALTH_ENDPOINT} no existe. Facturama puede haber cambiado API"
    return False, f"HTTP {resp.status_code} — {resp.text[:200]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida credenciales Facturama")
    parser.add_argument(
        "--env",
        choices=["sandbox", "production"],
        default=None,
        help="Forzar entorno (default: leer de FACTURAMA_ENV o sandbox)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Validación de credenciales Facturama")
    print("=" * 60)

    # 1. Variables de entorno
    user, password = check_env_vars()
    env = args.env or os.environ.get("FACTURAMA_ENV", "sandbox").lower()

    print()
    print("1. Variables de entorno:")
    print(fmt_status(user is not None, "FACTURAMA_USER o FACTURAMA_API_KEY"))
    print(fmt_status(password is not None, "FACTURAMA_PASSWORD"))
    print(f"  ℹ FACTURAMA_ENV: {env}")

    if not user or not password:
        print()
        print("Faltan credenciales. Configurar en .env o variable de entorno:")
        print("  export FACTURAMA_USER='tu_usuario_o_api_key'")
        print("  export FACTURAMA_PASSWORD='tu_password'")
        print("  export FACTURAMA_ENV='sandbox'  # o 'production'")
        print()
        print("Crear cuenta sandbox gratis: https://facturama.mx")
        return 1

    # 2. Conectividad
    print()
    print(f"2. Conectividad con Facturama ({env}):")
    base_url = SANDBOX_URL if env == "sandbox" else PROD_URL
    print(f"  ℹ Endpoint: {base_url}")

    ok, detail = check_endpoint(user, password, env)
    print(fmt_status(ok, "Auth + endpoint", detail))

    if not ok:
        print()
        print("Diagnóstico:")
        if "401" in detail:
            print("  → Revisar usuario y password. Si usas API key, asegurarte de")
            print("    pasarla como FACTURAMA_USER (con FACTURAMA_PASSWORD vacío o")
            print("    igual a API key según docs Facturama).")
        elif "Network" in detail or "Timeout" in detail:
            print("  → Verificar conexión a internet o firewall corporativo.")
            print(f"  → Probar: curl -u $FACTURAMA_USER:$FACTURAMA_PASSWORD {base_url}{HEALTH_ENDPOINT}")
        elif "404" in detail:
            print("  → Endpoint puede haber cambiado. Revisar docs Facturama 2026.")
        return 1

    # 3. Resumen
    print()
    print("=" * 60)
    print(f"✓ Credenciales Facturama válidas en {env.upper()}")
    print("=" * 60)
    print()
    print("Siguientes pasos:")
    print(f"  1. Confirmar FACTURAMA_ENV={env} en tu .env")
    print("  2. Reiniciar Claude Code para que mp_facturama_extendido detecte env vars")
    print("  3. Probar timbrado de prueba:")
    print("       /core:timbrar-cfdi receptor IBM970131DRA, consultoría $1000")
    print()
    if env == "sandbox":
        print("⚠ Estás en SANDBOX — los CFDIs no tienen valor fiscal real.")
        print("  Hacer 100+ timbrados de prueba antes de cambiar a production.")
    else:
        print("🚨 Estás en PRODUCCIÓN — los CFDIs SÍ son válidos ante SAT.")
        print("  Cada timbre cuesta dinero ($0.50-$3 MXN según plan).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
