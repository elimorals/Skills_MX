"""Cliente mp_infonavit_patronal — mock-first."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, ValidationError  # noqa: E402
from shared.playwright_stub import (  # noqa: E402
    detectar_modo_playwright,
    mock_response_playwright,
    raise_playwright_real_no_implementado,
)

from mp_infonavit_patronal import mock_data  # noqa: E402


NAMESPACE = "infonavit_patronal_mcp"
CRED_VARS = ["INFONAVIT_RFC_PATRONAL", "INFONAVIT_USUARIO", "INFONAVIT_PASSWORD"]


class InfonavitPatronalClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _modo(self) -> str:
        return detectar_modo_playwright(CRED_VARS)

    def _log(self, op: str, params: dict[str, Any], *, success: bool = True) -> None:
        safe = dict(params)
        if "nss" in safe and safe["nss"]:
            safe["nss_hash"] = Bitacora.hash_sensitive(str(safe.pop("nss")))
        if "registro_patronal" in safe:
            safe["rp_hash"] = Bitacora.hash_sensitive(str(safe.pop("registro_patronal")))
        self._bitacora.log(op, success=success, params_summary=safe)

    def consultar_creditos_trabajadores(self, registro_patronal: str) -> dict[str, Any]:
        self._log("creditos_trabajadores", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_creditos_trabajadores(registro_patronal),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    def descargar_emis(
        self, registro_patronal: str, mes: int, ejercicio: int
    ) -> dict[str, Any]:
        if mes < 1 or mes > 12:
            raise ValidationError("mes debe ser 1-12")
        self._log("emis", {
            "registro_patronal": registro_patronal,
            "mes": mes, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_emis(registro_patronal, mes, ejercicio),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    def consultar_descuentos_mensuales(
        self, registro_patronal: str, nss: str, mes: int, ejercicio: int
    ) -> dict[str, Any]:
        self._log("descuentos_mensuales", {
            "registro_patronal": registro_patronal,
            "nss": nss, "mes": mes, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_descuentos_mensuales(registro_patronal, nss, mes, ejercicio),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    def consultar_avisos_pendientes(self, registro_patronal: str) -> dict[str, Any]:
        self._log("avisos", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_avisos_pendientes(registro_patronal),
                portal="infonavit_empresarial",
            )
        raise_playwright_real_no_implementado("infonavit_empresarial")

    # ============ Sprint F — profundización ============

    # Catálogo factores descuento INFONAVIT (Régimen LFINFONAVIT Art. 29)
    FACTORES_DESCUENTO: dict[str, dict[str, Any]] = {
        "PESOS_NORMAL": {
            "descripcion": "Crédito tradicional en pesos — descuento porcentual SBC",
            "factor_min": 0.05,
            "factor_max": 0.30,
            "default": 0.20,
        },
        "VSM_NORMAL": {
            "descripcion": "Crédito tradicional VSM — descuento en factor VSM",
            "factor_min": 0.05,
            "factor_max": 0.30,
            "default": 0.20,
        },
        "CUOTA_FIJA_PESOS": {
            "descripcion": "Crédito en pesos con cuota fija — descuento monto fijo mensual",
            "factor_min": None,
            "factor_max": None,
            "default": 3500.0,
        },
        "REESTRUCTURADO_VSM": {
            "descripcion": "Crédito reestructurado VSM — descuento reducido",
            "factor_min": 0.03,
            "factor_max": 0.15,
            "default": 0.10,
        },
        "OMISIONES_PASIVAS": {
            "descripcion": "Pago de adeudos por omisiones (no aplica a SBC corriente)",
            "factor_min": 0.0,
            "factor_max": 0.20,
            "default": 0.15,
        },
    }

    def descuento_calcular(
        self,
        sbc_diario_mxn: float,
        credito_tipo: str,
        factor_o_monto: float | None = None,
        dias_mes: int = 30,
    ) -> dict[str, Any]:
        """Auto-cálculo del descuento INFONAVIT mensual por trabajador.

        Local. Implementa Art. 29 LFINFONAVIT + reglas RCV.
        - PESOS_NORMAL / VSM_NORMAL: descuento = SBC * 30 * factor (%)
        - CUOTA_FIJA_PESOS: descuento = monto fijo mensual MXN
        - REESTRUCTURADO_VSM: descuento reducido sobre SBC * 30 * factor
        - OMISIONES_PASIVAS: descuento adicional para regularización
        """
        self._log(
            "descuento_calcular",
            {
                "sbc_diario_mxn": sbc_diario_mxn,
                "credito_tipo": credito_tipo,
                "factor_o_monto": factor_o_monto,
            },
        )
        if sbc_diario_mxn <= 0:
            raise ValidationError("sbc_diario_mxn debe ser > 0")
        tipo = (credito_tipo or "").strip().upper()
        if tipo not in self.FACTORES_DESCUENTO:
            raise ValidationError(
                f"credito_tipo inválido: {credito_tipo!r}. Tipos: {list(self.FACTORES_DESCUENTO.keys())}"
            )

        info = self.FACTORES_DESCUENTO[tipo]
        sbc_mensual = round(sbc_diario_mxn * dias_mes, 2)

        if tipo == "CUOTA_FIJA_PESOS":
            descuento = factor_o_monto if factor_o_monto is not None else info["default"]
            if descuento < 0:
                raise ValidationError("monto cuota fija debe ser ≥ 0")
            descuento_mensual = round(descuento, 2)
            factor_aplicado = None
        else:
            factor = factor_o_monto if factor_o_monto is not None else info["default"]
            if info["factor_min"] is not None and factor < info["factor_min"]:
                raise ValidationError(
                    f"factor < min permitido ({info['factor_min']}) para tipo {tipo}"
                )
            if info["factor_max"] is not None and factor > info["factor_max"]:
                raise ValidationError(
                    f"factor > max permitido ({info['factor_max']}) para tipo {tipo}"
                )
            descuento_mensual = round(sbc_mensual * factor, 2)
            factor_aplicado = factor

        # Cap legal: no más de 30% del SBC mensual (Art. 110 LFT)
        cap_legal = round(sbc_mensual * 0.30, 2)
        aplicado_cap = descuento_mensual > cap_legal
        descuento_final = min(descuento_mensual, cap_legal)

        return {
            "sbc_diario_mxn": sbc_diario_mxn,
            "sbc_mensual_mxn": sbc_mensual,
            "credito_tipo": tipo,
            "credito_tipo_descripcion": info["descripcion"],
            "factor_aplicado": factor_aplicado,
            "descuento_calculado_mxn": descuento_mensual,
            "cap_legal_30pct_sbc_mxn": cap_legal,
            "aplicado_cap_lft_art110": aplicado_cap,
            "descuento_final_mensual_mxn": descuento_final,
            "descuento_anual_mxn": round(descuento_final * 12, 2),
            "fundamento": "Art. 29, 35 LFINFONAVIT + Art. 110 LFT",
        }

    def creditos_sin_reporte(
        self, registro_patronal: str
    ) -> dict[str, Any]:
        """Detección de créditos INFONAVIT NO aplicados en nómina.

        Compara lista de créditos activos (portal Empresarial) vs descuentos
        reportados al INFONAVIT. Detecta omisiones que generan intereses moratorios
        para el patrón.

        Path real requiere usuario+password Empresarial. Mock por default.
        """
        self._log(
            "creditos_sin_reporte",
            {"registro_patronal": registro_patronal},
        )
        if self._modo() != "mock":
            raise_playwright_real_no_implementado("infonavit_empresarial")

        import hashlib as _hash
        h = int(_hash.sha256(registro_patronal.encode()).hexdigest(), 16)

        n_creditos = (h % 6)  # 0 a 5 créditos sin reporte
        omisiones = []
        for i in range(n_creditos):
            meses_omiso = ((h >> (i + 1)) % 6) + 1
            descuento = round(2000.0 + ((h >> (i + 5)) % 5000), 2)
            intereses_estimados = round(descuento * meses_omiso * 0.018, 2)  # ~1.8% mes mora
            omisiones.append(
                {
                    "nss_hash": Bitacora.hash_sensitive(f"{registro_patronal}-{i}-NSS"),
                    "numero_credito": f"INFO{(h + i) % 10000000:07d}",
                    "tipo_credito": ["PESOS_NORMAL", "VSM_NORMAL", "CUOTA_FIJA_PESOS"][i % 3],
                    "meses_omiso": meses_omiso,
                    "descuento_esperado_mensual_mxn": descuento,
                    "intereses_moratorios_estimados_mxn": intereses_estimados,
                }
            )

        total_descuentos_omisos = round(
            sum(o["descuento_esperado_mensual_mxn"] for o in omisiones), 2
        )
        total_intereses = round(sum(o["intereses_moratorios_estimados_mxn"] for o in omisiones), 2)

        return mock_response_playwright(
            {
                "registro_patronal_hash": Bitacora.hash_sensitive(registro_patronal),
                "total_creditos_sin_reporte": n_creditos,
                "total_descuentos_omisos_mensuales_mxn": total_descuentos_omisos,
                "total_intereses_moratorios_estimados_mxn": total_intereses,
                "omisiones": omisiones,
                "requiere_regularizacion": n_creditos > 0,
                "fundamento": "Art. 29 LFINFONAVIT + Art. 30 LSS (responsabilidad patronal).",
            },
            portal="infonavit_empresarial",
        )

    def emis_historico(
        self, registro_patronal: str, anios: int = 3
    ) -> dict[str, Any]:
        """Histórico EMIS (Estados de Cuenta Individuales del Patrón) por años.

        Útil para auditorías, defensas en juicio laboral, due diligence.
        Path real requiere credenciales Empresarial.
        """
        self._log(
            "emis_historico",
            {"registro_patronal": registro_patronal, "anios": anios},
        )
        if anios < 1 or anios > 10:
            raise ValidationError("anios debe estar entre 1 y 10")
        if self._modo() != "mock":
            raise_playwright_real_no_implementado("infonavit_empresarial")

        import hashlib as _hash
        from datetime import date as _date

        h = int(_hash.sha256(registro_patronal.encode()).hexdigest(), 16)
        anio_actual = _date.today().year
        bimestres_por_anio = 6

        registros = []
        for anio in range(anio_actual - anios + 1, anio_actual + 1):
            for bim in range(1, bimestres_por_anio + 1):
                pagado = bool((h >> bim) & 1 or bim <= 4)
                cuota = round(8000.0 + ((h + anio + bim) % 12000), 2)
                registros.append(
                    {
                        "anio": anio,
                        "bimestre": bim,
                        "periodo": f"{anio}-B{bim}",
                        "cuota_calculada_mxn": cuota,
                        "cuota_pagada_mxn": cuota if pagado else 0.0,
                        "status": "PAGADO" if pagado else "OMISO",
                        "fecha_pago": (
                            _date(anio, bim * 2, 17).isoformat() if pagado else None
                        ),
                    }
                )

        omisos = [r for r in registros if r["status"] == "OMISO"]
        return mock_response_playwright(
            {
                "registro_patronal_hash": Bitacora.hash_sensitive(registro_patronal),
                "anios_consultados": anios,
                "total_registros": len(registros),
                "registros_pagados": len(registros) - len(omisos),
                "registros_omisos": len(omisos),
                "monto_total_pagado_mxn": round(
                    sum(r["cuota_pagada_mxn"] for r in registros), 2
                ),
                "monto_total_omiso_mxn": round(
                    sum(r["cuota_calculada_mxn"] for r in omisos), 2
                ),
                "registros": registros,
            },
            portal="infonavit_empresarial",
        )

    def conciliacion_nomina(
        self,
        registro_patronal: str,
        descuentos_nomina: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Conciliación cruzada: descuentos en nómina vs cuotas reportadas a INFONAVIT.

        `descuentos_nomina` formato: [{"nss": str, "monto_mxn": float, "periodo": "YYYY-MM"}].
        Devuelve discrepancias agrupadas por trabajador.

        Local en parte (verificación de inputs) + mock para datos INFONAVIT cuando no hay credenciales.
        """
        self._log(
            "conciliacion_nomina",
            {
                "registro_patronal": registro_patronal,
                "total_registros_nomina": len(descuentos_nomina or []),
            },
        )
        if not descuentos_nomina:
            raise ValidationError("descuentos_nomina vacío — sin datos para conciliar")
        if len(descuentos_nomina) > 5000:
            raise ValidationError("Máximo 5000 registros por llamada")

        import hashlib as _hash

        # Simula lo que el INFONAVIT espera (path real consulta portal)
        h = int(_hash.sha256(registro_patronal.encode()).hexdigest(), 16)
        diferencias = []
        coincidencias = 0
        for i, d in enumerate(descuentos_nomina):
            nss = str(d.get("nss", "")).strip()
            monto_nomina = float(d.get("monto_mxn", 0.0))
            periodo = d.get("periodo", "")
            if not nss or len(nss) < 10:
                diferencias.append(
                    {
                        "indice": i,
                        "tipo": "NSS_INVALIDO",
                        "nss_hash": Bitacora.hash_sensitive(nss),
                        "descripcion": "NSS con menos de 10 dígitos.",
                    }
                )
                continue
            # Simulación: INFONAVIT espera el monto +/- algo según hash
            esperado = round(monto_nomina * (1.0 + (((h + i) % 21 - 10) / 100.0)), 2)
            diff = round(monto_nomina - esperado, 2)
            if abs(diff) < 1.0:
                coincidencias += 1
            else:
                diferencias.append(
                    {
                        "indice": i,
                        "tipo": "MONTO_DIFIERE",
                        "nss_hash": Bitacora.hash_sensitive(nss),
                        "periodo": periodo,
                        "monto_nomina_mxn": monto_nomina,
                        "monto_esperado_infonavit_mxn": esperado,
                        "diferencia_mxn": diff,
                        "accion_recomendada": (
                            "Ajustar nómina al alza" if diff < 0 else "Aclarar con INFONAVIT"
                        ),
                    }
                )

        return mock_response_playwright(
            {
                "registro_patronal_hash": Bitacora.hash_sensitive(registro_patronal),
                "total_registros_nomina": len(descuentos_nomina),
                "coincidencias_exactas": coincidencias,
                "diferencias_detectadas": len(diferencias),
                "diferencias": diferencias,
                "porcentaje_match": round(
                    coincidencias / max(len(descuentos_nomina), 1) * 100, 2
                ),
                "fundamento": "Art. 29 LFINFONAVIT — obligación patronal exactitud descuentos.",
            },
            portal="infonavit_empresarial",
        )
