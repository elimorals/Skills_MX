"""Tests Sprint F: profundización SAT (calendario, prevalidar, histórico, devolución, buzón resumen)."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mp_sat_portal.client import SatPortalClient


class TestCalendarioFiscal:
    def setup_method(self):
        self.c = SatPortalClient()

    def test_resico_pf_genera_12_isr_12_iva_1_anual(self):
        r = self.c.calendario_fiscal_por_regimen("XAXX010101000", "626", 2026)
        assert r["total_declaraciones"] == 25
        conceptos = [d["concepto"] for d in r["declaraciones"]]
        assert conceptos.count("ISR_RESICO_PROV") == 12
        assert conceptos.count("IVA_MENSUAL") == 12
        assert conceptos.count("ISR_RESICO_ANUAL") == 1

    def test_pm_general_incluye_ieps(self):
        r = self.c.calendario_fiscal_por_regimen("ABC010101000", "601", 2026)
        conceptos = {d["concepto"] for d in r["declaraciones"]}
        assert "IEPS_MENSUAL" in conceptos
        assert "ISR_ANUAL_PM" in conceptos

    def test_asalariados_solo_anual(self):
        r = self.c.calendario_fiscal_por_regimen("XAXX010101000", "605", 2026)
        assert r["total_declaraciones"] == 1
        assert r["declaraciones"][0]["concepto"] == "ISR_ANUAL_PF"

    def test_regimen_desconocido_devuelve_error(self):
        r = self.c.calendario_fiscal_por_regimen("XAXX010101000", "999", 2026)
        assert r["error"] == "regimen_no_reconocido"
        assert len(r["regimenes_soportados"]) == 4

    def test_fechas_son_dia_17(self):
        r = self.c.calendario_fiscal_por_regimen("XAXX010101000", "626", 2026)
        mensuales = [d for d in r["declaraciones"] if "ANUAL" not in d["concepto"]]
        for d in mensuales:
            assert d["fecha_limite"].endswith("-17"), d


class TestCfdiPrevalidar:
    def setup_method(self):
        self.c = SatPortalClient()

    def test_xml_vacio_invalido(self):
        r = self.c.cfdi_prevalidar("", "INGRESO")
        assert r["valido"] is False
        assert r["errores"][0]["codigo"] == "CFDI40000"

    def test_falta_version_40(self):
        xml = '<cfdi:Comprobante Version="3.3"><cfdi:Emisor/><cfdi:Receptor RegimenFiscalReceptor="601" DomicilioFiscalReceptor="01000" UsoCFDI="G03"/><cfdi:Conceptos><cfdi:Concepto ObjetoImp="02"/></cfdi:Conceptos></cfdi:Comprobante>'
        r = self.c.cfdi_prevalidar(xml, "INGRESO")
        assert r["valido"] is False
        codigos = [e["codigo"] for e in r["errores"]]
        assert "CFDI40102" in codigos

    def test_cfdi40_minimo_valido(self):
        xml = (
            '<cfdi:Comprobante Version="4.0">'
            '<cfdi:Emisor Rfc="ABC010101AAA"/>'
            '<cfdi:Receptor Rfc="XAXX010101000" RegimenFiscalReceptor="616" DomicilioFiscalReceptor="01000" UsoCFDI="G03"/>'
            '<cfdi:Conceptos><cfdi:Concepto ObjetoImp="02"/></cfdi:Conceptos>'
            "</cfdi:Comprobante>"
        )
        r = self.c.cfdi_prevalidar(xml, "INGRESO")
        assert r["valido"] is True
        assert r["total_errores"] == 0

    def test_pago_requiere_complemento(self):
        xml = (
            '<cfdi:Comprobante Version="4.0">'
            '<cfdi:Emisor Rfc="ABC010101AAA"/>'
            '<cfdi:Receptor Rfc="XAXX010101000" RegimenFiscalReceptor="616" DomicilioFiscalReceptor="01000" UsoCFDI="CP01"/>'
            '<cfdi:Conceptos><cfdi:Concepto ObjetoImp="01"/></cfdi:Conceptos>'
            "</cfdi:Comprobante>"
        )
        r = self.c.cfdi_prevalidar(xml, "PAGO")
        codigos = [e["codigo"] for e in r["errores"]]
        assert "CFDI40201" in codigos

    def test_rfc_invalido_detectado(self):
        xml = (
            '<cfdi:Comprobante Version="4.0">'
            '<cfdi:Emisor Rfc="MALRFC"/>'
            '<cfdi:Receptor Rfc="XAXX010101000" RegimenFiscalReceptor="616" DomicilioFiscalReceptor="01000" UsoCFDI="G03"/>'
            '<cfdi:Conceptos><cfdi:Concepto ObjetoImp="02"/></cfdi:Conceptos>'
            "</cfdi:Comprobante>"
        )
        r = self.c.cfdi_prevalidar(xml, "INGRESO")
        codigos = [e["codigo"] for e in r["errores"]]
        assert "CFDI40110" in codigos


class TestDeclaracionesHistorico:
    def setup_method(self):
        self.c = SatPortalClient()

    def test_devuelve_12_periodos_y_simulated(self):
        r = self.c.declaraciones_historico("XAXX010101000", 2026)
        assert r["simulated"] is True
        assert r["total_declaraciones_periodo"] == 12

    def test_alerta_resico_3_omisiones_es_bool(self):
        r = self.c.declaraciones_historico("XAXX010101000", 2026)
        assert isinstance(r["alerta_resico_3_omisiones"], bool)

    def test_determinismo_por_rfc(self):
        r1 = self.c.declaraciones_historico("XAXX010101000", 2026)
        r2 = self.c.declaraciones_historico("XAXX010101000", 2026)
        assert r1["omitidas"] == r2["omitidas"]


class TestDevolucionEstatus:
    def setup_method(self):
        self.c = SatPortalClient()

    def test_fase_en_rango_valido(self):
        r = self.c.devolucion_estatus("FOLIO1234")
        assert r["fase_actual"] in {"RECIBIDA", "EN_REVISION", "INFO_ADICIONAL_REQUERIDA", "AUTORIZADA", "DEPOSITADA", "RECHAZADA"}
        assert "siguiente_paso" in r

    def test_plazo_legal_40_dias(self):
        r = self.c.devolucion_estatus("FOLIO9999")
        assert r["plazo_legal_max_dias_habiles"] == 40

    def test_monto_autorizado_solo_si_autorizada(self):
        r = self.c.devolucion_estatus("XYZ")
        if r["fase_actual"] in {"AUTORIZADA", "DEPOSITADA"}:
            assert r["monto_autorizado_mxn"] is not None
        else:
            assert r["monto_autorizado_mxn"] is None


class TestBuzonResumen:
    def setup_method(self):
        self.c = SatPortalClient()

    def test_resumen_tiene_metricas_clave(self):
        r = self.c.buzon_notificaciones_resumen("XAXX010101000")
        assert "total_urgentes_5d" in r
        assert "total_vencidas" in r
        assert "requiere_atencion_inmediata" in r
        assert r["fuente_legal"].startswith("Art. 17-K")

    def test_solo_pendientes_filtra_leidos(self):
        r = self.c.buzon_notificaciones_resumen("XAXX010101000", solo_pendientes=True)
        for n in r["notificaciones"]:
            assert n["leido"] is False
