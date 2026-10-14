"""Prueba en vivo: Autenticación real contra el WS Descarga Masiva del SAT.

Solo lectura: obtiene un token (no crea solicitudes). Requiere la e.firma real
en SAT_EFIRMA_CERT / SAT_EFIRMA_KEY / SAT_EFIRMA_PASSWORD y PLUGINS_MX_LIVE=1.
No imprime el token.
"""
from __future__ import annotations

import pytest

from mp_sat_ws.client import Fiel, SatWsClient


@pytest.mark.live
def test_autenticacion_real(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    token = SatWsClient(fiel=Fiel.from_env())._token()
    assert len(token) > 100
