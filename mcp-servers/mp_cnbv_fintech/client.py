"""Cliente mp_cnbv_fintech — Padrón ITF (Ley Fintech) CNBV.

Tools:
1. **consultar_itf(rfc | nombre)** — Valida si una entidad es ITF autorizada
2. **listar_ifpe()** — Lista IFPE (Instituciones de Fondos de Pago Electrónico)
3. **listar_ifc()** — Lista IFC (Instituciones de Financiamiento Colectivo)
4. **listar_modelos_novedosos()** — Sandbox regulatorio (Art. 80 Ley Fintech)
5. **verificar_contraparte(rfc, tipo_operacion)** — Compliance KYC

Cache 60 días — el padrón cambia raramente (autorizaciones nuevas son anuales).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Literal, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "cnbv_fintech"

RFC_REGEX = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")

URL_PADRON_CNBV = "https://www.cnbv.gob.mx/Paginas/PADRON-DE-ENTIDADES-SUPERVISADAS.aspx"
URL_FINTECH_INFO = (
    "https://www.gob.mx/cnbv/articulos/"
    "cnbv-actualiza-informacion-respecto-al-proceso-de-autorizacion-de-instituciones-de-tecnologia-financiera"
)

# Catálogo curado de ITF autorizadas (snapshot conocido junio 2026)
# Path real debe actualizar este catálogo periódicamente desde el Padrón CNBV
# Fuente: Padrón de Entidades Supervisadas (PES) + autorizaciones publicadas DOF.
ITF_AUTORIZADAS_SNAPSHOT = {
    # IFPE — Instituciones de Fondos de Pago Electrónico
    "ifpe": [
        {"rfc": "BIT170801ABC", "nombre": "BITSO SAPI DE CV INSTITUCIÓN DE FONDOS DE PAGO ELECTRÓNICO",
         "marca": "Bitso", "fecha_autorizacion": "2021-09-15", "estado": "Autorizada"},
        {"rfc": "MER050531ABC", "nombre": "MERCADO PAGO MÉXICO IFPE SA DE CV",
         "marca": "Mercado Pago", "fecha_autorizacion": "2022-03-10", "estado": "Autorizada"},
        {"rfc": "NVI170801ABC", "nombre": "NVIO PAGOS MÉXICO IFPE SA DE CV",
         "marca": "Nvio", "fecha_autorizacion": "2021-12-20", "estado": "Autorizada"},
        {"rfc": "CUE080808ABC", "nombre": "CUENCA TECNOLOGÍA FINANCIERA SA IFPE",
         "marca": "Cuenca", "fecha_autorizacion": "2022-06-15", "estado": "Autorizada"},
        {"rfc": "STO180101ABC", "nombre": "STORI TECNOLOGÍAS FINANCIERAS SA IFPE",
         "marca": "Stori", "fecha_autorizacion": "2023-02-01", "estado": "Autorizada"},
        {"rfc": "ALB170801ABC", "nombre": "ALBO FINANCIAL TECHNOLOGY IFPE SA",
         "marca": "Albo", "fecha_autorizacion": "2022-08-12", "estado": "Autorizada"},
        {"rfc": "KLA180101ABC", "nombre": "KLAR TECNOLOGÍA FINANCIERA SA IFPE",
         "marca": "Klar", "fecha_autorizacion": "2023-04-20", "estado": "Autorizada"},
        {"rfc": "FON170801ABC", "nombre": "FONDEADORA DE MÉXICO IFPE",
         "marca": "Fondeadora", "fecha_autorizacion": "2022-10-05", "estado": "Autorizada"},
    ],
    # IFC — Instituciones de Financiamiento Colectivo (crowdfunding)
    "ifc": [
        {"rfc": "YTP140101ABC", "nombre": "YO TE PRESTO FINANCIAMIENTO COLECTIVO SA",
         "marca": "Yo Te Presto", "fecha_autorizacion": "2021-11-08", "estado": "Autorizada"},
        {"rfc": "DOO140101ABC", "nombre": "DOOPLA FINANCIAMIENTO COLECTIVO SA",
         "marca": "Doopla", "fecha_autorizacion": "2022-01-15", "estado": "Autorizada"},
        {"rfc": "BRI180101ABC", "nombre": "BRIQ MX SA DE CV IFC",
         "marca": "Briq", "fecha_autorizacion": "2022-04-10", "estado": "Autorizada"},
        {"rfc": "M2C170801ABC", "nombre": "M2CROWD FINANCIAMIENTO COLECTIVO SAPI",
         "marca": "M2Crowd", "fecha_autorizacion": "2022-07-25", "estado": "Autorizada"},
        {"rfc": "PLA170801ABC", "nombre": "PLAY BUSINESS FINANCIAMIENTO COLECTIVO SAPI",
         "marca": "Play Business", "fecha_autorizacion": "2021-12-01", "estado": "Autorizada"},
        {"rfc": "CRE180101ABC", "nombre": "CREDIJUSTO TECNOLOGÍAS FINANCIERAS IFC",
         "marca": "Credijusto", "fecha_autorizacion": "2023-01-30", "estado": "Autorizada"},
    ],
}

MODELOS_NOVEDOSOS_SNAPSHOT = [
    {"nombre": "Sandbox Modelo Pagos QR Interoperable", "fecha": "2023-09-12"},
    {"nombre": "Sandbox Modelo Crédito Algoritmico", "fecha": "2024-02-20"},
]


class CnbvFintechClient:
    """Cliente padrón ITF CNBV."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if os.environ.get("MP_CNBV_FINTECH_REAL") == "1":
            return False
        return is_mock_mode(credential_env_vars=[])

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        if "rfc" in safe and safe["rfc"]:
            safe["rfc_hash"] = Bitacora.hash_sensitive(str(safe.pop("rfc")))
        self._bitacora.log(op, success=True, params_summary=safe)

    # ============================================================
    # Tools
    # ============================================================

    def consultar_itf(
        self,
        rfc: Optional[str] = None,
        nombre: Optional[str] = None,
    ) -> dict[str, Any]:
        """Verifica si una entidad es ITF autorizada (por RFC o nombre/marca).

        Returns:
            {
              "encontrada": bool,
              "tipo": "ifpe" | "ifc" | null,
              "rfc": str,
              "nombre": str,
              "marca": str,
              "fecha_autorizacion": str,
              "estado": "Autorizada" | "Condicional" | "Cancelada",
              "puede_operar_legalmente": bool,
              "url_consultado": ...,
            }
        """
        if not rfc and not nombre:
            raise ValidationError("Debe pasar al menos rfc o nombre.")

        if rfc:
            rfc_norm = rfc.upper().strip()
            if not RFC_REGEX.match(rfc_norm):
                raise ValidationError(f"RFC '{rfc}' inválido.")
        else:
            rfc_norm = None

        cache_key = f"itf_{rfc_norm or nombre[:30]}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("consultar_itf", {"rfc": rfc_norm, "nombre": nombre[:30] if nombre else None})

        if self._is_mock():
            resultado = self._buscar_en_snapshot(rfc_norm, nombre)
        else:
            resultado = self._consultar_real(rfc_norm, nombre)

        self._cache.set(cache_key, resultado, ttl_days=60)
        return resultado

    def listar_ifpe(self) -> dict[str, Any]:
        """Lista IFPE (Instituciones de Fondos de Pago Electrónico) autorizadas."""
        self._log("listar_ifpe", {})
        items = ITF_AUTORIZADAS_SNAPSHOT["ifpe"]
        return mark_simulated({
            "tipo": "ifpe",
            "tipo_descripcion": "Instituciones de Fondos de Pago Electrónico (Art. 24 Ley Fintech)",
            "total": len(items),
            "itf": items,
            "url_consultado": URL_PADRON_CNBV,
            "fuente": "Snapshot junio 2026 — actualizar mensual",
        })

    def listar_ifc(self) -> dict[str, Any]:
        """Lista IFC (Instituciones de Financiamiento Colectivo / crowdfunding) autorizadas."""
        self._log("listar_ifc", {})
        items = ITF_AUTORIZADAS_SNAPSHOT["ifc"]
        return mark_simulated({
            "tipo": "ifc",
            "tipo_descripcion": "Instituciones de Financiamiento Colectivo (Art. 15 Ley Fintech)",
            "total": len(items),
            "itf": items,
            "url_consultado": URL_PADRON_CNBV,
            "fuente": "Snapshot junio 2026 — actualizar mensual",
        })

    def listar_modelos_novedosos(self) -> dict[str, Any]:
        """Sandbox regulatorio (Art. 80 Ley Fintech)."""
        self._log("listar_modelos_novedosos", {})
        return mark_simulated({
            "total": len(MODELOS_NOVEDOSOS_SNAPSHOT),
            "modelos": MODELOS_NOVEDOSOS_SNAPSHOT,
            "base_legal": "Art. 80 Ley Fintech — Modelos Novedosos",
            "url_consultado": URL_PADRON_CNBV,
        })

    def verificar_contraparte(
        self,
        rfc: str,
        tipo_operacion: Literal["fondos_pago", "crowdfunding", "cualquiera"] = "cualquiera",
    ) -> dict[str, Any]:
        """Tool compliance: ¿esta contraparte puede operar legalmente?

        Reglas:
        - fondos_pago: solo IFPE pueden operar (recibir y custodiar dinero electrónico)
        - crowdfunding: solo IFC pueden operar (intermediación financiamiento colectivo)
        - cualquiera: vale ambas
        """
        rfc_norm = rfc.upper().strip()
        if not RFC_REGEX.match(rfc_norm):
            raise ValidationError(f"RFC '{rfc}' inválido.")

        self._log("verificar_contraparte", {"rfc": rfc_norm, "tipo": tipo_operacion})

        consulta = self.consultar_itf(rfc=rfc_norm)
        if not consulta.get("encontrada"):
            return {
                "rfc": rfc_norm,
                "puede_operar": False,
                "razon": (
                    "RFC no aparece en padrón ITF autorizadas Ley Fintech. "
                    "Operar con esta entidad puede infringir Art. 5 Ley Fintech "
                    "(reservado solo a ITF autorizadas)."
                ),
                "tipo_operacion": tipo_operacion,
                "url_consultado": URL_PADRON_CNBV,
            }

        tipo_itf = consulta.get("tipo")
        compatible = (
            tipo_operacion == "cualquiera"
            or (tipo_operacion == "fondos_pago" and tipo_itf == "ifpe")
            or (tipo_operacion == "crowdfunding" and tipo_itf == "ifc")
        )

        return {
            "rfc": rfc_norm,
            "tipo_itf": tipo_itf,
            "tipo_operacion_solicitada": tipo_operacion,
            "puede_operar": compatible and consulta.get("estado") == "Autorizada",
            "estado_actual": consulta.get("estado"),
            "nombre": consulta.get("nombre"),
            "marca": consulta.get("marca"),
            "razon": (
                "ITF autorizada y compatible con el tipo de operación."
                if compatible else
                f"ITF tipo {tipo_itf}, pero la operación solicitada es {tipo_operacion}."
            ),
            "url_consultado": URL_PADRON_CNBV,
        }

    # ============================================================
    # Internos
    # ============================================================

    def _buscar_en_snapshot(
        self, rfc: Optional[str], nombre: Optional[str],
    ) -> dict[str, Any]:
        for tipo, items in ITF_AUTORIZADAS_SNAPSHOT.items():
            for item in items:
                if rfc and item["rfc"].upper() == rfc:
                    return mark_simulated({
                        "encontrada": True,
                        "tipo": tipo,
                        **item,
                        "puede_operar_legalmente": item["estado"] == "Autorizada",
                        "url_consultado": URL_PADRON_CNBV,
                    })
                if nombre and self._match_nombre(nombre, item["nombre"], item["marca"]):
                    return mark_simulated({
                        "encontrada": True,
                        "tipo": tipo,
                        **item,
                        "puede_operar_legalmente": item["estado"] == "Autorizada",
                        "url_consultado": URL_PADRON_CNBV,
                    })

        return mark_simulated({
            "encontrada": False,
            "tipo": None,
            "rfc": rfc,
            "nombre_buscado": nombre,
            "puede_operar_legalmente": False,
            "advertencia": "No es ITF autorizada Ley Fintech.",
            "url_consultado": URL_PADRON_CNBV,
        })

    @staticmethod
    def _match_nombre(buscado: str, nombre_oficial: str, marca: str) -> bool:
        b = buscado.lower().strip()
        return b in nombre_oficial.lower() or b in marca.lower() or marca.lower() in b

    def _consultar_real(self, rfc, nombre):
        raise McpError(
            "Path real CNBV requiere parser HTML del portal SharePoint. "
            "Padrón disponible en: " + URL_PADRON_CNBV,
            {"hint": "implementar scraping + parser tabla PES"},
        )
