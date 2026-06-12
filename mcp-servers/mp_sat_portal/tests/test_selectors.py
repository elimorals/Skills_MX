"""Tests del registry de selectores."""

from __future__ import annotations

from mp_sat_portal.selectors import (
    CURRENT_VERSION,
    SelectorsV1,
    default_selectors,
)


def test_default_selectors_is_current_version():
    s = default_selectors()
    assert isinstance(s, CURRENT_VERSION)


def test_selectors_v1_has_required_fields():
    s = SelectorsV1()
    # Login
    assert s.login_url.startswith("https://")
    assert s.login_input_cer
    assert s.login_input_key
    assert s.login_input_password
    assert s.login_button_submit
    # CSF
    assert s.csf_menu_link
    assert s.csf_button_descargar
    # Buzón
    assert s.buzon_url.startswith("https://")
    # CFDI masivo
    assert s.cfdi_descarga_url.startswith("https://")
    # Timeouts numéricos
    assert s.timeout_navigation_ms > 0
    assert s.timeout_action_ms > 0


def test_selectors_v1_is_frozen():
    """Los selectores son inmutables por diseño (cambio = nueva versión)."""
    s = SelectorsV1()
    import pytest

    with pytest.raises((AttributeError, Exception)):
        s.login_url = "https://otro.com"  # type: ignore[misc]


def test_login_selectors_subset_for_breakage():
    s = SelectorsV1()
    login = s.login_selectors()
    assert s.login_input_cer in login
    assert s.login_input_key in login
    assert s.login_input_password in login
    assert s.login_button_submit in login
    # No incluye selectores de otros flujos
    assert s.csf_menu_link not in login


def test_as_dict_exports_all_fields():
    s = SelectorsV1()
    d = s.as_dict()
    # Debe contener al menos los selectores conocidos
    assert "login_url" in d
    assert "csf_menu_link" in d
    assert "buzon_lista_notificaciones" in d
    assert "cfdi_resultados_tabla" in d
    # Version está incluida
    assert "version" in d
    assert d["version"].startswith("v1")


def test_version_string_is_informative():
    s = SelectorsV1()
    assert "2026" in s.version or "Q" in s.version
