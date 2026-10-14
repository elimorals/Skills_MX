"""Cliente unificado consulta agua municipal/estatal MX.

Ruteo por organismo:
  - consultable=True (validado en vivo): consulta real con httpx. Hoy: jmas_juarez.
  - metodo="publica_captcha": handoff humano (SIAPA: reCAPTCHA v2). Nunca se salta.
  - resto: UpstreamError explícito (consulta real no implementada/validada).
Datos simulados solo con PLUGINS_MX_MOCK=1 (marcados simulated=true).
Caché 14 días solo para respuestas reales.
"""
from __future__ import annotations

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.agua_mx import (  # noqa: E402
    OrganismoAgua,
    buscar_organismo,
    buscar_por_estado,
    estadisticas,
    listar_organismos,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import NotFoundError, UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.handoff_humano import handoff_humano  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "agua_mx"
CACHE_TTL_HOURS = 24 * 14  # 14 días — recibos bimestrales
_HEADERS = {"User-Agent": "Mozilla/5.0 (plugins-mx)"}


def _txt(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _monto(txt: str | None) -> float | None:
    if not txt:
        return None
    limpio = re.sub(r"[^\d.]", "", txt)
    return float(limpio) if limpio else None


def parse_jmas(page: str) -> dict[str, Any]:
    """Parsea pago.php de JMAS Juárez. No devuelve nombre ni dirección del titular."""
    if "No se encontró la cuenta" in page:
        raise NotFoundError("JMAS Juárez: no se encontró la cuenta o no hay información disponible.")

    def campo(label: str) -> str | None:
        m = re.search(rf"<strong>\s*{label}:?\s*</strong>(.*?)</p>", page, re.S)
        return _txt(m.group(1)) if m else None

    def tarjeta(titulo: str) -> str | None:
        m = re.search(rf"<h6>\s*{titulo}\s*</h6>\s*<h3[^>]*>(.*?)</h3>", page, re.S)
        return _txt(m.group(1)) if m else None

    saldo = _monto(tarjeta("Saldo Actual"))
    if saldo is None:
        raise UpstreamError("JMAS Juárez: respuesta sin 'Saldo Actual' (¿cambió el portal?)")
    consumo = re.search(r"([\d.]+)", tarjeta("Consumo Anterior") or "")
    conceptos = []
    detalle = re.search(r"Detalle del Cobro(.*?)</table>", page, re.S)
    if detalle:
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", detalle.group(1), re.S):
            celdas = [_txt(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(celdas) >= 2 and celdas[0].upper() != "TOTAL" and _monto(celdas[-1]) is not None:
                conceptos.append({"concepto": celdas[0], "monto_mxn": _monto(celdas[-1])})
    return {
        "adeudo_mxn": saldo,
        "estatus": "PENDIENTE" if saldo > 0 else "AL DIA",
        "vencimiento": tarjeta("Fecha de Vencimiento"),
        "consumo_m3": float(consumo.group(1)) if consumo else None,
        "estado_cuenta": campo("Estado de Cuenta"),
        "tarifa": campo("Tarifa"),
        "periodo": campo("Período"),
        "conceptos": conceptos,
    }


class AguaMxClient:
    """Cliente unificado consulta agua."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
        http: httpx.Client | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._http = http

    def consultar_adeudo(self, organismo: str, cuenta: str) -> dict[str, Any]:
        """Adeudo actual de una cuenta de agua (dato real, handoff o error explícito)."""
        org = buscar_organismo(organismo)
        if not org:
            raise NotFoundError(
                f"Organismo '{organismo}' no está en el catálogo. "
                f"Usa agua_listar_organismos() para ver opciones.",
                {"organismo_solicitado": organismo},
            )
        cuenta = cuenta.strip()
        if not cuenta:
            raise ValidationError("Cuenta requerida.")
        if not re.match(org.identificador_regex, cuenta):
            raise ValidationError(
                f"Cuenta '{cuenta}' no matchea formato esperado de {org.clave}: {org.identificador_regex}.",
                {"organismo": org.clave, "esperado": org.identificador_regex},
            )
        self._bitacora.log("consultar_adeudo", success=True, params_summary={
            "organismo": org.clave, "cuenta_hash": self._bitacora.hash_sensitive(cuenta)})

        if is_mock_mode([], default_when_no_creds=False):
            return self._mock(org, cuenta)
        if org.metodo == "publica_captcha":
            return self._handoff(org, cuenta)
        if not org.consultable:
            raise UpstreamError(
                f"Consulta real de {org.clave} no implementada/validada aún. {org.notas}".strip(),
                {"organismo": org.clave, "portal": org.url_consulta or org.url_portal, "implementado": False},
            )

        cache_key = f"{org.clave}:{cuenta}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        result = self._real_jmas(org, cuenta)  # único consultable hoy
        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        return result

    def listar_organismos(self, solo_consultables: bool = False) -> dict[str, Any]:
        orgs = listar_organismos(solo_consultables=solo_consultables)
        return {
            "total": len(orgs),
            "filtro_solo_consultables": solo_consultables,
            "organismos": [
                {
                    "clave": o.clave,
                    "nombre": o.nombre_completo,
                    "estado": o.estado,
                    "municipios_cubre": o.municipio,
                    "url_portal": o.url_portal,
                    "identificador": o.identificador_label,
                    "metodo": o.metodo,
                    "frecuencia": o.frecuencia_recibo,
                    "poblacion_aprox": o.poblacion_aprox,
                    "consultable": o.consultable,
                }
                for o in orgs
            ],
        }

    def buscar_por_estado(self, estado: str) -> dict[str, Any]:
        orgs = buscar_por_estado(estado)
        return {
            "estado_buscado": estado.upper(),
            "encontrados": len(orgs),
            "organismos": [{"clave": o.clave, "nombre": o.nombre_completo, "consultable": o.consultable} for o in orgs],
        }

    def estadisticas_catalogo(self) -> dict[str, Any]:
        return estadisticas()

    # ============================================================
    # Paths
    # ============================================================

    def _real_jmas(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        client = self._http or httpx.Client(timeout=30, headers=_HEADERS, follow_redirects=True)
        try:
            r = client.get(org.url_consulta, params={"cuenta": cuenta})
            r.raise_for_status()
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc) from exc
        finally:
            if self._http is None:
                client.close()
        return {
            "organismo": org.clave,
            "cuenta": cuenta,
            "consultado": True,
            **parse_jmas(r.text),
            "fuente": org.url_consulta,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def _handoff(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        return handoff_humano(
            portal=org.url_consulta or org.url_portal,
            motivo="captcha",
            detalle=org.notas,
            organismo=org.clave,
            pasos=[
                f"Abrir {org.url_consulta or org.url_portal}",
                f"Capturar {org.identificador_label.lower()} {cuenta} (y la clave del recibo si la pide)",
                "Resolver el CAPTCHA y continuar para ver el adeudo",
            ],
        )

    def _mock(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        """Mock determinístico por último dígito (solo PLUGINS_MX_MOCK=1)."""
        last = cuenta[-1] if cuenta else "0"
        if last in "13579":
            adeudo = float(int(last) * 145.30 + 122.50)
            estatus = "PENDIENTE" if int(last) <= 5 else "VENCIDO"
        else:
            adeudo, estatus = 0.0, "AL DIA"
        return mark_simulated({
            "organismo": org.clave,
            "cuenta": cuenta,
            "consultado": True,
            "adeudo_mxn": adeudo,
            "estatus": estatus,
            "fuente": org.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
