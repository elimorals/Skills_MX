"""Cliente CEP (Constancia de Pago Electrónico) — Banxico.

Banxico no tiene API REST documentada; el portal https://www.banxico.org.mx/cep/
usa endpoints form/JSON que replicamos con httpx (ver `spei.py`).

Modos:
- **Real (default)**: httpx contra valida.do / instituciones.do / descarga.do.
  Si el portal falla → `UpstreamError`; si activa el CAPTCHA visible → handoff
  humano estructurado (nunca se resuelve el CAPTCHA).
- **Mock** solo con `PLUGINS_MX_MOCK=1`: respuestas determinísticas marcadas
  `simulated: true`.

Cache: CEP por clave se cachea 90 días; consultas de estado "no encontrado" no
se cachean (el SPEI puede liquidarse después).
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_banxico_cep import spei  # noqa: E402
from mp_banxico_cep.catalogos import BANCOS_CLABE, ESTADO_CEP, lookup_banco  # noqa: E402
from mp_banxico_cep.clabe import parsear_clave_rastreo  # noqa: E402
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402

NAMESPACE = "banxico_cep_mcp"
CACHE_CEP_DIAS = 90
CACHE_CONSULTA_DIAS = 30


def handoff_captcha(campos: dict[str, Any]) -> dict[str, Any]:
    """Respuesta para cuando Banxico exige CAPTCHA: lo completa una persona."""
    return {
        "requiere_humano": True,
        "motivo": "captcha_requerido",
        "url": spei.BASE_URL,
        "pasos": [
            "Abrir la URL en un navegador.",
            "Capturar fecha, clave de rastreo, instituciones emisora/receptora, cuenta y monto (abajo).",
            "Escribir el código de la imagen de seguridad y pulsar 'Descargar CEP' o 'Consultar Pago'.",
        ],
        "campos_prellenados": campos,
        "simulated": False,
    }


class BanxicoCepClient:
    """Cliente para generar y validar CEP de pagos SPEI."""

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

    # ---------- camino real ----------

    def _consulta_real(
        self,
        *,
        clave_rastreo: str,
        fecha_operacion: date,
        banco_emisor: str,
        banco_receptor: str,
        cuenta: str = "",
        monto: float | None = None,
        tipo_consulta: int = 0,
        formato_descarga: str | None = None,
    ) -> dict[str, Any]:
        campos = {
            "fecha": spei.fecha_portal(fecha_operacion),
            "clave_rastreo": clave_rastreo,
            "banco_emisor": banco_emisor,
            "banco_receptor": banco_receptor,
            "cuenta_beneficiaria": cuenta or None,
            "monto": monto,
        }
        try:
            with spei.nuevo_cliente() as http:
                spei.abrir_sesion(http)
                catalogo = spei.instituciones(http, fecha_operacion)
                emisor = spei.clave_participante(catalogo, banco_emisor)
                receptor = spei.clave_participante(catalogo, banco_receptor)
                if not emisor or not receptor:
                    raise ValidationError(
                        "Banco emisor/receptor no es participante SPEI en esa fecha según Banxico.",
                        {"emisor": banco_emisor, "receptor": banco_receptor,
                         "fecha": campos["fecha"]},
                    )
                res = spei.consultar(
                    http,
                    fecha=fecha_operacion,
                    clave_rastreo=clave_rastreo,
                    emisor=emisor["clave"],
                    receptor=receptor["clave"],
                    cuenta=cuenta,
                    monto=monto,
                    tipo_consulta=tipo_consulta,
                )
                out: dict[str, Any] = {
                    "clave_rastreo": clave_rastreo,
                    "fecha_operacion": fecha_operacion.isoformat(),
                    "banco_emisor": {"clave": banco_emisor, "participante": emisor},
                    "banco_receptor": {"clave": banco_receptor, "participante": receptor},
                    "estado": res["estado"],
                    "mensaje_portal": res["mensaje"],
                    "fuente": spei.BASE_URL,
                    "consultado_en": datetime.now(timezone.utc).isoformat(),
                    "simulated": False,
                }
                encontrado = res["estado"] in ("cep_disponible", "liquidado", "devuelto")
                if formato_descarga and encontrado:
                    contenido = spei.descargar(http, formato_descarga)
                    out["_descarga"] = contenido
                return out
        except spei.CaptchaRequerido:
            return handoff_captcha(campos)

    # ---------- generar_cep ----------

    async def generar_cep(
        self,
        clave_rastreo: str,
        fecha_operacion: date,
        banco_emisor: str,
        banco_receptor: str,
        monto: float,
        cuenta_beneficiaria: str | None = None,
    ) -> dict[str, Any]:
        """Solicita el CEP a Banxico (requiere cuenta beneficiaria y monto exacto)."""
        self._validar_datos_basicos(banco_emisor, banco_receptor, monto, clave_rastreo)

        cache_key = self._cache_key_cep(
            clave_rastreo, fecha_operacion, banco_emisor, banco_receptor, monto
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_cep(
                clave_rastreo, fecha_operacion, banco_emisor, banco_receptor, monto
            )
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_CEP_DIAS)
            self._log("generar_cep", clave_rastreo, fecha_operacion, "mock", banco_emisor,
                      banco_receptor, monto)
            return response

        if not cuenta_beneficiaria:
            raise ValidationError(
                "Banxico exige la cuenta beneficiaria (CLABE, tarjeta o celular) para emitir el CEP."
            )
        res = await asyncio.to_thread(
            self._consulta_real,
            clave_rastreo=clave_rastreo,
            fecha_operacion=fecha_operacion,
            banco_emisor=banco_emisor,
            banco_receptor=banco_receptor,
            cuenta=cuenta_beneficiaria,
            monto=monto,
            tipo_consulta=1,
            formato_descarga="XML",
        )
        if res.get("requiere_humano"):
            return res
        xml = res.pop("_descarga", None)
        res["cep_disponible"] = xml is not None
        res["estado_descripcion"] = ESTADO_CEP.get(res["estado"], res["mensaje_portal"])
        if xml is not None:
            res["cep"] = spei.parsear_xml_cep(xml)
            self._cache.set(cache_key, res, ttl_hours=24 * CACHE_CEP_DIAS)
        self._log("generar_cep", clave_rastreo, fecha_operacion, "real", banco_emisor,
                  banco_receptor, monto)
        return res

    # ---------- validar_cep ----------

    async def validar_cep(
        self,
        clave_rastreo: str,
        fecha_operacion: date | None = None,
        banco_emisor: str | None = None,
        banco_receptor: str | None = None,
    ) -> dict[str, Any]:
        """Consulta el estado del pago (sin cuenta ni monto)."""
        parseo = parsear_clave_rastreo(clave_rastreo)
        if not parseo["formato_valido"]:
            raise ValidationError(
                f"Clave de rastreo con formato inválido. Alertas: {parseo['alertas']}"
            )

        cache_key = f"validar_{clave_rastreo.upper()}_{fecha_operacion}_{banco_emisor}_{banco_receptor}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            # Heurística determinística: claves cuyo hash[0] es par → existe, impar → no
            seed = int(hashlib.sha256(clave_rastreo.encode()).hexdigest()[0], 16)
            existe = seed % 2 == 0
            response = mark_simulated(
                {
                    "clave_rastreo": clave_rastreo,
                    "existe_en_banxico": existe,
                    "estado": "disponible" if existe else "no_encontrado",
                    "estado_descripcion": ESTADO_CEP[
                        "disponible" if existe else "no_encontrado"
                    ],
                    "consultado_en": datetime.now(timezone.utc).isoformat(),
                    "emisor_probable": parseo["emisor_probable"],
                }
            )
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_CONSULTA_DIAS)
            return response

        if not (fecha_operacion and banco_emisor and banco_receptor):
            raise ValidationError(
                "Banxico exige fecha_operacion, banco_emisor y banco_receptor para consultar el pago."
            )
        for b in (banco_emisor, banco_receptor):
            if not lookup_banco(b):
                raise ValidationError(f"Banco '{b}' no está en el catálogo de códigos CLABE.")
        res = await asyncio.to_thread(
            self._consulta_real,
            clave_rastreo=clave_rastreo,
            fecha_operacion=fecha_operacion,
            banco_emisor=banco_emisor,
            banco_receptor=banco_receptor,
        )
        if res.get("requiere_humano"):
            return res
        res["existe_en_banxico"] = res["estado"] in ("cep_disponible", "liquidado", "devuelto")
        if res["existe_en_banxico"]:
            self._cache.set(cache_key, res, ttl_hours=24 * CACHE_CONSULTA_DIAS)
        self._log("validar_cep", clave_rastreo, fecha_operacion, "real", banco_emisor,
                  banco_receptor, None)
        return res

    # ---------- descargar_pdf ----------

    async def descargar_pdf_cep(
        self,
        clave_rastreo: str,
        fecha_operacion: date,
        banco_emisor: str,
        banco_receptor: str,
        monto: float,
        cuenta_beneficiaria: str | None = None,
    ) -> dict[str, Any]:
        """Descarga el PDF oficial del CEP a un archivo local."""
        self._validar_datos_basicos(banco_emisor, banco_receptor, monto, clave_rastreo)

        if self._mock_mode:
            cep = await self.generar_cep(
                clave_rastreo, fecha_operacion, banco_emisor, banco_receptor, monto
            )
            return mark_simulated(
                {
                    "clave_rastreo": clave_rastreo,
                    "pdf_path": f"/mock/cep/{clave_rastreo.upper()}.pdf",
                    "pdf_bytes": 0,
                    "cep_disponible": cep["cep_disponible"],
                    "nota": "Modo mock — no se generó PDF real.",
                }
            )

        if not cuenta_beneficiaria:
            raise ValidationError(
                "Banxico exige la cuenta beneficiaria para descargar el CEP."
            )
        res = await asyncio.to_thread(
            self._consulta_real,
            clave_rastreo=clave_rastreo,
            fecha_operacion=fecha_operacion,
            banco_emisor=banco_emisor,
            banco_receptor=banco_receptor,
            cuenta=cuenta_beneficiaria,
            monto=monto,
            tipo_consulta=1,
            formato_descarga="PDF",
        )
        if res.get("requiere_humano"):
            return res
        pdf = res.pop("_descarga", None)
        res["cep_disponible"] = pdf is not None
        if pdf is not None:
            destino = Path(tempfile.gettempdir()) / "plugins-mx-cep"
            destino.mkdir(parents=True, exist_ok=True)
            path = destino / f"{clave_rastreo.upper()}_{fecha_operacion.isoformat()}.pdf"
            path.write_bytes(pdf)
            res["pdf_path"] = str(path)
            res["pdf_bytes"] = len(pdf)
        return res

    # ---------- consultar_pago_por_clave ----------

    async def consultar_pago_por_clave(self, clave_rastreo: str) -> dict[str, Any]:
        """Con solo la clave no se puede consultar Banxico: indica qué falta."""
        parseo = parsear_clave_rastreo(clave_rastreo)
        if not parseo["formato_valido"]:
            raise ValidationError(
                f"Clave de rastreo con formato inválido. Alertas: {parseo['alertas']}"
            )

        if self._mock_mode:
            seed_hex = hashlib.sha256(clave_rastreo.encode()).hexdigest()
            monto_mock = round(100.0 + int(seed_hex[:6], 16) % 50000 / 100.0, 2)
            return mark_simulated(
                {
                    "clave_rastreo": clave_rastreo,
                    "emisor_probable": parseo["emisor_probable"],
                    "monto_estimado_mock": monto_mock,
                    "nota": "Modo mock — datos derivados algorítmicamente de la clave.",
                }
            )

        raise ValidationError(
            "Banxico CEP exige fecha_operacion, banco_emisor, banco_receptor y monto "
            "para emitir un CEP. La clave de rastreo sola no es suficiente. "
            "Recopila esos datos del cliente y llama a generar_cep."
        )

    def _log(self, op, clave, fecha, mode, emisor, receptor, monto) -> None:
        self._bitacora.log(
            op,
            success=True,
            params_summary={
                "clave_hash": Bitacora.hash_sensitive(clave),
                "fecha": fecha.isoformat(),
                "banco_emisor": emisor,
                "banco_receptor": receptor,
                "monto": monto,
                "mode": mode,
            },
        )

    # ---------- helpers ----------

    @staticmethod
    def _validar_datos_basicos(
        banco_emisor: str,
        banco_receptor: str,
        monto: float,
        clave_rastreo: str,
    ) -> None:
        if not lookup_banco(banco_emisor):
            raise ValidationError(
                f"Banco emisor '{banco_emisor}' no está en el catálogo conocido. "
                "Verificar código de 3 dígitos contra catalogos.BANCOS_CLABE."
            )
        if not lookup_banco(banco_receptor):
            raise ValidationError(
                f"Banco receptor '{banco_receptor}' no está en el catálogo conocido."
            )
        if monto <= 0:
            raise ValidationError("Monto debe ser positivo.")
        if not parsear_clave_rastreo(clave_rastreo)["formato_valido"]:
            raise ValidationError(
                f"Clave de rastreo con formato inválido: '{clave_rastreo}'."
            )

    @staticmethod
    def _cache_key_cep(
        clave: str, fecha: date, emisor: str, receptor: str, monto: float
    ) -> str:
        # Hash compacto de los identificadores — la combinación es única por SPEI
        raw = f"{clave}|{fecha.isoformat()}|{emisor}|{receptor}|{monto:.2f}".upper()
        h = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return f"cep_{h}"

    @staticmethod
    def _mock_cep(
        clave: str, fecha: date, emisor: str, receptor: str, monto: float
    ) -> dict[str, Any]:
        """Construye una respuesta CEP determinística para tests/mock."""
        seed = hashlib.sha256(clave.encode()).hexdigest()
        hora_seed = int(seed[6:8], 16) % 24
        min_seed = int(seed[8:10], 16) % 60
        seg_seed = int(seed[10:12], 16) % 60
        cuenta_ord = "**** " + seed[12:16]
        cuenta_ben = "**** " + seed[16:20]

        return mark_simulated(
            {
                "clave_rastreo": clave,
                "fecha_operacion": fecha.isoformat(),
                "hora_operacion": f"{hora_seed:02d}:{min_seed:02d}:{seg_seed:02d}",
                "banco_emisor": {
                    "clave": emisor,
                    "nombre": lookup_banco(emisor),
                },
                "banco_receptor": {
                    "clave": receptor,
                    "nombre": lookup_banco(receptor),
                },
                "monto": round(monto, 2),
                "moneda": "MXN",
                "ordenante": {
                    "nombre": "ORDENANTE MOCK",
                    "cuenta_enmascarada": cuenta_ord,
                },
                "beneficiario": {
                    "nombre": "BENEFICIARIO MOCK",
                    "cuenta_enmascarada": cuenta_ben,
                },
                "concepto": "Pago referencia mock",
                "referencia": seed[:8],
                "cep_disponible": True,
                "estado": "disponible",
                "estado_descripcion": ESTADO_CEP["disponible"],
                "pdf_url": f"https://www.banxico.org.mx/cep/?mock={seed[:12]}",
                "generado_en": datetime.now(timezone.utc).isoformat(),
            }
        )
