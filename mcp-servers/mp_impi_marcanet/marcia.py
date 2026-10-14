"""MARCia (IMPI) — búsqueda pública de marcas, https://marcia.impi.gob.mx/

Endpoints JSON observados con Playwright el 2026-10-14 (sin CAPTCHA, sin login):

1. GET  /marcas/search/quick                       → cookies JSESSIONID, SESSIONTOKEN, XSRF-TOKEN
2. POST /marcas/search/internal/record             body {"_type":"Search$Quick","query":..,"images":[]}
                                                   header X-XSRF-TOKEN = cookie XSRF-TOKEN
                                                   → {"id": <searchId>, "count": N, ...}
3. POST /marcas/search/internal/result             body {"searchId", "pageSize", "pageNumber", filtros vacíos}
                                                   → {"totalResults", "resultPage": [{id, applicationNumber,
                                                      registrationNumber, title, status, appType, owners,
                                                      dates{application, expiry, cancellation}, classes, ...}]}
"""

from __future__ import annotations

from typing import Any

import httpx

from shared.errors import UpstreamError, handle_httpx_error
from shared.http_helpers import build_ssl_verify, default_user_agent

BASE = "https://marcia.impi.gob.mx"
PORTAL_URL = f"{BASE}/marcas/search/quick"


def _json(r: httpx.Response) -> dict[str, Any]:
    try:
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise handle_httpx_error(exc) from exc
    except ValueError as exc:
        raise UpstreamError("MARCia devolvió algo que no es JSON.", {"body_preview": r.text[:300]}) from exc


def buscar(query: str, limite: int) -> dict[str, Any]:
    """Búsqueda rápida. Devuelve {"total": int, "items": [resultPage...]}."""
    with httpx.Client(
        timeout=45.0, verify=build_ssl_verify(), follow_redirects=True,
        headers={"User-Agent": default_user_agent("mp_impi_marcanet"),
                 "Accept": "application/json, text/plain, */*"},
    ) as c:
        try:
            c.get(PORTAL_URL).raise_for_status()
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc) from exc
        xsrf = c.cookies.get("XSRF-TOKEN")
        if not xsrf:
            raise UpstreamError("MARCia no entregó cookie XSRF-TOKEN; el portal cambió.", {"url": PORTAL_URL})
        h = {"X-XSRF-TOKEN": xsrf, "Origin": BASE, "Referer": PORTAL_URL}
        rec = _json(c.post(f"{BASE}/marcas/search/internal/record",
                           json={"_type": "Search$Quick", "images": [], "query": query}, headers=h))
        if "id" not in rec:
            raise UpstreamError("MARCia no devolvió searchId.", {"respuesta": rec})
        res = _json(c.post(f"{BASE}/marcas/search/internal/result", headers=h, json={
            "searchId": rec["id"], "pageSize": limite, "pageNumber": 0,
            "statusFilter": [], "viennaCodeFilter": [], "niceClassFilter": [],
        }))
    return {"total": res.get("totalResults", rec.get("count", 0)), "items": res.get("resultPage") or []}


def mapear(item: dict[str, Any]) -> dict[str, Any]:
    fechas = item.get("dates") or {}
    owners = [o.strip() for o in item.get("owners") or []]
    return {
        "expediente": item.get("id"),
        "numero_expediente": item.get("applicationNumber"),
        "numero_registro": item.get("registrationNumber"),
        "area": "MARCAS",
        "tipo_expediente": item.get("appType"),
        "denominacion": (item.get("title") or "").strip(),
        "estatus": item.get("status"),
        "titular": "; ".join(owners),
        "titulares": owners,
        "clases_niza": item.get("classes") or [],
        "fecha_solicitud": fechas.get("application"),
        "fecha_vigencia": fechas.get("expiry"),
        "imagen_url": f"{BASE}{item['images']}" if item.get("images") else None,
    }
