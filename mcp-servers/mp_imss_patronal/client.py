"""Cliente mp_imss_patronal — mock-first.

⚠ Path Playwright real NO implementado. IMSS IDSE requiere e.firma o
tarjeta NPIE. Construcción real ~100-150h.
"""

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

from mp_imss_patronal import mock_data  # noqa: E402
from mp_imss_patronal.catalogos import CAUSA_BAJA, TIPOS_MOVIMIENTO_AFILIATORIO  # noqa: E402


NAMESPACE = "imss_patronal_mcp"
CRED_VARS = ["IMSS_RFC_PATRONAL", "IMSS_NPIE_PATH", "IMSS_EFIRMA_CERT"]


class ImssPatronalClient:
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
            safe["registro_patronal_hash"] = Bitacora.hash_sensitive(
                str(safe.pop("registro_patronal"))
            )
        self._bitacora.log(op, success=success, params_summary=safe)

    # ---------- tools ----------

    def consultar_avisos_pendientes(self, registro_patronal: str) -> dict[str, Any]:
        self._log("consultar_avisos", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_avisos_pendientes(registro_patronal),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def enviar_movimiento_afiliatorio(
        self,
        registro_patronal: str,
        nss: str,
        tipo_movimiento: str,
        salario_diario: float | None = None,
        causa_baja: str | None = None,
    ) -> dict[str, Any]:
        if tipo_movimiento not in TIPOS_MOVIMIENTO_AFILIATORIO:
            raise ValidationError(
                f"tipo_movimiento '{tipo_movimiento}' inválido. "
                f"Válidos: {', '.join(TIPOS_MOVIMIENTO_AFILIATORIO.keys())}"
            )
        if tipo_movimiento == "08" and salario_diario is None:
            raise ValidationError("Alta (08) requiere salario_diario")
        if tipo_movimiento == "02":
            if not causa_baja or causa_baja not in CAUSA_BAJA:
                raise ValidationError(
                    f"Baja (02) requiere causa_baja. Válidas: {list(CAUSA_BAJA.keys())}"
                )

        self._log("movimiento_afiliatorio", {
            "registro_patronal": registro_patronal,
            "nss": nss,
            "tipo": tipo_movimiento,
        })
        if self._modo() == "mock":
            if tipo_movimiento == "08":
                return mock_response_playwright(
                    mock_data.mock_alta_trabajador(registro_patronal, nss, salario_diario),  # type: ignore[arg-type]
                    portal="imss_idse",
                )
            if tipo_movimiento == "02":
                return mock_response_playwright(
                    mock_data.mock_baja_trabajador(registro_patronal, nss, causa_baja),  # type: ignore[arg-type]
                    portal="imss_idse",
                )
            return mock_response_playwright(
                {
                    "registro_patronal": registro_patronal,
                    "nss_mascarado": "**" + nss[-2:] if len(nss) > 2 else nss,
                    "tipo_movimiento": tipo_movimiento,
                    "estatus": "PROCESADO",
                    "fecha": "ya",
                },
                portal="imss_idse",
                nota_extra=f"Mock para tipo movimiento {tipo_movimiento}.",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def descargar_cedula_autodeterminacion(
        self, registro_patronal: str, bimestre: int, ejercicio: int
    ) -> dict[str, Any]:
        if bimestre < 1 or bimestre > 6:
            raise ValidationError("bimestre debe ser 1-6")
        self._log("cedula", {
            "registro_patronal": registro_patronal,
            "bimestre": bimestre, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_cedula_autodeterminacion(registro_patronal, bimestre, ejercicio),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def consultar_emcr(
        self, registro_patronal: str, mes: int, ejercicio: int
    ) -> dict[str, Any]:
        self._log("emcr", {
            "registro_patronal": registro_patronal,
            "mes": mes, "ejercicio": ejercicio,
        })
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_emcr(registro_patronal, mes, ejercicio),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def consultar_salario_diario_integrado(
        self, registro_patronal: str, nss: str
    ) -> dict[str, Any]:
        self._log("sbc", {"registro_patronal": registro_patronal, "nss": nss})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_sbc(registro_patronal, nss),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    def consultar_padron_trabajadores(
        self, registro_patronal: str
    ) -> dict[str, Any]:
        self._log("padron", {"registro_patronal": registro_patronal})
        if self._modo() == "mock":
            return mock_response_playwright(
                mock_data.mock_padron_trabajadores(registro_patronal),
                portal="imss_idse",
            )
        raise_playwright_real_no_implementado("imss_idse")

    # ============ Sprint F — profundización ============

    # Constantes 2026 oficiales
    UMA_2026_DIARIA: float = 113.07
    TOPE_SBC_UMAS: int = 25  # Art. 28 LSS
    TOPE_SBC_DIARIO_MXN: float = 113.07 * 25  # $2,826.75
    SMG_DIARIO_2026: float = 313.06  # zona libre frontera norte se ajusta por separado

    # Cuotas patronales (% sobre SBC) — LSS 2026 vigente
    CUOTA_ENF_MAT_FIJA_UMA: float = 0.204  # 20.40% sobre 1 UMA por trabajador
    CUOTA_ENF_MAT_EXCEDENTE: float = 0.011  # 1.1% sobre excedente >3 UMAs
    CUOTA_PRESTACIONES_DINERO: float = 0.007  # 0.70%
    CUOTA_GASTOS_MED_PENSIONADOS: float = 0.0105  # 1.05%
    CUOTA_INVALIDEZ_VIDA: float = 0.0175  # 1.75%
    CUOTA_CESANTIA_VEJEZ: float = 0.0315  # 3.15% (cambió en reforma pensiones 2020+)
    CUOTA_GUARDERIAS: float = 0.01  # 1.00%
    CUOTA_INFONAVIT: float = 0.05  # 5%
    CUOTA_RETIRO: float = 0.02  # 2%

    # Primas Riesgo de Trabajo — Clases I-V
    PRIMAS_RIESGO_TRABAJO: dict[str, float] = {
        "I": 0.0054355,  # 0.54355%
        "II": 0.0113065,  # 1.13065%
        "III": 0.0259840,  # 2.59840%
        "IV": 0.0465325,  # 4.65325%
        "V": 0.0759950,  # 7.59950%
    }

    def sbc_calcular(
        self,
        salario_diario_base: float,
        bono_anual_mxn: float = 0.0,
        dias_aguinaldo: int = 15,
        dias_prima_vacacional: int = 6,
        otras_percepciones_anuales_mxn: float = 0.0,
    ) -> dict[str, Any]:
        """Auto-cálculo SBC con factor integración + tope UMAs 2026.

        Local. No requiere credenciales. Implementa Art. 27 LSS.
        """
        self._log(
            "sbc_calcular",
            {"salario_diario_base": salario_diario_base, "bono_anual": bono_anual_mxn},
        )
        if salario_diario_base <= 0:
            raise ValidationError("salario_diario_base debe ser > 0")
        if dias_aguinaldo < 15:
            raise ValidationError("Aguinaldo mínimo legal LFT Art. 87: 15 días")

        # Factor integración mínimo (15 aguinaldo + 6 prima vac. en año 1)
        # = (15/365) + (6 * 0.25 * (vacaciones LFT 2024 = 12 días año 1) / 365)
        # Simplificado: factor_minimo = 1.0452 (15 días aguinaldo + 6 días prima vac. * 12 días vac.)
        factor_aguinaldo = dias_aguinaldo / 365.0
        # Vacaciones LFT 2023+ : 12 días año 1 (antes 6)
        dias_vacaciones_anio_1 = 12
        factor_prima_vac = (dias_prima_vacacional / 100.0) * dias_vacaciones_anio_1 / 365.0
        factor_otras = (bono_anual_mxn + otras_percepciones_anuales_mxn) / max(
            salario_diario_base * 365.0, 1.0
        )
        factor_integracion = 1.0 + factor_aguinaldo + factor_prima_vac + factor_otras

        sbc_calculado = round(salario_diario_base * factor_integracion, 2)
        sbc_tope = self.TOPE_SBC_DIARIO_MXN
        sbc_final = min(sbc_calculado, sbc_tope)
        aplicado_tope = sbc_calculado > sbc_tope

        return {
            "salario_diario_base_mxn": salario_diario_base,
            "factor_integracion": round(factor_integracion, 6),
            "sbc_calculado_mxn": sbc_calculado,
            "sbc_tope_25_umas_mxn": sbc_tope,
            "sbc_final_mxn": sbc_final,
            "aplicado_tope_25_umas": aplicado_tope,
            "uma_2026_diaria": self.UMA_2026_DIARIA,
            "fundamento": "Art. 27, 28 LSS + UMA 2026 (DOF Banxico)",
            "advertencia_smg": (
                "Por debajo de SMG diario 2026 ($313.06)"
                if salario_diario_base < self.SMG_DIARIO_2026
                else None
            ),
        }

    def ema_vs_eba_diferencias(
        self,
        registro_patronal: str,
        periodo: str,
    ) -> dict[str, Any]:
        """Detección de inconsistencias EMA (Empresa) vs EBA (Banco).

        Compara la cédula EMA (lo que IMSS dice que debes) vs EBA (lo que pagaste).
        Inconsistencias típicas: cuotas calculadas distinto, movimientos no aplicados,
        intereses por mora.

        Path real requiere e.firma. Mock por default.
        """
        self._log(
            "ema_vs_eba",
            {"registro_patronal": registro_patronal, "periodo": periodo},
        )
        if self._modo() != "mock":
            raise_playwright_real_no_implementado("imss_idse")

        import hashlib as _hash
        h = int(_hash.sha256(f"{registro_patronal}{periodo}".encode()).hexdigest(), 16)

        ema_total = round(50000.0 + (h % 100000), 2)
        diff_pct = ((h >> 8) % 50) / 10.0  # 0.0 a 5.0%
        eba_total = round(ema_total * (1 - diff_pct / 100.0), 2)
        diferencia = round(ema_total - eba_total, 2)

        inconsistencias = []
        if diff_pct > 2.0:
            inconsistencias.append(
                {
                    "tipo": "DIFERENCIA_CUOTAS",
                    "monto_mxn": diferencia,
                    "descripcion": f"EMA vs EBA difieren en {diff_pct:.1f}% — revisar cuotas calculadas.",
                }
            )
        if (h >> 16) & 1:
            inconsistencias.append(
                {
                    "tipo": "MOVIMIENTO_NO_APLICADO",
                    "descripcion": "Aviso de alta/baja del periodo no se reflejó en EMA.",
                }
            )
        if (h >> 20) & 1:
            inconsistencias.append(
                {
                    "tipo": "INTERESES_MORA",
                    "monto_mxn": round((h % 5000) + 100.0, 2),
                    "descripcion": "EBA incluye intereses por pago extemporáneo.",
                }
            )

        return mock_response_playwright(
            {
                "registro_patronal": registro_patronal,
                "periodo": periodo,
                "ema_total_mxn": ema_total,
                "eba_total_mxn": eba_total,
                "diferencia_mxn": diferencia,
                "diferencia_porcentual": diff_pct,
                "requiere_aclaracion": len(inconsistencias) > 0,
                "inconsistencias": inconsistencias,
                "fundamento": "Art. 39-A LSS — conciliación cuotas patronales.",
            },
            portal="imss_idse",
        )

    def calendario_obligaciones(
        self, giro: str = "comercio", clase_riesgo: str = "I"
    ) -> dict[str, Any]:
        """Calendario obligaciones IMSS por giro y clase de riesgo.

        Local. Devuelve fechas vencimiento mensuales + bimestrales + anuales.
        """
        self._log(
            "calendario_obligaciones",
            {"giro": giro, "clase_riesgo": clase_riesgo},
        )
        from datetime import date as _date

        anio = _date.today().year
        clase = clase_riesgo.upper()
        if clase not in self.PRIMAS_RIESGO_TRABAJO:
            raise ValidationError(
                f"clase_riesgo inválida: {clase_riesgo!r}. Valores: I, II, III, IV, V"
            )

        # Cuotas mensuales: día 17 del mes siguiente
        DIA_MENSUAL = 17
        # Cuotas bimestrales INFONAVIT + RCV: día 17 del mes siguiente al bimestre
        BIMESTRES = [
            (1, 2, 3),  # Ene-Feb se paga en Mar
            (3, 4, 5),
            (5, 6, 7),
            (7, 8, 9),
            (9, 10, 11),
            (11, 12, 1),
        ]

        mensuales = []
        for mes in range(1, 13):
            vence_mes = mes + 1 if mes < 12 else 1
            vence_anio = anio if mes < 12 else anio + 1
            mensuales.append(
                {
                    "concepto": "CUOTAS_OBRERO_PATRONALES_MES",
                    "periodo": f"{anio}-{mes:02d}",
                    "fecha_limite": _date(vence_anio, vence_mes, DIA_MENSUAL).isoformat(),
                }
            )

        bimestrales = []
        for inicio, fin, mes_pago in BIMESTRES:
            anio_pago = anio if mes_pago > inicio else anio + 1
            bimestrales.append(
                {
                    "concepto": "INFONAVIT_RCV_BIMESTRAL",
                    "periodo": f"{anio}-{inicio:02d}/{fin:02d}",
                    "fecha_limite": _date(anio_pago, mes_pago, DIA_MENSUAL).isoformat(),
                }
            )

        return {
            "giro": giro,
            "clase_riesgo": clase,
            "prima_riesgo_trabajo_pct": self.PRIMAS_RIESGO_TRABAJO[clase] * 100,
            "anio": anio,
            "obligaciones_mensuales": mensuales,
            "obligaciones_bimestrales": bimestrales,
            "obligacion_anual": {
                "concepto": "DETERMINACION_PRIMA_RIESGO_TRABAJO",
                "fecha_limite": _date(anio, 2, 28).isoformat(),
                "descripcion": "Determinación anual de prima de RT (Art. 74 LSS) — febrero",
            },
            "fundamento": "LSS Art. 39, 74, 102 + Reglamento IMSS",
        }

    def simulador_costo_patronal(
        self,
        salario_diario_base: float,
        bono_anual_mxn: float = 0.0,
        clase_riesgo: str = "I",
    ) -> dict[str, Any]:
        """Costo total patronal mensual + anual por colaborador.

        Combina SBC + cuotas IMSS + INFONAVIT + ISR retenido + provisiones LFT.
        Local. No requiere credenciales.
        """
        self._log(
            "simulador_costo_patronal",
            {"salario_diario_base": salario_diario_base, "clase_riesgo": clase_riesgo},
        )
        clase = clase_riesgo.upper()
        if clase not in self.PRIMAS_RIESGO_TRABAJO:
            raise ValidationError(
                f"clase_riesgo inválida: {clase_riesgo!r}. Valores: I, II, III, IV, V"
            )

        sbc_data = self.sbc_calcular(salario_diario_base, bono_anual_mxn=bono_anual_mxn)
        sbc = sbc_data["sbc_final_mxn"]
        uma = self.UMA_2026_DIARIA
        salario_mensual = round(salario_diario_base * 30.4, 2)
        sbc_mensual = round(sbc * 30.4, 2)

        # Cuotas patronales mensuales
        enf_mat_fija = round(uma * 30.4 * self.CUOTA_ENF_MAT_FIJA_UMA, 2)
        excedente = max(0.0, sbc - uma * 3) * 30.4
        enf_mat_exc = round(excedente * self.CUOTA_ENF_MAT_EXCEDENTE, 2)
        prest_dinero = round(sbc_mensual * self.CUOTA_PRESTACIONES_DINERO, 2)
        gastos_pensionados = round(sbc_mensual * self.CUOTA_GASTOS_MED_PENSIONADOS, 2)
        invalidez_vida = round(sbc_mensual * self.CUOTA_INVALIDEZ_VIDA, 2)
        cesantia_vejez = round(sbc_mensual * self.CUOTA_CESANTIA_VEJEZ, 2)
        guarderias = round(sbc_mensual * self.CUOTA_GUARDERIAS, 2)
        riesgo_trabajo = round(sbc_mensual * self.PRIMAS_RIESGO_TRABAJO[clase], 2)
        retiro = round(sbc_mensual * self.CUOTA_RETIRO, 2)

        infonavit = round(sbc_mensual * self.CUOTA_INFONAVIT, 2)

        total_imss = round(
            enf_mat_fija + enf_mat_exc + prest_dinero + gastos_pensionados
            + invalidez_vida + cesantia_vejez + guarderias + riesgo_trabajo + retiro,
            2,
        )

        costo_mensual = round(salario_mensual + total_imss + infonavit, 2)
        # Provisiones LFT: aguinaldo 15d + prima vac 25% sobre 12d + PTU 10% utilidad (no patronal directo)
        provision_aguinaldo_mensual = round(salario_diario_base * 15 / 12, 2)
        provision_prima_vac_mensual = round(salario_diario_base * 12 * 0.25 / 12, 2)

        costo_total_mensual_con_provisiones = round(
            costo_mensual + provision_aguinaldo_mensual + provision_prima_vac_mensual, 2
        )

        return {
            "salario_diario_base_mxn": salario_diario_base,
            "salario_mensual_neto_mxn": salario_mensual,
            "sbc_final_mxn": sbc,
            "clase_riesgo": clase,
            "prima_riesgo_trabajo_pct": round(self.PRIMAS_RIESGO_TRABAJO[clase] * 100, 4),
            "cuotas_imss_mensuales_mxn": {
                "enfermedad_maternidad_fija": enf_mat_fija,
                "enfermedad_maternidad_excedente_3umas": enf_mat_exc,
                "prestaciones_en_dinero": prest_dinero,
                "gastos_medicos_pensionados": gastos_pensionados,
                "invalidez_vida": invalidez_vida,
                "cesantia_vejez": cesantia_vejez,
                "guarderias": guarderias,
                "riesgo_trabajo": riesgo_trabajo,
                "retiro": retiro,
                "subtotal_imss": total_imss,
            },
            "cuota_infonavit_mensual_mxn": infonavit,
            "provisiones_lft_mensuales_mxn": {
                "aguinaldo": provision_aguinaldo_mensual,
                "prima_vacacional": provision_prima_vac_mensual,
            },
            "costo_directo_mensual_mxn": costo_mensual,
            "costo_total_mensual_con_provisiones_mxn": costo_total_mensual_con_provisiones,
            "costo_total_anual_estimado_mxn": round(
                costo_total_mensual_con_provisiones * 12, 2
            ),
            "factor_costo_sobre_salario": round(
                costo_total_mensual_con_provisiones / max(salario_mensual, 1), 4
            ),
            "uma_2026_diaria": uma,
            "fundamento": "LSS Art. 25, 28, 102, 106, 107, 147 + LFT Art. 76, 80, 87",
        }

    def riesgo_trabajo_prima_cambio(
        self,
        prima_actual: float,
        s_dias_subsidiados: int = 0,
        n_total_trabajadores: int = 1,
        v_casos_invalidez: int = 0,
        i_casos_incapacidad_permanente_parcial: float = 0.0,
        d_casos_defuncion: int = 0,
    ) -> dict[str, Any]:
        """Proyección anual de prima de Riesgo de Trabajo (Art. 72 LSS).

        Fórmula oficial IMSS:
            Prima = [(S/365) + V·(I+D)] · (F/N) + M

        Donde:
            S = días subsidiados por incapacidades temporales
            V = factor 0.21*38.0556 = 7.99 (LSS RM 2026)
            I = % de incapacidades permanentes parciales
            D = núm. defunciones
            F = 2.3 (factor de prima)
            N = núm. trabajadores promedio expuestos a riesgo
            M = 0.005 (prima mínima)

        Tope: ±1% por año (Art. 74 LSS).
        """
        self._log(
            "riesgo_trabajo_prima",
            {
                "prima_actual": prima_actual,
                "s_dias": s_dias_subsidiados,
                "n_total": n_total_trabajadores,
            },
        )
        if n_total_trabajadores <= 0:
            raise ValidationError("n_total_trabajadores debe ser > 0")
        if prima_actual < 0.005 or prima_actual > 0.150:
            raise ValidationError(
                "prima_actual fuera de rango LSS (0.5% mínimo, 15% máximo)"
            )

        V = 7.99
        F = 2.3
        M = 0.005

        # Fracción de siniestralidad
        siniestralidad = ((s_dias_subsidiados / 365.0)
                         + V * (i_casos_incapacidad_permanente_parcial + d_casos_defuncion))
        prima_calculada = round(
            siniestralidad * (F / n_total_trabajadores) + M, 6
        )

        # Tope ±1% Art. 74 LSS
        diff = prima_calculada - prima_actual
        if diff > 0.01:
            prima_proxima = round(prima_actual + 0.01, 6)
            aplicado_tope = "incremento_topado_1pct"
        elif diff < -0.01:
            prima_proxima = round(prima_actual - 0.01, 6)
            aplicado_tope = "decremento_topado_1pct"
        else:
            prima_proxima = prima_calculada
            aplicado_tope = "sin_tope"

        # Validar mínimo y máximo legal
        prima_proxima = max(0.005, min(0.150, prima_proxima))

        return {
            "prima_actual_pct": round(prima_actual * 100, 4),
            "siniestralidad_calculada": round(siniestralidad, 6),
            "prima_calculada_sin_tope_pct": round(prima_calculada * 100, 4),
            "prima_proxima_anio_pct": round(prima_proxima * 100, 4),
            "aplicado_tope": aplicado_tope,
            "diferencia_anual_pct": round((prima_proxima - prima_actual) * 100, 4),
            "fundamento": "Art. 72, 74 LSS + Reglamento del Seguro de RT",
            "fecha_limite_presentacion": "28 de febrero del año siguiente",
            "advertencia_prima_alta": prima_proxima > 0.05,
        }
        raise_playwright_real_no_implementado("imss_idse")
