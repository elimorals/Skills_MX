"""HTTP helpers reusables — SSL gov.mx + encoding fallback.

Patrones extraídos de mp_sat_portal, mp_condusef_sipres, mp_sat_opinion_32d
después de descubrir que MUCHOS portales gov.mx comparten 2 quirks:

1. **Cadena de cert SSL incompleta** (gov.mx no manda intermediates).
   Solución: usar `truststore` (system CA bundle via Keychain en macOS o
   Linux ca-certificates), fallback a `certifi`.

2. **Encoding latin-1 sin charset declarado** (SAT, CONDUSEF).
   httpx default a UTF-8 produce U+FFFD para acentos. Solución: decodificar
   con UTF-8 strict primero, fallback a latin-1.

Reusable en futuros MCPs: REPUVE, COFEPRIS, no-antecedentes-CDMX, CJF, PNT, etc.
"""
from __future__ import annotations

from typing import Any


def build_ssl_verify() -> Any:
    """Construye verify= para httpx.Client compatible con servers gov.mx.

    Preferencia (de mejor a peor):
        1. truststore → usa el system CA bundle (Keychain macOS, ca-certs Linux)
           Crítico: muchos servers gov.mx mandan cadena de cert incompleta.
           Solo truststore detecta los intermediates instalados por el OS.
        2. certifi → CA bundle de Python (Mozilla). Funciona para la mayoría.
        3. True → default (CA bundle del OS, varía por instalación).

    Returns:
        ssl.SSLContext si truststore disponible, path str si certifi, True si fallback.

    Example:
        with httpx.Client(verify=build_ssl_verify()) as client:
            r = client.get("https://servidor-gov-mx.com/")
    """
    try:
        import ssl
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        pass
    try:
        import certifi
        return certifi.where()
    except ImportError:
        return True


def decode_response_robust(resp: Any, fallback_encoding: str = "latin-1") -> str:
    """Decodifica el body de un httpx.Response con encoding tolerante.

    Reglas (en orden):
        1. Si el server declaró charset en Content-Type → respetarlo (resp.text).
        2. Si no, intentar UTF-8 strict.
        3. Si UTF-8 falla, fallback al encoding especificado (default: latin-1).

    Args:
        resp: httpx.Response o equivalente (requiere .headers + .text + .content).
        fallback_encoding: encoding a usar si UTF-8 estricto falla. Default
            "latin-1" porque cubre SAT, CONDUSEF, y casi todos los servers
            gov.mx legacy.

    Returns:
        String decodificado correctamente.

    Example:
        with httpx.Client(verify=build_ssl_verify()) as client:
            r = client.get("https://webapps.condusef.gob.mx/...")
            body = decode_response_robust(r)
    """
    content_type = (resp.headers.get("content-type") or "").lower()
    if "charset=" in content_type:
        # Server declaró charset — httpx ya lo aplicó en .text
        return resp.text
    try:
        return resp.content.decode("utf-8")
    except UnicodeDecodeError:
        return resp.content.decode(fallback_encoding, errors="replace")


def default_user_agent(mcp_name: str, purpose: str = "compliance B2B/B2G") -> str:
    """Construye un User-Agent honesto para identificarnos ante servers gov.mx.

    Args:
        mcp_name: nombre del MCP (ej. "mp_condusef_sipres").
        purpose: descripción corta del caso de uso.

    Returns:
        "plugins-mx/{mcp_name} ({purpose})"
    """
    return f"plugins-mx/{mcp_name} ({purpose})"


__all__ = [
    "build_ssl_verify",
    "decode_response_robust",
    "default_user_agent",
]
