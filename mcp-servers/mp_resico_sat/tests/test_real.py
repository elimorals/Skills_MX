"""RESICO: cálculos locales no son simulación; la devolución (escritura) sí."""

from mp_resico_sat.client import RESICOClient
from shared.bitacora import Bitacora


def test_calculos_no_simulados(tmp_path):
    c = RESICOClient(bitacora=Bitacora("resico_test", root=tmp_path))
    assert c.calcular_isr_mes(30_000)["simulated"] is False
    assert c.calcular_isr_mes(30_000)["isr_mxn"] == 330.0
    assert c.retencion_plataforma("uber", 1000)["simulated"] is False
    assert c.evaluar_estatus("AAAA010101AAA", 0, True, 100_000)["simulated"] is False
    assert c.solicitar_devolucion_mensual("AAAA010101AAA", "2026-01", 10)["simulated"] is True
