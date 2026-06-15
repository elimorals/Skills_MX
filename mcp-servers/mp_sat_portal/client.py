"""Cliente orquestador para el portal SAT.

Estrategia:
- Tools PÚBLICOS (sin auth): intenta HTTP real → fallback mock si falla
  - consultar_padron, consultar_69b_efos, consultar_69_incumplidos,
    verificar_cfdi_uuid
- Tools con AUTH (CIEC o e.firma): siempre mock por default. Path real requiere
  Playwright + credenciales del contribuyente — fuera del alcance default.
  Para activar el path real, instalar `pip install plugins-mx-mcp-servers[playwright]`
  y proveer SAT_RFC + SAT_CIEC (o SAT_EFIRMA_CERT/KEY/PASSWORD).

⚠ El portal SAT cambia con frecuencia. Selectores Playwright pueden romper.
La estrategia mock-first protege a los skills downstream de fallar silenciosamente.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from shared.bitacora import Bitacora
from shared.cache import FileCache
from shared.errors import McpError, UpstreamError
from shared.mock import is_mock_mode, mark_simulated

from mp_sat_portal import mock_data, rfc69b, uuid_validator


NAMESPACE = "sat_portal"


# URLs públicas SAT (verificar vigencia — cambian periódicamente)
# Validado Playwright MCP 2026-06-15: el SAT migró todo a Azure Blob Storage
# bajo wu1agsprosta001.blob.core.windows.net. Las URLs viejas en
# omawww.sat.gob.mx siguen respondiendo pero con archivos STALE (Ene 2026),
# mientras los nuevos en Azure se actualizan mensualmente.
URL_VERIFICACFDI = "https://verificacfdi.facturaelectronica.sat.gob.mx/"

# === Lista 69-B (EFOS) — operaciones simuladas Art. 69-B CFF ===
_SAT_BLOB_AGAFF = "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF"
URL_LISTA_69B_DEFINITIVOS = f"{_SAT_BLOB_AGAFF}/Definitivos.csv"
URL_LISTA_69B_PRESUNTOS = f"{_SAT_BLOB_AGAFF}/Presuntos.csv"
URL_LISTA_69B_DESVIRTUADOS = f"{_SAT_BLOB_AGAFF}/Desvirtuados.csv"
URL_LISTA_69B_SENTENCIAS_FAVORABLES = f"{_SAT_BLOB_AGAFF}/SentenciasFavorables.csv"
URL_LISTA_69B_COMPLETO = f"{_SAT_BLOB_AGAFF}/Listado_completo_69-B.csv"

# === Lista 69 (incumplidos Art. 69 CFF) — fragmentada en 8 categorías ===
# Tras la migración, no existe un único "IncumplidosListado.csv". El SAT publica
# 8 archivos distintos por motivo de publicación. Para mantener compatibilidad
# con código existente, URL_LISTA_69_INCUMPLIDOS apunta a "Firmes.csv" que es
# conceptualmente lo más cercano a "incumplidos" (créditos fiscales firmes).
_SAT_BLOB_AGR = "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR"
URL_LISTA_69_FIRMES = f"{_SAT_BLOB_AGR}/Firmes.csv"
URL_LISTA_69_INCUMPLIDOS = URL_LISTA_69_FIRMES  # alias backward-compatible
URL_LISTA_69_CANCELADOS = f"{_SAT_BLOB_AGR}/Cancelados.csv"
URL_LISTA_69_EXIGIBLES = f"{_SAT_BLOB_AGR}/Exigibles.csv"
URL_LISTA_69_NO_LOCALIZADOS = f"{_SAT_BLOB_AGR}/No_localizados.csv"
URL_LISTA_69_SENTENCIAS = f"{_SAT_BLOB_AGR}/Sentencias.csv"
URL_LISTA_69_CSD_SIN_EFECTOS = f"{_SAT_BLOB_AGR}/CSDsinefectos.csv"
URL_LISTA_69_ENTES_GOB_OMISOS = f"{_SAT_BLOB_AGR}/EntespublicosydeGobiernoomisos.csv"
URL_LISTA_69_REDUCCION_MULTAS = f"{_SAT_BLOB_AGR}/ReduccionArt74CFF.csv"

# Catálogo completo de las 8 fuentes de la Lista 69 para iteración programática
URLS_LISTA_69_TODOS: dict[str, str] = {
    "firmes": URL_LISTA_69_FIRMES,
    "cancelados": URL_LISTA_69_CANCELADOS,
    "exigibles": URL_LISTA_69_EXIGIBLES,
    "no_localizados": URL_LISTA_69_NO_LOCALIZADOS,
    "sentencias": URL_LISTA_69_SENTENCIAS,
    "csd_sin_efectos": URL_LISTA_69_CSD_SIN_EFECTOS,
    "entes_publicos_gob_omisos": URL_LISTA_69_ENTES_GOB_OMISOS,
    "reduccion_multas_art74": URL_LISTA_69_REDUCCION_MULTAS,
}

# Selectores reales Verifica CFDI SAT (ASP.NET WebForms) — validado 2026-06-13:
VERIFICACFDI_SELECTORES = {
    "uuid": "input[name='ctl00$MainContent$TxtUUID']",  # 36 chars
    "rfc_emisor": "input[name='ctl00$MainContent$TxtRfcEmisor']",  # 13 chars
    "rfc_receptor": "input[name='ctl00$MainContent$TxtRfcReceptor']",  # 13 chars
    "captcha": "input[name='ctl00$MainContent$TxtCaptchaNumbers']",  # 5 chars — HUMANO REQUERIDO
    "submit": "button:has-text('Verificar CFDI')",
    "captcha_img": "img[id*='Captcha']",  # 2 imágenes captcha (web + XML)
}

# ⚠ Verifica CFDI tiene CAPTCHA — automatización completa NO viable.
# Path correcto: usar mp_facturama_extendido.timbrar_cfdi() para validación
# en momento del timbrado (PAC certifica). Verifica CFDI post-emisión es
# para humano-en-loop (cliente confirma autenticidad de CFDI recibido).


# Env vars que indican credenciales para path real
CRED_ENV_VARS = ["SAT_RFC", "SAT_CIEC", "SAT_EFIRMA_CERT"]


class SatPortalClient:
    """Cliente orquestador del portal SAT.

    Cada método retorna un dict con shape consistente. En modo mock añade
    `simulated: true`. En modo real puede levantar McpError si el portal
    cambió y los selectores rompieron.
    """

    def __init__(
        self,
        *,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
        http_timeout: float = 30.0,
    ) -> None:
        self.cache = cache or FileCache(NAMESPACE)
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self.http_timeout = http_timeout

    # ---------- helpers ----------

    def _mock(self) -> bool:
        return is_mock_mode(CRED_ENV_VARS)

    def _log(self, op: str, payload: dict[str, Any], *, success: bool = True) -> None:
        """Log una operación. Hashea identificadores sensibles (RFC, folio)."""
        safe = dict(payload)
        if "rfc" in safe and safe["rfc"]:
            safe["rfc_hash"] = Bitacora.hash_sensitive(safe.pop("rfc"))
        if "rfc_emisor" in safe and safe["rfc_emisor"]:
            safe["rfc_emisor_hash"] = Bitacora.hash_sensitive(safe.pop("rfc_emisor"))
        if "rfc_receptor" in safe and safe["rfc_receptor"]:
            safe["rfc_receptor_hash"] = Bitacora.hash_sensitive(safe.pop("rfc_receptor"))
        self.bitacora.log(op, success=success, params_summary=safe)

    def _http_get_text(self, url: str, ttl_hours: float = 24.0) -> str | None:
        """GET con cache de texto plano. Retorna None si falla la red.

        Usa shared/http_helpers para SSL gov.mx-compatible + encoding fallback.
        """
        cached = self.cache.get(url)
        if cached is not None:
            return cached if isinstance(cached, str) else None
        from shared.http_helpers import build_ssl_verify, decode_response_robust
        try:
            with httpx.Client(
                timeout=self.http_timeout, follow_redirects=True,
                verify=build_ssl_verify(),
            ) as client:
                resp = client.get(url)
                resp.raise_for_status()
                body = decode_response_robust(resp)
                self.cache.set(url, body, ttl_hours=ttl_hours)
                return body
        except httpx.RequestError:
            return None
        except httpx.HTTPStatusError:
            return None

    # ---------- tools públicos ----------

    def consultar_padron(self, rfc: str) -> dict[str, Any]:
        """Consulta status del RFC en padrón SAT (público)."""
        self._log("consultar_padron", {"rfc": rfc})
        # El padrón web no tiene endpoint JSON estable. En path real con
        # Playwright se haría scrape. Por ahora mock-first.
        if self._mock():
            return mark_simulated(
                mock_data.mock_padron(rfc),
                "Endpoint real requiere Playwright contra https://siat.sat.gob.mx",
            )
        # Future: Playwright path
        raise UpstreamError(
            "Path real no implementado. Setea PLUGINS_MX_MOCK=1 para forzar mock."
        )

    def consultar_69b_efos(self, rfc: str | None = None) -> dict[str, Any]:
        """Consulta lista 69-B (definitivos + presuntos).

        Descarga ambos CSVs públicos del SAT. Si la red falla retorna mock.
        Si pasa un RFC busca específicamente; si no, retorna conteo total.
        """
        self._log("consultar_69b_efos", {"rfc": rfc or "(lista completa)"})

        # En modo mock no toca red
        if self._mock():
            return mark_simulated(
                mock_data.mock_69b(rfc),
                "Modo mock — listas oficiales no consultadas.",
            )

        # Intentar HTTP real ambos archivos
        def_csv = self._http_get_text(URL_LISTA_69B_DEFINITIVOS)
        pre_csv = self._http_get_text(URL_LISTA_69B_PRESUNTOS)

        if def_csv is None and pre_csv is None:
            # Sin red → mock
            return mark_simulated(
                mock_data.mock_69b(rfc),
                "Listas oficiales no descargables — usando datos demo.",
            )

        registros: list[dict[str, Any]] = []
        if def_csv:
            registros.extend(rfc69b.parsear_csv_69b(def_csv))
        if pre_csv:
            registros.extend(rfc69b.parsear_csv_69b(pre_csv))

        if rfc:
            encontrado = rfc69b.buscar_rfc_en_lista(rfc, registros)
            return {
                "rfc_consultado": rfc.strip().upper(),
                "encontrado": encontrado is not None,
                "registro": encontrado,
                "total_lista": len(registros),
                "fuente": "wu1agsprosta001.blob.core.windows.net (SAT Datos Abiertos)",
                "simulated": False,
            }

        return {
            "rfc_consultado": None,
            "total_registros": len(registros),
            "registros": registros[:50],  # cap para no devolver listas enormes
            "truncado_a": 50,
            "fuente": "wu1agsprosta001.blob.core.windows.net (SAT Datos Abiertos)",
            "simulated": False,
        }

    def consultar_69_incumplidos(self, rfc: str | None = None) -> dict[str, Any]:
        """Consulta lista 69 (incumplidos del Art. 69 CFF)."""
        self._log("consultar_69_incumplidos", {"rfc": rfc or "(lista completa)"})

        if self._mock():
            return mark_simulated(
                mock_data.mock_69_incumplidos(rfc),
                "Modo mock — lista oficial no consultada.",
            )

        csv_body = self._http_get_text(URL_LISTA_69_INCUMPLIDOS)
        if csv_body is None:
            return mark_simulated(
                mock_data.mock_69_incumplidos(rfc),
                "Lista oficial no descargable — usando datos demo.",
            )

        registros = rfc69b.parsear_csv_69_incumplidos(csv_body)

        if rfc:
            encontrado = rfc69b.buscar_rfc_en_lista(rfc, registros)
            return {
                "rfc_consultado": rfc.strip().upper(),
                "encontrado": encontrado is not None,
                "registro": encontrado,
                "total_lista": len(registros),
                "fuente": "wu1agsprosta001.blob.core.windows.net (SAT Datos Abiertos)",
                "simulated": False,
            }

        return {
            "rfc_consultado": None,
            "total_registros": len(registros),
            "registros": registros[:50],
            "truncado_a": 50,
            "fuente": "wu1agsprosta001.blob.core.windows.net (SAT Datos Abiertos)",
            "simulated": False,
        }

    def verificar_cfdi_uuid(
        self,
        uuid: str,
        rfc_emisor: str,
        rfc_receptor: str,
        total: str,
    ) -> dict[str, Any]:
        """Verifica status de un CFDI contra el portal público SAT.

        Estrategia:
        1. Valida UUID estructuralmente (siempre real, no requiere red)
        2. Si UUID válido y NO mock: intenta GET al verificador SAT
        3. El portal devuelve HTML; parseamos con regex sencillo
        4. Si la red falla o el HTML cambió → mock

        ⚠ La respuesta del verificador puede tener varias formas. Esta
        implementación captura los casos comunes pero puede fallar si SAT
        cambia su markup.
        """
        validacion = uuid_validator.validar_uuid(uuid)
        if not validacion["valido"]:
            return {
                "uuid": uuid,
                "valido_estructuralmente": False,
                "razon_invalido": validacion["razon"],
                "estado_cfdi": None,
                "fuente": "local (validación estructural)",
                "simulated": False,
            }

        self._log(
            "verificar_cfdi_uuid",
            {
                "uuid": validacion["uuid_normalizado"],
                "rfc_emisor": rfc_emisor,
                "rfc_receptor": rfc_receptor,
            },
        )

        if self._mock():
            base = mock_data.mock_verificacion_uuid(
                validacion["uuid_normalizado"], rfc_emisor, rfc_receptor, total
            )
            base["valido_estructuralmente"] = True
            return mark_simulated(
                base,
                "Validación estructural real; portal SAT no consultado (modo mock).",
            )

        url = uuid_validator.construir_url_verificacion(
            validacion["uuid_normalizado"], rfc_emisor, rfc_receptor, total
        )
        html = self._http_get_text(url, ttl_hours=0.0833)  # ~5 min
        if html is None:
            base = mock_data.mock_verificacion_uuid(
                validacion["uuid_normalizado"], rfc_emisor, rfc_receptor, total
            )
            base["valido_estructuralmente"] = True
            return mark_simulated(
                base,
                "Portal SAT no respondió. Devolviendo simulación.",
            )

        return _parsear_html_verificacfdi(
            html,
            validacion["uuid_normalizado"],
            rfc_emisor,
            rfc_receptor,
            total,
        )

    # ---------- tools con auth (siempre mock por ahora) ----------

    def descargar_csf(self, rfc: str) -> dict[str, Any]:
        self._log("descargar_csf", {"rfc": rfc})
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + e.firma. No implementado todavía."
            )
        return mark_simulated(
            mock_data.mock_csf(rfc),
            "CSF real requiere e.firma o RFC+Contraseña — no consultado.",
        )

    def descargar_buzon_tributario(self, rfc: str) -> dict[str, Any]:
        self._log("descargar_buzon_tributario", {"rfc": rfc})
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + e.firma. No implementado todavía."
            )
        return mark_simulated(
            mock_data.mock_buzon_tributario(rfc),
            "Buzón Tributario requiere e.firma — no consultado.",
        )

    def descargar_cfdi_masivo(
        self,
        rfc: str,
        ejercicio: int,
        mes: int,
        tipo: str,
    ) -> dict[str, Any]:
        self._log(
            "descargar_cfdi_masivo",
            {"rfc": rfc, "ejercicio": ejercicio, "mes": mes, "tipo": tipo},
        )
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + e.firma. No implementado todavía."
            )
        return mark_simulated(
            mock_data.mock_cfdi_masivo(rfc, ejercicio, mes, tipo),
            "Descarga masiva requiere e.firma — simulación de solicitud.",
        )

    def agendar_cita_sat(
        self,
        rfc: str,
        tipo_tramite: str,
        entidad: str | None = None,
    ) -> dict[str, Any]:
        self._log(
            "agendar_cita_sat",
            {"rfc": rfc, "tipo_tramite": tipo_tramite, "entidad": entidad},
        )
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + RFC+CIEC. No implementado todavía."
            )
        return mark_simulated(
            mock_data.mock_cita_sat(rfc, tipo_tramite, entidad),
            "Citas SAT requieren RFC+CIEC — simulación de disponibilidad.",
        )

    def verificar_efirma_vigente(self, rfc: str) -> dict[str, Any]:
        self._log("verificar_efirma_vigente", {"rfc": rfc})
        if not self._mock():
            raise UpstreamError(
                "Path real requiere e.firma activa para auto-consulta."
            )
        return mark_simulated(
            mock_data.mock_efirma_status(rfc),
            "Status e.firma requiere e.firma — simulación.",
        )

    def descargar_acuse(self, folio: str) -> dict[str, Any]:
        self._log("descargar_acuse", {"folio": folio})
        if not self._mock():
            raise UpstreamError(
                "Path real requiere e.firma + autenticación previa."
            )
        return mark_simulated(
            mock_data.mock_acuse(folio),
            "Acuse real requiere autenticación SAT — simulación.",
        )

    def actualizar_obligaciones(self, rfc: str, accion: str) -> dict[str, Any]:
        """⚠ OPERACIÓN PELIGROSA — modifica el padrón. Siempre simulada por default."""
        self._log("actualizar_obligaciones", {"rfc": rfc, "accion": accion})
        # Incluso con credenciales reales, esta operación se bloquea sin
        # un flag explícito adicional para evitar cambios accidentales.
        if not self._mock():
            if os.environ.get("PLUGINS_MX_SAT_PERMITIR_ESCRITURA") != "1":
                raise UpstreamError(
                    "Operación de escritura bloqueada por seguridad. "
                    "Activar con PLUGINS_MX_SAT_PERMITIR_ESCRITURA=1 y revisar dos veces.",
                )
            raise UpstreamError(
                "Path real para escritura no implementado. Demasiado riesgoso sin revisión."
            )
        return mark_simulated(
            mock_data.mock_actualizar_obligaciones(rfc, accion),
            "Operación de escritura — SIEMPRE simulada en este path.",
        )


# ---------- parseo HTML del verificador ----------

import re as _re

_REGEX_ESTADO_CFDI = _re.compile(
    r"Estado CFDI[^<]*<[^>]+>\s*([^<]+)", _re.IGNORECASE
)
_REGEX_ESTADO_CANCELACION = _re.compile(
    r"Estatus de cancelaci[oó]n[^<]*<[^>]+>\s*([^<]+)", _re.IGNORECASE
)


def _parsear_html_verificacfdi(
    html: str,
    uuid: str,
    rfc_emisor: str,
    rfc_receptor: str,
    total: str,
) -> dict[str, Any]:
    """Extrae estado del CFDI del HTML del verificador SAT.

    El portal devuelve un ASPX con varias celdas. Buscamos los textos clave
    con regex tolerante. Si no se encuentra estructura conocida, devolvemos
    fallback con `parseo_fallido: true`.
    """
    m_estado = _REGEX_ESTADO_CFDI.search(html)
    m_cancel = _REGEX_ESTADO_CANCELACION.search(html)

    if not m_estado:
        return {
            "uuid": uuid,
            "rfc_emisor": rfc_emisor.strip().upper(),
            "rfc_receptor": rfc_receptor.strip().upper(),
            "total_consultado": str(total),
            "estado_cfdi": None,
            "estado_cancelacion": None,
            "parseo_fallido": True,
            "razon": "El HTML del portal cambió o el CFDI no fue encontrado.",
            "fuente": URL_VERIFICACFDI,
            "valido_estructuralmente": True,
            "simulated": False,
        }

    return {
        "uuid": uuid,
        "rfc_emisor": rfc_emisor.strip().upper(),
        "rfc_receptor": rfc_receptor.strip().upper(),
        "total_consultado": str(total),
        "estado_cfdi": m_estado.group(1).strip(),
        "estado_cancelacion": m_cancel.group(1).strip() if m_cancel else None,
        "parseo_fallido": False,
        "fuente": URL_VERIFICACFDI,
        "valido_estructuralmente": True,
        "simulated": False,
    }
