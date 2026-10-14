"""Consulta RENAPO — verificación de existencia en padrón oficial.

Portal oficial: https://www.gob.mx/curp/ (Ember; verificado 2026-10-14 en navegador,
bundle `assets/tramite-curp-*.js`):
- Consulta: POST https://www.gob.mx/v1/renapoCURP/consulta (JSON).
  - Por CURP:  {"curp", "tipoBusqueda": "curp", "ip": "127.0.0.1", "token"}
  - Por datos: {"nombres", "primerApellido", "segundoApellido", "diaNacimiento",
    "mesNacimiento", "selectedYear", "fechaNacimiento": "dd/mm/aaaa",
    "sexo": H|M|X, "claveEntidad", "tipoBusqueda": "datos", "ip", "token"}
  - Respuesta: {"codigo": "01" = éxito, "mensaje", "registros": [...]}.
- reCAPTCHA Enterprise score-based: sitekey 6Lfi0jcpAAAAAPfBiQkGzQR3gv8mDRkqPDHAy8hS,
  action "CONSULTA"; el token viaja en el body como `token`.
- www.gob.mx (página Y API) está detrás del challenge "crypto" de Akamai
  (`Challenge Validation`, proof-of-work en JS). httpx recibe el challenge en
  cualquier GET, también con cookies sembradas: no se evade (sin stealth ni sensores).

Modos:
- Solver apagado: **handoff humano** (URL, pasos, datos prellenados).
- Solver opt-in (`solver_activo("curp_renapo")`): GET previo a la página; si aparece el
  challenge de Akamai → handoff con `bloqueo_antibot: "akamai"` (no se gasta captcha).
  Si el portal deja de exigirlo: token Enterprise → consulta real → parseo.
- Los resultados reales NO se cachean (datos de terceros); la bitácora solo guarda hashes.

Mock solo con PLUGINS_MX_MOCK=1 (respuestas `simulated: true`).
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_curp_renapo.catalogos import ESTADOS_CURP  # noqa: E402
from mp_curp_renapo.validacion import (  # noqa: E402
    derivar_estado,
    derivar_fecha_nacimiento,
    derivar_sexo,
    validar_estructura,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.captcha_solver import (  # noqa: E402
    CaptchaSolver,
    TokenRechazado,
    con_token,
    extraer_sitekey,
    solver_activo,
)
from shared.errors import UpstreamError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import USER_AGENT, armar_handoff  # noqa: E402

NAMESPACE = "curp_renapo_mcp"
CACHE_DIAS = 90


PORTAL_URL = "https://www.gob.mx/curp/"
API_CONSULTA = "https://www.gob.mx/v1/renapoCURP/consulta"
SITEKEY = "6Lfi0jcpAAAAAPfBiQkGzQR3gv8mDRkqPDHAy8hS"
RECAPTCHA_ACCION = "CONSULTA"
PORTAL_SOLVER = "curp_renapo"
# Marcadores del challenge "crypto" de Akamai (página y API, 2026-10-14).
_AKAMAI = re.compile(r"Challenge Validation|sec-cpt-if|/_sec/verify", re.IGNORECASE)
_ACENTOS = str.maketrans("ÁÉÍÓÚÜ", "AEIOUU")
AVISO_PRIVACIDAD = (
    "Contiene datos personales de terceros: consultarlos y usarlos requiere base legal "
    "(LFPDPPP: consentimiento o excepción del art. 10) y finalidad informada. No se guardan en caché."
)


def handoff_renapo(
    curp: str | None, motivo: str = "consulta", campos: dict[str, Any] | None = None, **extra: Any,
) -> dict[str, Any]:
    """RENAPO exige reCAPTCHA Enterprise + challenge Akamai: lo completa una persona."""
    if campos is None:
        pasos = [
            "Abrir https://www.gob.mx/curp/ en un navegador.",
            "Elegir la pestaña 'Clave Única de Registro de Población' y pegar la CURP.",
            "Completar la verificación de seguridad (reCAPTCHA) y pulsar 'Buscar'.",
        ]
    else:
        pasos = [
            "Abrir https://www.gob.mx/curp/ en un navegador.",
            "Elegir la pestaña 'Datos personales' y capturar los datos prellenados.",
            "Completar la verificación de seguridad (reCAPTCHA) y pulsar 'Buscar'.",
        ]
    if motivo == "constancia":
        pasos.append("En el resultado, pulsar 'Descargar PDF' para obtener la constancia.")
    return armar_handoff(
        motivo="captcha",
        url=PORTAL_URL,
        pasos=pasos,
        campos_prellenados=campos if campos is not None else {"curp": curp},
        **extra,
    )


def _texto_portal(texto: str) -> str:
    """Como `omitirAcentos(val.toUpperCase()).trim()` del bundle (conserva la Ñ)."""
    return texto.strip().upper().translate(_ACENTOS)


def payload_datos(
    nombres: str, primer_apellido: str, segundo_apellido: str,
    fecha_nacimiento: date, sexo: str, clave_entidad: str,
) -> dict[str, str]:
    """Body del modo 'datos' tal como lo arma el bundle del portal (sin ip/token)."""
    sexo, clave_entidad = sexo.strip().upper(), clave_entidad.strip().upper()
    if sexo not in ("H", "M", "X"):
        raise ValidationError("sexo debe ser H, M o X.")
    if clave_entidad not in ESTADOS_CURP:
        raise ValidationError(f"Entidad '{clave_entidad}' no está en el catálogo RENAPO.")
    if not nombres.strip() or not primer_apellido.strip():
        raise ValidationError("nombres y primer_apellido son obligatorios.")
    dia, mes, anio = f"{fecha_nacimiento.day:02d}", f"{fecha_nacimiento.month:02d}", str(fecha_nacimiento.year)
    return {
        "nombres": _texto_portal(nombres),
        "primerApellido": _texto_portal(primer_apellido),
        "segundoApellido": _texto_portal(segundo_apellido),
        "diaNacimiento": dia, "mesNacimiento": mes, "selectedYear": anio,
        "fechaNacimiento": f"{dia}/{mes}/{anio}",
        "sexo": sexo, "claveEntidad": clave_entidad, "tipoBusqueda": "datos",
    }


def consulta_con_solver(payload: dict[str, str], campos: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET previo + token Enterprise + POST. Si aparece Akamai → handoff sin gastar captcha.

    `campos` = datos prellenados del handoff en modo 'datos' (None en modo CURP).
    """
    curp = payload.get("curp")
    bloqueo = {
        "bloqueo_antibot": "akamai",
        "detalle": "www.gob.mx respondió con el challenge de Akamai; no se evade. Consulta manual.",
    }
    with httpx.Client(timeout=30, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as http:
        try:
            pagina = http.get(PORTAL_URL)
        except httpx.HTTPError as exc:
            raise UpstreamError(f"gob.mx/curp no respondió: {type(exc).__name__}") from exc
        if _AKAMAI.search(pagina.text):
            return handoff_renapo(curp, campos=campos, **bloqueo)
        sitekey = extraer_sitekey(pagina.text, SITEKEY)
        solver = CaptchaSolver()

        def obtener_token() -> str:
            return solver.recaptcha(sitekey, PORTAL_URL, version="v3", accion=RECAPTCHA_ACCION, enterprise=True)

        def enviar(token: str) -> dict[str, Any] | None:
            try:
                r = http.post(API_CONSULTA, json={**payload, "ip": "127.0.0.1", "token": token},
                              headers={"Accept": "application/json"})
            except httpx.HTTPError as exc:
                raise UpstreamError(f"RENAPO no respondió: {type(exc).__name__}") from exc
            if _AKAMAI.search(r.text):
                return None
            try:
                data = r.json()
            except ValueError:
                data = {}
            mensaje = str(data.get("mensaje", "")).lower()
            if r.status_code in (401, 403) or (
                data.get("codigo") != "01" and ("captcha" in mensaje or "token" in mensaje)
            ):
                raise TokenRechazado()
            if r.status_code != 200 or not data:
                raise UpstreamError(f"RENAPO respondió HTTP {r.status_code}.", {"status_code": r.status_code})
            return data

        data = con_token(obtener_token, enviar, "RENAPO")
    if data is None:
        return handoff_renapo(curp, campos=campos, **bloqueo)
    return parsear_respuesta(data, payload["tipoBusqueda"])


def parsear_respuesta(data: dict[str, Any], tipo: str) -> dict[str, Any]:
    base = {
        "fuente": "RENAPO", "url_consultada": API_CONSULTA, "tipo_busqueda": tipo,
        "simulated": False, "consultado": True, "requiere_humano": False,
        "codigo": data.get("codigo"), "mensaje": data.get("mensaje"),
        "aviso_privacidad": AVISO_PRIVACIDAD,
    }
    registros = data.get("registros") or []
    if data.get("codigo") != "01" or not registros:
        return {**base, "encontrada": False}
    salida = [_normalizar_registro(x) for x in registros]
    return {**base, "encontrada": True, "total": len(salida), "resultados": salida, **salida[0]}


def _normalizar_registro(x: dict[str, Any]) -> dict[str, Any]:
    partes = (x.get("nombres"), x.get("primerApellido"), x.get("segundoApellido"))
    doc = x.get("datosDocProbatorio") or {}
    return {
        "curp": x.get("curp"),
        "nombres": x.get("nombres"),
        "primer_apellido": x.get("primerApellido"),
        "segundo_apellido": x.get("segundoApellido"),
        "nombre_completo": " ".join(p.strip() for p in partes if p and p.strip()),
        "fecha_nacimiento": x.get("fechaNacimiento"),
        "sexo": x.get("sexo"),
        "nacionalidad": x.get("nacionalidad"),
        "entidad": x.get("entidad"),
        "estatus_curp": x.get("statusCurp"),
        "documento_probatorio": (
            {"tipo": x.get("docProbatorio"), **doc} if x.get("docProbatorio") is not None or doc else None
        ),
    }


class RenapoClient:
    """Wrapper sobre la consulta a RENAPO con cache (solo mock) + modo mock."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    @property
    def is_mock(self) -> bool:
        return os.environ.get("PLUGINS_MX_MOCK") == "1"

    @property
    def _mock_mode(self) -> bool:
        return self.is_mock

    async def consultar(self, curp: str) -> dict[str, Any]:
        """Consulta una CURP en RENAPO. Cache 90 días solo en mock (los datos reales no se guardan)."""
        # Validación estructural primero — no tiene sentido consultar RENAPO
        # si la CURP ni siquiera pasa el dígito verificador.
        estructura = validar_estructura(curp)
        if not estructura["valido_estructura"]:
            raise ValidationError(
                "CURP inválida estructuralmente — RENAPO va a rechazar la consulta. "
                f"Errores: {'; '.join(estructura['errores'])}"
            )

        curp_norm = estructura["curp_normalizado"]
        cache_key = f"renapo_{curp_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_consulta(curp_norm, estructura)
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_DIAS)
            self._bitacora.log(
                "consultar_renapo",
                success=True,
                params_summary={
                    "curp_hash": Bitacora.hash_sensitive(curp_norm),
                    "mode": "mock",
                },
            )
            return response

        modo = "solver" if solver_activo(PORTAL_SOLVER) else "handoff"
        self._bitacora.log(
            "consultar_renapo",
            success=True,
            params_summary={"curp_hash": Bitacora.hash_sensitive(curp_norm), "mode": modo},
        )
        if modo == "solver":
            payload = {"curp": curp_norm, "tipoBusqueda": "curp"}
            r = await asyncio.to_thread(consulta_con_solver, payload)
            return {**r, "validacion_local": estructura}
        return {**handoff_renapo(curp_norm), "validacion_local": estructura}

    async def consultar_por_datos(
        self, nombres: str, primer_apellido: str, segundo_apellido: str,
        fecha_nacimiento: date, sexo: str, clave_entidad: str,
    ) -> dict[str, Any]:
        """Busca la CURP por datos personales. Nunca se cachea (datos de terceros)."""
        payload = payload_datos(nombres, primer_apellido, segundo_apellido, fecha_nacimiento, sexo, clave_entidad)
        campos = {
            "nombres": payload["nombres"], "primer_apellido": payload["primerApellido"],
            "segundo_apellido": payload["segundoApellido"], "fecha_nacimiento": fecha_nacimiento.isoformat(),
            "sexo": payload["sexo"], "clave_entidad": payload["claveEntidad"],
        }
        modo = "mock" if self._mock_mode else "solver" if solver_activo(PORTAL_SOLVER) else "handoff"
        self._bitacora.log(
            "consultar_renapo_por_datos",
            success=True,
            params_summary={"datos_hash": Bitacora.hash_sensitive("|".join(campos.values())), "mode": modo},
        )
        if modo == "mock":
            return mark_simulated({
                "fuente": "RENAPO", "tipo_busqueda": "datos", "encontrada": True,
                "datos_consultados": campos, "aviso_privacidad": AVISO_PRIVACIDAD,
                "nota": "Modo mock: no se consultó RENAPO.",
            })
        if modo == "solver":
            return await asyncio.to_thread(consulta_con_solver, payload, campos)
        return handoff_renapo(None, campos=campos)

    async def descargar_constancia(self, curp: str) -> dict[str, Any]:
        """Descarga el PDF de constancia CURP oficial.

        En mock devuelve metadata simulada. En real devuelve handoff humano
        (el portal exige reCAPTCHA Enterprise y challenge de Akamai).
        """
        estructura = validar_estructura(curp)
        if not estructura["valido_estructura"]:
            raise ValidationError(
                "CURP inválida estructuralmente — no se puede descargar constancia."
            )

        if self._mock_mode:
            return mark_simulated(
                {
                    "curp": estructura["curp_normalizado"],
                    "constancia_pdf_path": (
                        f"/mock/constancias/{estructura['curp_normalizado']}.pdf"
                    ),
                    "constancia_pdf_bytes": 0,
                    "vigente_al": datetime.now(timezone.utc).isoformat(),
                    "nota": (
                        "Modo mock — no se generó PDF real. En modo Playwright "
                        "habría descargado y persistido el PDF en cache."
                    ),
                }
            )

        return handoff_renapo(estructura["curp_normalizado"], motivo="constancia")

    # ---------- mock helpers ----------

    @staticmethod
    def _mock_consulta(curp: str, estructura: dict[str, Any]) -> dict[str, Any]:
        """Construye respuesta plausible derivada de la propia CURP."""
        fecha = derivar_fecha_nacimiento(curp)
        sexo = derivar_sexo(curp)
        estado_t = derivar_estado(curp)

        # Heurística determinística para "estado": las CURPs que terminan en
        # 0-3 son "vigente" (90% de los casos reales), 4 = "duplicado", 5+ = vigente
        digito = int(curp[-1])
        if digito == 4:
            estado_renapo = "DUPLICADO"
            estado_descripcion = "CURP duplicada — existe otra persona con esta CURP."
        else:
            estado_renapo = "VIGENTE"
            estado_descripcion = "CURP vigente en padrón RENAPO."

        return mark_simulated(
            {
                "curp": curp,
                "estado_renapo": estado_renapo,
                "estado_descripcion": estado_descripcion,
                "datos_persona": {
                    "fecha_nacimiento": fecha.isoformat() if fecha else None,
                    "sexo": sexo,
                    "entidad_registro": estado_t[1] if estado_t else None,
                    "nacionalidad": "MEXICANA"
                    if estado_t and estado_t[0] != "NE"
                    else "EXTRANJERA",
                },
                "consultado_en": datetime.now(timezone.utc).isoformat(),
                "cache_ttl_dias": CACHE_DIAS,
            }
        )
