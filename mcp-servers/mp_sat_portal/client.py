"""Cliente orquestador para el portal SAT.

Estrategia:
- Listas públicas 69 / 69-B: HTTP real por default (Azure Blob del SAT). Si la
  descarga falla se levanta UpstreamError — sin fallback a mock.
- Tools con e.firma (CSF, padrón, vigencia e.firma): login FIEL por httpx
  (`shared/sat_portal_fiel.py`, port de satcfdi). Mock solo con PLUGINS_MX_MOCK=1
  o sin credenciales (SAT_RFC / SAT_CIEC / SAT_EFIRMA_CERT).
- Buzón Tributario y acuses: sin implementación real → UpstreamError explícito
  con handoff humano.

⚠ El portal SAT cambia con frecuencia. Selectores Playwright pueden romper.
La estrategia mock-first protege a los skills downstream de fallar silenciosamente.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from shared.bitacora import Bitacora
from shared.cache import FileCache
from shared.errors import AuthError, ConfigError, McpError, UpstreamError, ValidationError
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


URL_VALIDA_RFC = "https://agsc.siat.sat.gob.mx/PTSC/ValidaRFC/index.jsf"  # tiene CAPTCHA
URL_BUZON_TRIBUTARIO = "https://www.sat.gob.mx (Trámites > Buzón Tributario, iniciar sesión con e.firma)"
URL_REIMPRESION_ACUSES = "https://www.sat.gob.mx (Declaraciones > Reimpresión de acuses, con e.firma)"

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

    def _mock_publico(self) -> bool:
        """Fuentes públicas: reales salvo PLUGINS_MX_MOCK=1."""
        return is_mock_mode([], default_when_no_creds=False)

    def _efirma(self, rfc: str):
        """Carga la e.firma de SAT_EFIRMA_* y exige que sea del RFC pedido y esté vigente."""
        from mp_sat_portal.efirma_loader import EfirmaLoader

        loader = EfirmaLoader.from_env()
        meta = loader.metadata()
        rfc_norm = rfc.strip().upper()
        if meta.rfc != rfc_norm:
            raise ValidationError(
                f"La e.firma cargada es de otro RFC; solo se puede consultar el RFC titular ({meta.rfc}).",
                {"rfc_solicitado": rfc_norm},
            )
        if not meta.is_valid_now:
            raise AuthError(
                f"e.firma no vigente (vence {meta.not_after.date().isoformat()}).",
                {"vigencia_hasta": meta.not_after.isoformat()},
            )
        return loader

    @staticmethod
    def _guardar_pdf(tipo: str, rfc: str, pdf: bytes) -> str:
        """Guarda el PDF (permisos 600) bajo PLUGINS_MX_CACHE_DIR/sat_portal/docs."""
        from datetime import datetime as _dt
        from pathlib import Path

        root = Path(os.environ.get("PLUGINS_MX_CACHE_DIR", "~/.cache/plugins-mx")).expanduser()
        carpeta = root / "sat_portal" / "docs"
        carpeta.mkdir(parents=True, exist_ok=True)
        path = carpeta / f"{tipo}_{rfc}_{_dt.now().strftime('%Y%m%d%H%M%S')}.pdf"
        path.write_bytes(pdf)
        path.chmod(0o600)
        return str(path)

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
        # Real: login FIEL al portal de Factura electrónica (ExisteLrfc + ValidaLco).
        # Con la e.firma propia se puede consultar cualquier RFC. La consulta
        # pública sin login (ValidaRFC) tiene CAPTCHA: handoff humano.
        if self._mock():
            return mark_simulated(
                mock_data.mock_padron(rfc),
                f"Modo mock. Consulta pública con CAPTCHA (humano): {URL_VALIDA_RFC}",
            )
        from mp_sat_portal.efirma_loader import EfirmaLoader
        from shared.sat_portal_fiel import URL_FACTURA, SatFielSession

        try:
            loader = EfirmaLoader.from_env()
        except ConfigError as exc:
            raise ConfigError(
                f"{exc} Sin e.firma la validación de RFC es manual (CAPTCHA): {URL_VALIDA_RFC}",
                {**exc.details, "handoff_url": URL_VALIDA_RFC},
            ) from exc
        if not loader.metadata().is_valid_now:
            raise AuthError("e.firma no vigente; no se puede iniciar sesión en el portal SAT.")
        with SatFielSession(loader) as sesion:
            datos = sesion.consultar_rfc(rfc)
        return {
            "rfc": rfc.strip().upper(),
            "encontrado": datos["existe_en_lco"],
            "lco": datos["lco"],
            "fuente": f"{URL_FACTURA} (Clientes/ExisteLrfc + Clientes/ValidaLco, login e.firma)",
            "simulated": False,
        }

    def consultar_69b_efos(self, rfc: str | None = None) -> dict[str, Any]:
        """Consulta lista 69-B (definitivos + presuntos).

        Descarga ambos CSVs públicos del SAT. Si alguno no se puede descargar
        levanta UpstreamError (una lista parcial daría falsos negativos).
        Si pasa un RFC busca específicamente; si no, retorna conteo total.
        """
        self._log("consultar_69b_efos", {"rfc": rfc or "(lista completa)"})

        if self._mock_publico():
            return mark_simulated(
                mock_data.mock_69b(rfc),
                "Modo mock — listas oficiales no consultadas.",
            )

        def_csv = self._http_get_text(URL_LISTA_69B_DEFINITIVOS)
        pre_csv = self._http_get_text(URL_LISTA_69B_PRESUNTOS)
        if def_csv is None or pre_csv is None:
            raise UpstreamError(
                "No se pudo descargar la lista 69-B del SAT (Definitivos/Presuntos).",
                {"urls": [URL_LISTA_69B_DEFINITIVOS, URL_LISTA_69B_PRESUNTOS]},
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

        if self._mock_publico():
            return mark_simulated(
                mock_data.mock_69_incumplidos(rfc),
                "Modo mock — lista oficial no consultada.",
            )

        csv_body = self._http_get_text(URL_LISTA_69_INCUMPLIDOS)
        if csv_body is None:
            raise UpstreamError(
                "No se pudo descargar la lista 69 (Firmes) del SAT.",
                {"url": URL_LISTA_69_INCUMPLIDOS},
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
        """Verifica el estado de un CFDI con el web service SOAP público del SAT.

        `ConsultaCFDIService` no requiere e.firma ni CAPTCHA; pide UUID, RFC
        emisor, RFC receptor y total. Si el SAT no responde → UpstreamError
        (sin fallback a mock).
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

        # Servicio público: mock solo si se pide explícitamente (PLUGINS_MX_MOCK=1).
        if is_mock_mode([], default_when_no_creds=False):
            base = mock_data.mock_verificacion_uuid(
                validacion["uuid_normalizado"], rfc_emisor, rfc_receptor, total
            )
            base["valido_estructuralmente"] = True
            return mark_simulated(
                base,
                "Validación estructural real; SAT no consultado (PLUGINS_MX_MOCK=1).",
            )

        return _consultar_cfdi_soap(
            validacion["uuid_normalizado"],
            rfc_emisor,
            rfc_receptor,
            total,
            self.http_timeout,
        )

    # ---------- tools con auth (e.firma) ----------

    def descargar_csf(self, rfc: str) -> dict[str, Any]:
        """Constancia de Situación Fiscal (PDF) del titular de la e.firma."""
        self._log("descargar_csf", {"rfc": rfc})
        if self._mock():
            return mark_simulated(
                mock_data.mock_csf(rfc),
                "CSF real requiere e.firma (SAT_EFIRMA_*) — no consultado.",
            )
        import hashlib
        from datetime import datetime as _dt

        from shared.sat_portal_fiel import URL_CONSTANCIA_PDF, SatFielSession

        loader = self._efirma(rfc)
        with SatFielSession(loader) as sesion:
            pdf = sesion.descargar_constancia()
        rfc_norm = rfc.strip().upper()
        return {
            "rfc": rfc_norm,
            "pdf_path": self._guardar_pdf("csf", rfc_norm, pdf),
            "pdf_bytes": len(pdf),
            "pdf_sha256": hashlib.sha256(pdf).hexdigest(),
            "fecha_descarga": _dt.now().isoformat(timespec="seconds"),
            "fuente": URL_CONSTANCIA_PDF,
            "nota": "Datos del PDF (régimen, domicilio, obligaciones) sin extraer todavía.",
            "simulated": False,
        }

    def descargar_buzon_tributario(self, rfc: str) -> dict[str, Any]:
        self._log("descargar_buzon_tributario", {"rfc": rfc})
        if not self._mock():
            raise UpstreamError(
                "Buzón Tributario real no implementado (flujo no portado ni validado). "
                f"Revísalo manualmente con e.firma: {URL_BUZON_TRIBUTARIO}",
                {"handoff_url": URL_BUZON_TRIBUTARIO},
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
        """Solicita al WS Descarga Masiva del SAT (vía mp_sat_ws) los CFDI de un mes."""
        self._log(
            "descargar_cfdi_masivo",
            {"rfc": rfc, "ejercicio": ejercicio, "mes": mes, "tipo": tipo},
        )
        if self._mock():
            return mark_simulated(
                mock_data.mock_cfdi_masivo(rfc, ejercicio, mes, tipo),
                "Descarga masiva requiere e.firma — simulación de solicitud.",
            )
        from calendar import monthrange

        from mp_sat_ws.client import Fiel, SatWsClient
        from shared.sat_ws import URL_SOLICITAR_DESCARGA, SolicitudDescarga

        ultimo_dia = monthrange(ejercicio, mes)[1]
        sol = SolicitudDescarga(
            rfc_emisor=rfc.strip().upper(),
            fecha_inicial=f"{ejercicio:04d}-{mes:02d}-01T00:00:00",
            fecha_final=f"{ejercicio:04d}-{mes:02d}-{ultimo_dia:02d}T23:59:59",
            tipo_solicitud="CFDI",
            tipo_descarga=tipo.lower(),  # type: ignore[arg-type]
        )
        # Fiel.from_env() levanta ConfigError si faltan SAT_EFIRMA_*: nunca cae a mock.
        r = SatWsClient(fiel=Fiel.from_env()).solicitar_descarga(sol)
        return {
            "rfc": r["rfc_emisor"],
            "ejercicio": ejercicio,
            "mes": mes,
            "tipo": tipo.lower(),
            "solicitud_id": r["id_solicitud"],
            "estado_solicitud": "ACEPTADA",
            "cod_estatus": r["cod_estatus"],
            "mensaje": r["mensaje"],
            "fecha_solicitud": r["fecha_solicitud"],
            "instrucciones": (
                "Consulta el avance con sat_ws_verificar_solicitud(id_solicitud, rfc_emisor) "
                "cada >=30 s; cuando esté TERMINADA baja cada paquete con sat_ws_descargar_paquete."
            ),
            "fuente": URL_SOLICITAR_DESCARGA,
            "simulated": False,
        }

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

    def verificar_efirma_vigente(self, rfc: str, *, verificar_en_portal: bool = True) -> dict[str, Any]:
        """Vigencia real de la e.firma de SAT_EFIRMA_*.

        1. Local (sin red): lee el .cer (RFC, número de certificado, vigencia),
           abre el .key con la contraseña y comprueba que el par corresponde.
        2. Portal (opcional): login FIEL a loginda.siat.sat.gob.mx. El SAT
           responde "Certificado Revocado" / "Certificado Caduco" si no la
           acepta. Es la forma pública de detectar revocación: el OCSP del SAT
           para FIEL es solo para convenios.
        """
        self._log("verificar_efirma_vigente", {"rfc": rfc})
        if self._mock():
            return mark_simulated(
                mock_data.mock_efirma_status(rfc),
                "Status e.firma requiere e.firma — simulación.",
            )
        from mp_sat_portal.efirma_loader import EfirmaLoader
        from shared.sat_portal_fiel import URL_LOGIN_PORTAL, SatFielSession

        loader = EfirmaLoader.from_env()
        meta = loader.metadata()
        rfc_norm = rfc.strip().upper()
        par_ok = loader.validate_key_pair()
        out: dict[str, Any] = {
            **meta.to_dict(),
            "rfc_solicitado": rfc_norm,
            "rfc_coincide": meta.rfc == rfc_norm,
            "llave_corresponde_al_certificado": par_ok,
            "verificacion_portal": None,
            "simulated": False,
        }
        if verificar_en_portal and par_ok and meta.is_valid_now:
            try:
                with SatFielSession(loader) as sesion:
                    sesion.login_portal()
                out["verificacion_portal"] = {"aceptada_por_sat": True, "url": URL_LOGIN_PORTAL}
            except AuthError as exc:
                out["verificacion_portal"] = {
                    "aceptada_por_sat": False,
                    "motivo_sat": exc.details.get("motivo"),
                    "url": URL_LOGIN_PORTAL,
                }
        portal = out["verificacion_portal"]
        out["vigente"] = bool(
            meta.is_valid_now and par_ok and (portal is None or portal["aceptada_por_sat"])
        )
        return out

    def descargar_acuse(self, folio: str) -> dict[str, Any]:
        self._log("descargar_acuse", {"folio": folio})
        if not self._mock():
            raise UpstreamError(
                "Descarga de acuses real no implementada (flujo no portado ni validado). "
                f"Reimprímelo manualmente con e.firma: {URL_REIMPRESION_ACUSES}",
                {"handoff_url": URL_REIMPRESION_ACUSES},
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

    # ============ Sprint F — profundización ============

    def calendario_fiscal_por_regimen(
        self, rfc: str, regimen: str, anio: int
    ) -> dict[str, Any]:
        """Calendario fiscal anual por régimen — local, sin red.

        Construye las fechas límite mensuales/anuales aplicables al régimen
        usando reglas RMF 2026 + UMA 2026. No requiere auth.
        """
        from datetime import date as _date

        self._log(
            "calendario_fiscal_por_regimen",
            {"rfc": rfc, "regimen": regimen, "anio": anio},
        )
        reg = (regimen or "").strip().upper()
        # Calendario RMF: pago provisional ISR + IVA mensual el día 17 del mes siguiente
        # RESICO: día 17 mensual + anual abril. RIF: bimestral día 17 del 2do mes.
        # PM 601: provisional 17 + anual marzo siguiente.
        # Asalariados 605: anual abril.
        DIA_LIMITE_MENSUAL = 17
        declaraciones: list[dict[str, Any]] = []

        def _agregar_mensual(concepto: str, descripcion: str) -> None:
            for mes in range(1, 13):
                # Vence el día 17 del mes siguiente
                vence_mes = mes + 1 if mes < 12 else 1
                vence_anio = anio if mes < 12 else anio + 1
                declaraciones.append(
                    {
                        "concepto": concepto,
                        "periodo": f"{anio}-{mes:02d}",
                        "fecha_limite": _date(vence_anio, vence_mes, DIA_LIMITE_MENSUAL).isoformat(),
                        "descripcion": descripcion,
                    }
                )

        if reg in {"626", "RESICO", "RESICO_PF"}:
            _agregar_mensual("ISR_RESICO_PROV", "Pago provisional ISR RESICO (1.00-2.50%)")
            _agregar_mensual("IVA_MENSUAL", "IVA mensual (RMF 2026)")
            declaraciones.append(
                {
                    "concepto": "ISR_RESICO_ANUAL",
                    "periodo": f"{anio}",
                    "fecha_limite": _date(anio + 1, 4, 30).isoformat(),
                    "descripcion": "Declaración anual RESICO PF — abril año siguiente",
                }
            )
        elif reg in {"601", "PM_GENERAL"}:
            _agregar_mensual("ISR_PROVISIONAL", "Pago provisional ISR PM (Art. 14 LISR)")
            _agregar_mensual("IVA_MENSUAL", "IVA mensual")
            _agregar_mensual("IEPS_MENSUAL", "IEPS mensual (si aplica)")
            declaraciones.append(
                {
                    "concepto": "ISR_ANUAL_PM",
                    "periodo": f"{anio}",
                    "fecha_limite": _date(anio + 1, 3, 31).isoformat(),
                    "descripcion": "Declaración anual PM — marzo año siguiente",
                }
            )
        elif reg in {"605", "ASALARIADOS"}:
            declaraciones.append(
                {
                    "concepto": "ISR_ANUAL_PF",
                    "periodo": f"{anio}",
                    "fecha_limite": _date(anio + 1, 4, 30).isoformat(),
                    "descripcion": "Declaración anual PF — abril año siguiente",
                }
            )
        elif reg in {"612", "ACTIVIDAD_EMPRESARIAL_PF", "PF_AGE"}:
            _agregar_mensual("ISR_PROVISIONAL", "Pago provisional ISR PF AGE")
            _agregar_mensual("IVA_MENSUAL", "IVA mensual")
            declaraciones.append(
                {
                    "concepto": "ISR_ANUAL_PF",
                    "periodo": f"{anio}",
                    "fecha_limite": _date(anio + 1, 4, 30).isoformat(),
                    "descripcion": "Declaración anual PF — abril año siguiente",
                }
            )
        else:
            return {
                "rfc": rfc,
                "regimen_solicitado": regimen,
                "error": "regimen_no_reconocido",
                "regimenes_soportados": [
                    "601 (PM General)",
                    "605 (Asalariados)",
                    "612 (PF Actividad Empresarial)",
                    "626 (RESICO)",
                ],
            }

        return {
            "rfc": rfc,
            "regimen": regimen,
            "anio": anio,
            "total_declaraciones": len(declaraciones),
            "declaraciones": declaraciones,
            "nota_uma_2026": "UMA 2026 diaria: $117.31 (INEGI, DOF 09-01-2026) — usar para topes IMSS/INFONAVIT relacionados.",
            "fuente": "RMF 2026 + LISR Art. 14, 113-E, 113-J",
        }

    def cfdi_prevalidar(self, xml: str, tipo: str) -> dict[str, Any]:
        """Pre-validación estructural CFDI 4.0 SIN timbrar.

        Verifica elementos requeridos por el SAT antes de enviar al PAC.
        Detecta los errores más comunes que el PAC rechazaría con código.
        Local, sin red.
        """
        import re as _re

        self._log("cfdi_prevalidar", {"tipo": tipo, "xml_len": len(xml or "")})
        errores: list[dict[str, str]] = []
        advertencias: list[dict[str, str]] = []
        xml_text = (xml or "").strip()

        if not xml_text:
            return {
                "valido": False,
                "tipo": tipo,
                "errores": [{"codigo": "CFDI40000", "descripcion": "XML vacío."}],
            }

        # Verificaciones estructurales mínimas CFDI 4.0
        if "cfdi:Comprobante" not in xml_text:
            errores.append(
                {"codigo": "CFDI40101", "descripcion": "Falta nodo raíz cfdi:Comprobante."}
            )
        if 'Version="4.0"' not in xml_text:
            errores.append(
                {"codigo": "CFDI40102", "descripcion": "Atributo Version no es 4.0 (CFDI 3.3 retirado desde 2023)."}
            )
        if "cfdi:Emisor" not in xml_text:
            errores.append(
                {"codigo": "CFDI40103", "descripcion": "Falta nodo cfdi:Emisor."}
            )
        if "cfdi:Receptor" not in xml_text:
            errores.append(
                {"codigo": "CFDI40104", "descripcion": "Falta nodo cfdi:Receptor."}
            )
        if 'RegimenFiscalReceptor' not in xml_text:
            errores.append(
                {"codigo": "CFDI40105", "descripcion": "Falta atributo RegimenFiscalReceptor (obligatorio 4.0)."}
            )
        if 'DomicilioFiscalReceptor' not in xml_text:
            errores.append(
                {"codigo": "CFDI40106", "descripcion": "Falta atributo DomicilioFiscalReceptor (CP del receptor)."}
            )
        if "cfdi:Conceptos" not in xml_text:
            errores.append(
                {"codigo": "CFDI40107", "descripcion": "Falta nodo cfdi:Conceptos."}
            )
        if 'UsoCFDI=' not in xml_text:
            errores.append(
                {"codigo": "CFDI40108", "descripcion": "Falta atributo UsoCFDI en Receptor."}
            )
        if 'ObjetoImp=' not in xml_text:
            errores.append(
                {"codigo": "CFDI40109", "descripcion": "Falta atributo ObjetoImp en concepto (01/02/03/04)."}
            )

        # Validaciones por tipo
        tipo_norm = (tipo or "").upper().strip()
        if tipo_norm == "PAGO":
            if "pago20:Pagos" not in xml_text:
                errores.append(
                    {"codigo": "CFDI40201", "descripcion": "Complemento pago20:Pagos requerido para tipo PAGO."}
                )
        if tipo_norm == "NOMINA":
            if "nomina12:Nomina" not in xml_text:
                errores.append(
                    {"codigo": "CFDI40301", "descripcion": "Complemento nomina12:Nomina requerido para tipo NOMINA."}
                )
        if tipo_norm == "CARTAPORTE":
            if "cartaporte31:" not in xml_text and "cartaporte30:" not in xml_text:
                errores.append(
                    {"codigo": "CFDI40401", "descripcion": "Complemento CartaPorte 3.1 (o 3.0) requerido para tipo CARTAPORTE."}
                )

        # Advertencias (no bloquean timbrado)
        if 'TipoDeComprobante="I"' in xml_text and "MetodoPago=" not in xml_text:
            advertencias.append(
                {"codigo": "ADV001", "descripcion": "Falta MetodoPago en comprobante tipo Ingreso (PUE/PPD)."}
            )

        # RFC normalization check
        m = _re.search(r'Emisor[^>]*Rfc="([^"]+)"', xml_text)
        if m and not _re.match(r"^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$", m.group(1).upper()):
            errores.append(
                {"codigo": "CFDI40110", "descripcion": f"RFC emisor con formato inválido: {m.group(1)}"}
            )

        return {
            "valido": len(errores) == 0,
            "tipo": tipo,
            "total_errores": len(errores),
            "total_advertencias": len(advertencias),
            "errores": errores,
            "advertencias": advertencias,
            "nota": "Pre-validación estructural local. NO sustituye validación del PAC.",
        }

    def declaraciones_historico(
        self, rfc: str, anio: int
    ) -> dict[str, Any]:
        """Histórico de declaraciones por RFC y año.

        Path real requiere e.firma o CIEC. Mock por default con shape plausible.
        """
        self._log("declaraciones_historico", {"rfc": rfc, "anio": anio})
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + e.firma. No implementado todavía."
            )
        from datetime import date as _date
        import hashlib as _hash

        rfc_norm = (rfc or "").strip().upper()
        h = int(_hash.sha256(rfc_norm.encode()).hexdigest(), 16)
        regimen = "626" if len(rfc_norm) == 13 else "601"

        declaraciones = []
        for mes in range(1, 13):
            presentada = (h >> mes) & 1 or mes <= 9
            folio = f"AC{anio}{mes:02d}{(h % 100000):05d}"
            declaraciones.append(
                {
                    "concepto": "ISR_PROVISIONAL" if regimen == "601" else "ISR_RESICO_PROV",
                    "periodo": f"{anio}-{mes:02d}",
                    "presentada": bool(presentada),
                    "fecha_presentacion": (
                        _date(anio, mes + 1 if mes < 12 else 1, 15).isoformat()
                        if presentada and mes < 12
                        else None
                    ),
                    "folio_acuse": folio if presentada else None,
                    "isr_pagado_mxn": round((h % 50000) + 1500.0 + mes * 100, 2) if presentada else 0.0,
                    "iva_pagado_mxn": round((h % 30000) + 800.0 + mes * 50, 2) if presentada else 0.0,
                }
            )

        omitidas = [d for d in declaraciones if not d["presentada"]]
        return mark_simulated(
            {
                "rfc": rfc_norm,
                "anio": anio,
                "regimen": regimen,
                "total_declaraciones_periodo": len(declaraciones),
                "presentadas": len(declaraciones) - len(omitidas),
                "omitidas": len(omitidas),
                "alerta_resico_3_omisiones": regimen == "626" and len(omitidas) >= 3,
                "declaraciones": declaraciones,
            },
            "Histórico real requiere e.firma — datos simulados.",
        )

    def devolucion_estatus(self, folio: str) -> dict[str, Any]:
        """Estatus de solicitud de devolución (Forma 41/14).

        Path real requiere e.firma + sesión activa SAT. Mock por default.
        """
        self._log("devolucion_estatus", {"folio": folio})
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + e.firma. No implementado todavía."
            )
        from datetime import date as _date, timedelta as _td
        import hashlib as _hash

        folio_norm = (folio or "").strip().upper()
        h = int(_hash.sha256(folio_norm.encode()).hexdigest(), 16)
        fases = [
            "RECIBIDA",
            "EN_REVISION",
            "INFO_ADICIONAL_REQUERIDA",
            "AUTORIZADA",
            "DEPOSITADA",
            "RECHAZADA",
        ]
        fase = fases[h % len(fases)]
        dias_transcurridos = h % 60
        return mark_simulated(
            {
                "folio": folio_norm,
                "fase_actual": fase,
                "fecha_recepcion": (_date.today() - _td(days=dias_transcurridos)).isoformat(),
                "dias_transcurridos": dias_transcurridos,
                "monto_solicitado_mxn": round((h % 200000) + 5000.0, 2),
                "monto_autorizado_mxn": (
                    round((h % 180000) + 4500.0, 2)
                    if fase in {"AUTORIZADA", "DEPOSITADA"}
                    else None
                ),
                "siguiente_paso": {
                    "RECIBIDA": "SAT analizará la solicitud en 10-15 días hábiles.",
                    "EN_REVISION": "Esperar resolución (max 40 días hábiles).",
                    "INFO_ADICIONAL_REQUERIDA": "Atender requerimiento en Buzón Tributario.",
                    "AUTORIZADA": "Depósito a CLABE registrada en próximos 10 días.",
                    "DEPOSITADA": "Trámite concluido.",
                    "RECHAZADA": "Revisar motivo en acuse para impugnar (45 días).",
                }[fase],
                "plazo_legal_max_dias_habiles": 40,
            },
            "Estatus real requiere e.firma — datos simulados.",
        )

    def buzon_notificaciones_resumen(
        self,
        rfc: str,
        solo_pendientes: bool = True,
    ) -> dict[str, Any]:
        """Resumen agregado del Buzón Tributario con conteo de urgentes.

        Complementa `descargar_buzon_tributario` con filtros y métricas.
        Path real requiere e.firma.
        """
        self._log(
            "buzon_notificaciones_resumen",
            {"rfc": rfc, "solo_pendientes": solo_pendientes},
        )
        if not self._mock():
            raise UpstreamError(
                "Path real requiere Playwright + e.firma. No implementado todavía."
            )
        from datetime import date as _date, timedelta as _td
        import hashlib as _hash

        rfc_norm = (rfc or "").strip().upper()
        h = int(_hash.sha256(rfc_norm.encode()).hexdigest(), 16)
        tipos = ["REQUERIMIENTO", "CITATORIO", "INVITACION", "RESOLUCION", "CARTA_INVITACION"]
        notificaciones = []
        for i in range(h % 8):
            dias = (h >> (i + 1)) % 30
            tipo = tipos[(h + i) % len(tipos)]
            fecha = _date.today() - _td(days=dias)
            plazo = {"REQUERIMIENTO": 15, "CITATORIO": 5, "INVITACION": 30, "RESOLUCION": 30, "CARTA_INVITACION": 90}[tipo]
            vence = fecha + _td(days=plazo)
            notificaciones.append(
                {
                    "folio": f"BT{(h + i) % 1000000:06d}",
                    "tipo": tipo,
                    "fecha_notificacion": fecha.isoformat(),
                    "fecha_vencimiento_respuesta": vence.isoformat(),
                    "dias_restantes": (vence - _date.today()).days,
                    "leido": bool((h >> (i + 5)) & 1),
                }
            )

        if solo_pendientes:
            notificaciones = [n for n in notificaciones if not n["leido"]]

        urgentes = [n for n in notificaciones if n["dias_restantes"] <= 5]
        vencidas = [n for n in notificaciones if n["dias_restantes"] < 0]

        return mark_simulated(
            {
                "rfc": rfc_norm,
                "total_notificaciones": len(notificaciones),
                "total_urgentes_5d": len(urgentes),
                "total_vencidas": len(vencidas),
                "requiere_atencion_inmediata": len(urgentes) > 0 or len(vencidas) > 0,
                "notificaciones": notificaciones,
                "fuente_legal": "Art. 17-K CFF (Buzón Tributario obligatorio).",
            },
            "Buzón real requiere e.firma — datos simulados.",
        )


# ---------- ConsultaCFDIService (SOAP público del SAT) ----------

URL_CONSULTA_CFDI = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc"
_ACCION_CONSULTA_CFDI = "http://tempuri.org/IConsultaCFDIService/Consulta"
_NS_CONSULTA = "http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio"


def _consultar_cfdi_soap(
    uuid: str, rfc_emisor: str, rfc_receptor: str, total: str, timeout: float = 30.0
) -> dict[str, Any]:
    """POST a ConsultaCFDIService y normaliza la respuesta."""
    import xml.etree.ElementTree as ET
    from decimal import Decimal, InvalidOperation
    from xml.sax.saxutils import escape

    from shared.errors import ValidationError, handle_httpx_error

    rfc_e, rfc_r = rfc_emisor.strip().upper(), rfc_receptor.strip().upper()
    try:
        tt = f"{Decimal(str(total).replace(',', '')):.6f}"
    except InvalidOperation:
        raise ValidationError(f"total no es numérico: {total!r}")
    expresion = f"?re={rfc_e}&rr={rfc_r}&tt={tt}&id={uuid}"
    cuerpo = (
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
        '<c:Consulta xmlns:c="http://tempuri.org/"><c:expresionImpresa>'
        f"{escape(expresion)}</c:expresionImpresa></c:Consulta></s:Body></s:Envelope>"
    )
    try:
        resp = httpx.post(
            URL_CONSULTA_CFDI,
            content=cuerpo.encode("utf-8"),
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": _ACCION_CONSULTA_CFDI,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise handle_httpx_error(exc)
    try:
        raiz = ET.fromstring(resp.content)
    except ET.ParseError:
        raise UpstreamError(
            "ConsultaCFDIService respondió sin XML válido.",
            {"body_preview": resp.text[:300]},
        )

    def campo(nombre: str) -> str | None:
        valor = raiz.findtext(f".//{{{_NS_CONSULTA}}}{nombre}")
        return (valor or "").strip() or None

    codigo = campo("CodigoEstatus")
    if codigo is None:
        raise UpstreamError(
            "Respuesta de ConsultaCFDIService sin CodigoEstatus.",
            {"body_preview": resp.text[:300]},
        )
    return {
        "uuid": uuid,
        "rfc_emisor": rfc_e,
        "rfc_receptor": rfc_r,
        "total_consultado": tt,
        "encontrado": codigo.startswith("S"),  # "S - Comprobante obtenido…" | "N - 60x: …"
        "codigo_estatus": codigo,
        "estado_cfdi": campo("Estado"),  # Vigente | Cancelado | No Encontrado
        "es_cancelable": campo("EsCancelable"),
        "estado_cancelacion": campo("EstatusCancelacion"),
        "validacion_efos": campo("ValidacionEFOS"),
        "fuente": URL_CONSULTA_CFDI,
        "valido_estructuralmente": True,
        "simulated": False,
    }
