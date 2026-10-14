"""Handoff humano para portales públicos con CAPTCHA (grupo E1, 2026-10-14).

Regla del plan mock→real: nunca se salta un CAPTCHA. Cuando el portal oficial
lo exige, el tool hace UNA petición real (GET de la página de consulta) para
confirmar que el portal responde y que el CAPTCHA sigue ahí, y devuelve los pasos
para que una persona complete la consulta en su navegador.

Si el portal no responde o cambió (ya no aparece el marcador esperado), se
levanta `UpstreamError`: nunca se cae a datos simulados.

Los datos simulados solo existen con `PLUGINS_MX_MOCK=1` (ver `mock_forzado`).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

from shared.errors import UpstreamError

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)


def mock_forzado() -> bool:
    """Datos simulados SOLO si el usuario lo pide explícitamente."""
    return os.environ.get("PLUGINS_MX_MOCK", "").strip() == "1"


@dataclass(frozen=True)
class PortalCaptcha:
    clave: str
    nombre: str
    url: str
    captcha_tipo: str  # "imagen", "altcha", "turnstile", "recaptcha_v2", "ninguno"
    marcador: str  # regex que debe aparecer en el HTML (detecta cambios del portal)
    pasos: tuple[str, ...] = field(default_factory=tuple)
    motivo: str = "captcha"  # "captcha" | "flujo_no_automatizado"


# Validados en vivo el 2026-10-14 (ver README de cada MCP, sección "Estado real").
SAF_CDMX_ADEUDOS = PortalCaptcha(
    clave="saf_cdmx_adeudos",
    nombre="SAF CDMX — Consulta ciudadana de adeudos vehiculares",
    url="https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana",
    captcha_tipo="imagen",
    marcador=r'id="captcha_code"',
    pasos=(
        "Abre la URL en tu navegador.",
        "Escribe la placa sin espacios ni guiones en 'Placa'.",
        "Escribe el texto de la imagen CAPTCHA y pulsa 'Buscar'.",
        "Revisa las pestañas Tenencia, Infracciones, Sanciones ambientales y Fotocívicas.",
    ),
)

OVICA_CDMX_PREDIAL = PortalCaptcha(
    clave="ovica_cdmx_predial",
    nombre="Oficina Virtual del Catastro CDMX (OVICA) — liquidación predial",
    url="https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion",
    captcha_tipo="altcha",
    marcador=r"altcha",
    pasos=(
        "Abre la URL en tu navegador.",
        "Captura la cuenta predial (12 caracteres alfanuméricos de tu boleta).",
        "Completa la verificación ALTCHA y consulta el adeudo por bimestre.",
    ),
)

EDOMEX_INFRACCIONES = PortalCaptcha(
    clave="edomex_infracciones",
    nombre="Secretaría de Seguridad EdoMex — consulta de infracciones",
    url="https://infracciones.ssedomex.gob.mx/Search",
    captcha_tipo="turnstile",
    marcador=r"challenges\.cloudflare\.com/turnstile",
    pasos=(
        "Abre la URL en tu navegador.",
        "Elige tipo de documento (placa, permiso o serie) y captúralo.",
        "Completa la verificación de Cloudflare y consulta.",
    ),
)

EDOMEX_RECAUDACION = PortalCaptcha(
    clave="edomex_recaudacion",
    nombre="Portal de Servicios al Contribuyente EdoMex (tenencia/refrendo)",
    url="https://pagosytramites.edomex.gob.mx/recaudacion/",
    captcha_tipo="no_verificado",
    marcador=r"Portal de Servicios al Contribuyente",
    motivo="flujo_no_automatizado",
    pasos=(
        "Abre la URL en tu navegador.",
        "Entra a Control Vehicular / Tenencia y captura placa y los últimos dígitos del NIV.",
        "Completa la verificación que pida el portal y genera el formato de pago si hay adeudo.",
    ),
)

SAN_PEDRO_MULTAS = PortalCaptcha(
    clave="sanpedro_multas",
    nombre="Tesorería San Pedro Garza García — multas de tránsito",
    url="https://aplicativos.sanpedro.gob.mx/esanpedro/multas/multasnew.asp",
    captcha_tipo="recaptcha_v2",
    marcador=r"g-recaptcha",
    pasos=(
        "Abre la URL en tu navegador.",
        "Captura la placa sin espacios ni guiones.",
        "Marca el reCAPTCHA y consulta.",
    ),
)

JALISCO_ADEUDOS = PortalCaptcha(
    clave="jal_adeudos_vehiculares",
    nombre="Gobierno en Línea Jalisco — adeudos vehiculares",
    url="https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos",
    captcha_tipo="recaptcha_v2",
    marcador=r"g-recaptcha",
    pasos=(
        "Abre la URL en tu navegador.",
        "Captura placa, número de serie, nombre y motor como aparecen en la tarjeta de circulación.",
        "Marca el reCAPTCHA y consulta.",
    ),
)

ICVNL_ESTADO_CUENTA = PortalCaptcha(
    clave="icvnl_estado_cuenta",
    nombre="Instituto de Control Vehicular NL — estado de cuenta",
    url="https://www.icvnl.gob.mx/estadodecuenta",
    captcha_tipo="no_verificado",
    marcador=r"Instituto de Control Vehicular",
    motivo="flujo_no_automatizado",
    pasos=(
        "Abre la URL en tu navegador.",
        "Consulta el estado de cuenta de refrendo por placa.",
        "Las multas de tránsito en NL son municipales: consulta el portal de tu municipio.",
    ),
)

IGECEM_EDOMEX = PortalCaptcha(
    clave="igecem_edomex",
    nombre="IGECEM — catastro del Estado de México",
    url="https://igecem.edomex.gob.mx",
    captcha_tipo="no_verificado",
    marcador=r"IGECEM|Instituto de Informaci",
    motivo="flujo_no_automatizado",
    pasos=(
        "IGECEM no publica consulta de valor catastral por clave sin trámite.",
        "Solicita la constancia/certificación catastral en IGECEM o consulta el valor en tu boleta predial municipal.",
    ),
)


def verificar_portal(portal: PortalCaptcha, *, timeout: float = 30.0) -> dict[str, Any]:
    """GET real a la página de consulta. Lanza UpstreamError si no sirve."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True,
                          headers={"User-Agent": USER_AGENT}) as http:
            r = http.get(portal.url)
    except httpx.HTTPError as e:
        raise UpstreamError(
            f"Portal {portal.nombre} no respondió: {type(e).__name__}",
            {"url": portal.url},
        ) from e
    if r.status_code != 200:
        raise UpstreamError(
            f"Portal {portal.nombre} respondió HTTP {r.status_code}.",
            {"url": portal.url, "status_code": r.status_code},
        )
    if not re.search(portal.marcador, r.text, re.IGNORECASE):
        raise UpstreamError(
            f"Portal {portal.nombre} cambió: ya no aparece el marcador esperado. "
            "Revisar el flujo antes de seguir enviando usuarios ahí.",
            {"url": portal.url, "marcador": portal.marcador},
        )
    return {
        "url": str(r.url),
        "status_code": r.status_code,
        "verificado_en": datetime.now(timezone.utc).isoformat(),
    }


def armar_handoff(
    *,
    motivo: str,
    pasos: list[str] | tuple[str, ...],
    url: str | None = None,
    portal: str | None = None,
    detalle: str = "",
    captcha_tipo: str | None = None,
    campos_prellenados: dict[str, Any] | None = None,
    portal_verificado: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Única forma de salida de un handoff humano en todos los MCPs.

    `motivo` es un código corto: captcha | login | bot_manager | flujo_no_automatizado |
    envio_manual | sin_verificador_publico | sin_consulta_publica | accion_del_titular |
    requiere_lista_oficial | bloqueo_portal. La explicación en texto va en `detalle`.
    """
    return {
        "requiere_humano": True,
        "status": "requiere_humano",
        "consultado": False,
        "simulated": False,
        "motivo": motivo,
        "detalle": detalle,
        "portal": portal,
        "url": url,
        "pasos": list(pasos),
        "captcha_tipo": captcha_tipo,
        "campos_prellenados": campos_prellenados or {},
        "portal_verificado": portal_verificado,
        **extra,
    }


def handoff_humano(portal: PortalCaptcha, **extra: Any) -> dict[str, Any]:
    """Respuesta real (no simulada): el portal está arriba y requiere a una persona."""
    evidencia = verificar_portal(portal)
    detalle = (
        f"El portal oficial exige CAPTCHA ({portal.captcha_tipo}); no se automatiza."
        if portal.motivo == "captcha"
        else "El flujo del portal oficial no está automatizado; consulta manual."
    )
    return armar_handoff(
        motivo=portal.motivo,
        detalle=detalle,
        portal=portal.nombre,
        url=portal.url,
        pasos=portal.pasos,
        captcha_tipo=portal.captcha_tipo,
        portal_verificado=evidencia,
        **extra,
    )


__all__ = [
    "PortalCaptcha", "mock_forzado", "verificar_portal", "handoff_humano", "armar_handoff",
    "SAF_CDMX_ADEUDOS", "OVICA_CDMX_PREDIAL", "EDOMEX_INFRACCIONES",
    "EDOMEX_RECAUDACION", "SAN_PEDRO_MULTAS", "JALISCO_ADEUDOS",
    "ICVNL_ESTADO_CUENTA", "IGECEM_EDOMEX",
]
