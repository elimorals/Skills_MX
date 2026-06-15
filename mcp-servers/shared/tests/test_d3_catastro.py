"""D.3 — Catastros estatales discovery 2026-06-15."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.catastro_estatal import CATALOGO_CATASTRO_ESTATAL, buscar_catastro


D3_AGREGADOS = [
    ("ovica_cdmx", "login"),
    ("catastro_jal", "indirecto"),
    ("ircnl", "login"),
    ("catastro_gto", "indirecto"),
    ("icreson_son", "indirecto"),
]


@pytest.mark.parametrize("clave,metodo", D3_AGREGADOS)
def test_catastro_existe(clave, metodo):
    c = buscar_catastro(clave)
    assert c is not None, f"{clave} no en catálogo"
    assert c.metodo == metodo
    assert "Discovery 2026-06-15" in c.notas


def test_patron_nacional_consulta_publica_no_disponible():
    """Confirmación: ningún catastro estatal D.3 expone consulta pública por cuenta."""
    for clave, _ in D3_AGREGADOS:
        c = buscar_catastro(clave)
        assert c.metodo in ("login", "indirecto", "no_implementado"), \
            f"{clave} no debería ser 'publica' o 'publica_captcha'"


def test_catalogo_total_10():
    assert len(CATALOGO_CATASTRO_ESTATAL) == 10  # 5 originales + 5 D.3
