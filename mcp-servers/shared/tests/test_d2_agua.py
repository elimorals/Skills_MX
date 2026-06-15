"""D.2 — Agua organismos top descubiertos en vivo 2026-06-15."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.agua_mx import CATALOGO_AGUA, buscar_organismo


D2_AGREGADOS = [
    ("jmas_juarez", True, 1500000),
    ("ooapas", True, 750000),
    ("cespm", False, 1050000),       # login required
    ("aguah", False, 936000),         # app-only
    ("simas_saltillo", False, 880000),  # login required
]


@pytest.mark.parametrize("clave,consultable,pob", D2_AGREGADOS)
def test_organismo_existe(clave, consultable, pob):
    org = buscar_organismo(clave)
    assert org is not None, f"{clave} no en catálogo"
    assert org.consultable == consultable
    assert org.poblacion_aprox == pob


def test_d2_publicos_tienen_url_consulta():
    """JMAS y OOAPAS son los únicos consultables — deben tener url_consulta."""
    for clave in ("jmas_juarez", "ooapas"):
        org = buscar_organismo(clave)
        assert org.url_consulta, f"{clave} sin url_consulta"
        assert org.url_consulta.startswith("http")


def test_catalogo_total_18():
    assert len(CATALOGO_AGUA) == 17  # 12 originales + 5 D.2 (oapas ya existía)
