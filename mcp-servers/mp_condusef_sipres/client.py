"""Cliente CONDUSEF SIPRES — búsqueda de entidades financieras autorizadas.

Endpoint: POST https://webapps.condusef.gob.mx/SIPRES/jsp/pub/resulbusq.jsp
Body: tipo=1&pnom=<nombre>&pedo=&psec=&psta=
Response: text/html charset=ISO-8859-1

Modo mock por default. PLUGINS_MX_MOCK=0 para producción.
Cache 7 días — el padrón se actualiza diariamente.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.sipres_condusef import (  # noqa: E402
    ENDPOINT_BUSQUEDA,
    ESTATUS_OPERACION,
    PORTAL_URL,
    RESPONSE_ENCODING,
    TIPO_INSTITUCIONES,
    EntidadSIPRES,
    construir_body_busqueda,
    extraer_total_resultados,
    parsear_resultados_html,
    validar_query,
)


NAMESPACE = "condusef_sipres"
CACHE_TTL_HOURS = 24 * 7  # 7 días
MAX_LIMITE = 200
DEFAULT_LIMITE = 50
TIMEOUT_SECONDS = 30.0


class CondusefSipresClient:
    """Cliente unificado SIPRES."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ============================================================
    # Tool 1: Buscar instituciones
    # ============================================================

    def buscar_institucion(
        self,
        nombre: str = "",
        sector: str = "",
        estado: str = "",
        estatus: str = "",
        limite: int = DEFAULT_LIMITE,
    ) -> dict[str, Any]:
        """Búsqueda en el padrón de entidades financieras autorizadas.

        Args:
            nombre: nombre o denominación social (ej. "BANORTE", "BBVA"). Vacío = todas.
            sector: sector (ej. "Instituciones de banca múltiple"). Vacío = todos.
            estado: entidad federativa del domicilio (ej. "Ciudad de México").
            estatus: filtro de status (ej. "En operación", "Cancelado").
            limite: máx resultados a devolver. Default 50, máx 200.

        Returns:
            {
              "filtros": {nombre, sector, estado, estatus},
              "total_padron": int,           # total real en SIPRES
              "devueltos": int,              # cuántos devolvemos
              "resultados": [EntidadSIPRES.to_dict(), ...],
              "fecha_consulta": ISO-8601 UTC,
              "fuente": URL portal,
              "simulated": bool,
            }
        """
        # Validar al menos un filtro o explícitamente pedir todos
        if not (nombre or sector or estado or estatus):
            raise ValidationError(
                "Debe proporcionarse al menos un filtro (nombre, sector, estado o estatus). "
                "SIPRES sin filtros tarda varios minutos.",
                {"campos": ["nombre", "sector", "estado", "estatus"]},
            )

        if nombre:
            nombre = validar_query(nombre)
        if not 1 <= limite <= MAX_LIMITE:
            raise ValidationError(
                f"limite={limite} fuera de rango [1, {MAX_LIMITE}].",
                {"limite": limite},
            )

        cache_key = f"buscar:{nombre}:{sector}:{estado}:{estatus}:{limite}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._bitacora.log(
                "buscar_institucion",
                success=True,
                params_summary={"nombre": nombre, "sector": sector, "cache": "hit"},
            )
            return cached

        # Portal público — default a real cuando no hay override
        if is_mock_mode(credential_env_vars=[], default_when_no_creds=False):
            result = self._mock_buscar(
                nombre=nombre, sector=sector, estado=estado, estatus=estatus, limite=limite,
            )
        else:
            result = self._llamar_endpoint(
                nombre=nombre, sector=sector, estado=estado, estatus=estatus, limite=limite,
            )

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "buscar_institucion",
            success=True,
            params_summary={
                "nombre": nombre, "sector": sector,
                "devueltos": result.get("devueltos"),
                "cache": "miss",
            },
        )
        return result

    # ============================================================
    # Tool 2: Verificación binaria para KYC
    # ============================================================

    def verificar_autorizada(self, nombre: str) -> dict[str, Any]:
        """Decisión binaria para KYC institucional / due-diligence fintech.

        ¿Esta institución financiera está autorizada y en operación según
        la CONDUSEF? Útil antes de:
            - Contratar productos de una SOFOM
            - Usar una IFPE/IFC fintech
            - Operar con casa de cambio
            - Suscribir póliza con aseguradora

        Args:
            nombre: razón social o nombre comercial.

        Returns:
            {
              "nombre_buscado": str,
              "encontrada": bool,
              "autorizada_en_operacion": bool,
              "coincidencias": int,
              "mejor_match": EntidadSIPRES | None,
              "advertencias": [str]
            }
        """
        nombre = validar_query(nombre)
        resultado = self.buscar_institucion(nombre=nombre, limite=20)
        coincidencias = resultado["resultados"]

        if not coincidencias:
            return {
                "nombre_buscado": nombre,
                "encontrada": False,
                "autorizada_en_operacion": False,
                "coincidencias": 0,
                "mejor_match": None,
                "advertencias": [
                    f"NO se encontraron coincidencias para '{nombre}' en SIPRES. "
                    "Posibles causas: (1) no es entidad financiera regulada CONDUSEF; "
                    "(2) opera con otra denominación social; (3) incumple normatividad "
                    "(SIPRES no la lista entidades sancionadas). "
                    "ANTES DE OPERAR: validar con CNBV (banca/valores), "
                    "CNSF (seguros) o CONSAR (AFORES) según sector."
                ],
            }

        # Mejor match: el que está "En operación" y tiene denominación más cercana
        en_operacion = [r for r in coincidencias if ESTATUS_OPERACION.lower() in r["estatus"].lower()]
        mejor = en_operacion[0] if en_operacion else coincidencias[0]
        autorizada = bool(en_operacion)

        advertencias: list[str] = []
        if not autorizada:
            estatus_actual = mejor["estatus"]
            advertencias.append(
                f"⛔ Encontrada(s) {len(coincidencias)} coincidencia(s), pero NINGUNA está "
                f"'En operación' actualmente. Status del mejor match: '{estatus_actual}'. "
                "NO contratar — la entidad está suspendida, cancelada o revocada."
            )
        elif len(en_operacion) > 1:
            advertencias.append(
                f"Múltiples entidades en operación ({len(en_operacion)}) coinciden con '{nombre}'. "
                "Verifica clave_registro exacta antes de contratar — grupos financieros "
                "tienen varias filiales con denominación similar."
            )

        return {
            "nombre_buscado": nombre,
            "encontrada": True,
            "autorizada_en_operacion": autorizada,
            "coincidencias": len(coincidencias),
            "mejor_match": mejor,
            "advertencias": advertencias,
        }

    # ============================================================
    # HTTP layer
    # ============================================================

    def _llamar_endpoint(
        self,
        nombre: str,
        sector: str,
        estado: str,
        estatus: str,
        limite: int,
    ) -> dict[str, Any]:
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise UpstreamError(
                "httpx no está instalado. Instala con `pip install httpx`.",
                {"raw": str(e)},
            ) from e

        # NOTA: SIPRES espera nombres específicos en los filtros multi-select
        # (psec, pedo, psta). Para v1 enviamos sector/estado/estatus por separado
        # y filtramos client-side. Server-side los espera comma-separated.
        body = construir_body_busqueda(
            pnom=nombre,
            psec=sector,
            pedo=estado,
            psta=estatus,
            tipo=TIPO_INSTITUCIONES,
        )

        # Usa shared helpers: truststore para gov.mx (cadena cert incompleta)
        from shared.http_helpers import build_ssl_verify
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=True, verify=build_ssl_verify()) as client:
                resp = client.post(
                    ENDPOINT_BUSQUEDA,
                    data=body,
                    headers={
                        "User-Agent": "plugins-mx/mp_condusef_sipres (KYC institucional)",
                        "Accept": "text/html,*/*",
                        "Referer": PORTAL_URL,
                    },
                )
                resp.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        # SIPRES devuelve ISO-8859-1; httpx puede mal-detectarlo
        try:
            html_text = resp.content.decode(RESPONSE_ENCODING)
        except UnicodeDecodeError:
            html_text = resp.text  # fallback al best-effort de httpx

        return self._normalizar_resultado(
            html_text=html_text,
            nombre=nombre,
            sector=sector,
            estado=estado,
            estatus=estatus,
            limite=limite,
            simulated=False,
        )

    @staticmethod
    def _normalizar_resultado(
        html_text: str,
        nombre: str,
        sector: str,
        estado: str,
        estatus: str,
        limite: int,
        simulated: bool,
    ) -> dict[str, Any]:
        """Parsea HTML SIPRES y devuelve el shape canónico."""
        total = extraer_total_resultados(html_text)
        entidades = parsear_resultados_html(html_text)
        devueltos = entidades[:limite]
        return {
            "filtros": {
                "nombre": nombre,
                "sector": sector,
                "estado": estado,
                "estatus": estatus,
            },
            "total_padron": total,
            "devueltos": len(devueltos),
            "resultados": [e.to_dict() for e in devueltos],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": ENDPOINT_BUSQUEDA,
            "simulated": simulated,
        }

    # ============================================================
    # Mock layer
    # ============================================================

    def _mock_buscar(
        self,
        nombre: str,
        sector: str,
        estado: str,
        estatus: str,
        limite: int,
    ) -> dict[str, Any]:
        """Respuestas simuladas determinísticas para CI/dev."""
        # Mock determinístico:
        #   - vacío o muy corto → 0
        #   - contiene FAKE/NOEXIST/XYZ-FAKE → 0 (sentinels para tests)
        #   - BANCO/BBVA/BANORTE → 3 resultados (grupos financieros típicos)
        #   - otro nombre válido → 1 resultado
        nombre_upper = nombre.upper()
        sentinels_no_match = ("FAKE", "NOEXIST", "INEXIST", "XYZ-")
        if not nombre or len(nombre) < 3:
            ents: list[EntidadSIPRES] = []
        elif any(s in nombre_upper for s in sentinels_no_match):
            ents = []
        elif "BANCO" in nombre_upper or "BBVA" in nombre_upper or "BANORTE" in nombre_upper:
            ents = [self._mock_entidad(nombre, idx=i) for i in range(3)]
        else:
            ents = [self._mock_entidad(nombre, idx=0)]

        devueltos = ents[:limite]
        out = {
            "filtros": {
                "nombre": nombre,
                "sector": sector,
                "estado": estado,
                "estatus": estatus,
            },
            "total_padron": len(ents),
            "devueltos": len(devueltos),
            "resultados": [e.to_dict() for e in devueltos],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": ENDPOINT_BUSQUEDA,
        }
        return mark_simulated(out)

    @staticmethod
    def _mock_entidad(nombre: str, idx: int) -> EntidadSIPRES:
        """Genera EntidadSIPRES determinística para mocks."""
        denominaciones = [
            f"{nombre}, S.A., Institución de Banca Múltiple",
            f"{nombre} Casa de Bolsa, S.A. de C.V.",
            f"Grupo Financiero {nombre}, S.A.B. de C.V.",
        ]
        sectores = [
            "Instituciones de banca múltiple",
            "Casas de Bolsa",
            "SOFOM E.R.",
        ]
        estatus_list = [ESTATUS_OPERACION, ESTATUS_OPERACION, "Cancelado"]
        return EntidadSIPRES(
            clave_registro=str(40000 + idx),
            denominacion=denominaciones[idx % 3],
            nombre_corto=nombre.upper(),
            estatus=estatus_list[idx % 3],
            sector=sectores[idx % 3],
            estado="Ciudad de México",
            ultima_actualizacion="2026-05-15",
            no_localizable="",
            idins=str(16000 + idx),
            estatus_tooltip=(
                "Institución Financiera que se encuentra ofreciendo sus productos al público."
                if estatus_list[idx % 3] == ESTATUS_OPERACION
                else "Institución cuyo registro fue cancelado."
            ),
        )
