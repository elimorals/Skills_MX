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
            "nota_uma_2026": "UMA 2026 diaria: $113.07 — usar para topes IMSS/INFONAVIT relacionados.",
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
