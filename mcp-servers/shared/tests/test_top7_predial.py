"""Top-7 muns predial validados — verifica que el catálogo tenga URLs reales."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.catalogo_municipios_mx import MUNICIPIOS


TOP7 = [
    ("bc", "tijuana", 1922523, True),       # login-only pero validado
    ("gto", "leon", 1721215, True),
    ("bc", "mexicali", 1049792, True),
    ("qro", "queretaro", 1049777, True),
    ("yuc", "merida", 995129, True),
    ("sin", "culiacan", 962871, True),
    ("qroo", "cancun", 911503, True),
]


@pytest.mark.parametrize("estado,municipio,pob_min,validado_esperado", TOP7)
def test_top7_validado(estado, municipio, pob_min, validado_esperado):
    cfg = MUNICIPIOS.get(estado, {}).get(municipio)
    assert cfg is not None, f"{estado}/{municipio} no está en catálogo"
    assert cfg.validado == validado_esperado, f"{estado}/{municipio} validado={cfg.validado}"
    assert cfg.portal_predial_url, f"{estado}/{municipio} sin URL"
    assert cfg.poblacion_aprox >= pob_min * 0.95, f"{estado}/{municipio} pob fuera de rango"


def test_top7_cobertura_total():
    pob = sum(MUNICIPIOS[e][m].poblacion_aprox for e, m, _, _ in TOP7)
    # ~8.6M hab cubiertos (top-7 reales con población oficial INEGI)
    assert pob > 8_500_000, f"Cobertura top-7 = {pob}, esperado >8.5M"


def test_tijuana_marcado_login_only():
    cfg = MUNICIPIOS["bc"]["tijuana"]
    assert "login" in cfg.notas.lower() or "registro" in cfg.notas.lower(), \
        "Tijuana debe estar marcado como login/registro requerido"
