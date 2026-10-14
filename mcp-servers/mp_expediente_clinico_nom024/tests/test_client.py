"""Tests mp_expediente_clinico_nom024."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_receta_basica_no_controlado():
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    r = c.generar_receta_electronica(
        medico_cedula="1234567", medico_nombre="Dra. Ana López",
        medico_especialidad="Medicina General",
        paciente_nombre="Juan Hernández", paciente_edad=34, paciente_sexo="M",
        medicamentos=[{"nombre": "paracetamol", "dosis": "500mg", "via": "VO",
                       "frecuencia": "c/8h", "duracion": "5 días"}],
        diagnostico="Cefalea tensional",
    )
    assert r["folio"].startswith("RX-")
    assert r["vigencia_dias"] is None  # sin vigencia legal fijada para no controlados
    assert r["fecha_vencimiento"] is None
    assert r["requiere_recetario_especial_codigo_barras"] is False
    assert r["medicamentos"][0]["fraccion_venta_art226"] == "no_controlado"


def test_receta_con_medicamento_fraccion_i():
    """Morfina: estupefaciente (LGS Art. 234) → Art. 226 fr. I, recetario especial (Art. 241)."""
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    r = c.generar_receta_electronica(
        medico_cedula="9876543", medico_nombre="Dr. Algólogo",
        medico_especialidad="Anestesiología y Algología",
        paciente_nombre="Paciente Oncológico", paciente_edad=58, paciente_sexo="F",
        medicamentos=[{"nombre": "morfina 10mg", "dosis": "10mg",
                       "via": "VO", "frecuencia": "c/4h", "duracion": "1 día"}],
        diagnostico="Dolor oncológico severo",
    )
    assert r["requiere_recetario_especial_codigo_barras"] is True
    assert r["advertencias"]
    med = r["medicamentos"][0]
    assert med["fraccion_venta_art226"] == "I"
    assert med["categoria_lgs"] == "estupefaciente_art234"


def test_benzodiazepina_y_fenobarbital_reglas_lgs():
    from mp_expediente_clinico_nom024.client import ECEClient
    from shared.ece_nom024_mx import clasificar_medicamento
    clon = clasificar_medicamento("clonazepam 2mg")
    assert (clon.categoria, clon.fraccion, clon.vigencia_receta_dias, clon.surtidos_max) == \
        ("psicotropico_245_III", "II", 30, 1)
    feno = clasificar_medicamento("fenobarbital")
    assert (feno.fraccion, feno.vigencia_meses, feno.surtidos_max) == ("III", 6, 3)
    assert clasificar_medicamento("metilfenidato").categoria == "estupefaciente_art234"
    r = ECEClient().generar_receta_electronica(
        medico_cedula="1234567", medico_nombre="X", medico_especialidad="MG",
        paciente_nombre="Y", paciente_edad=30, paciente_sexo="F",
        medicamentos=[{"nombre": "fenobarbital"}], diagnostico="Epilepsia")
    assert r["fecha_vencimiento"] is not None


def test_receta_con_curp_hashea():
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    r = c.generar_receta_electronica(
        medico_cedula="1234567", medico_nombre="X", medico_especialidad="MG",
        paciente_nombre="Y", paciente_edad=20, paciente_sexo="M",
        paciente_curp="HEGJ900101HDFRRN09",
        medicamentos=[{"nombre": "ibuprofeno"}],
        diagnostico="Dolor"
    )
    # CURP no debe estar en claro
    assert "HEGJ900101HDFRRN09" not in str(r["paciente"])
    assert r["paciente"]["curp_hash"]


def test_receta_curp_invalida_lanza():
    from mp_expediente_clinico_nom024.client import ECEClient
    from shared.errors import ValidationError
    c = ECEClient()
    with pytest.raises(ValidationError):
        c.generar_receta_electronica(
            medico_cedula="1234567", medico_nombre="X", medico_especialidad="MG",
            paciente_nombre="Y", paciente_edad=20, paciente_sexo="M",
            paciente_curp="INVALIDA",
            medicamentos=[{"nombre": "ibuprofeno"}], diagnostico="Dolor"
        )


def test_receta_sin_medicamentos_lanza():
    from mp_expediente_clinico_nom024.client import ECEClient
    from shared.errors import ValidationError
    c = ECEClient()
    with pytest.raises(ValidationError):
        c.generar_receta_electronica(
            medico_cedula="1234567", medico_nombre="X", medico_especialidad="MG",
            paciente_nombre="Y", paciente_edad=20, paciente_sexo="M",
            medicamentos=[], diagnostico="X"
        )


def test_verificar_medico_estructural():
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    r = c.verificar_medico_para_receta(cedula="1234567")
    assert r["estructural_valida"] is True
    assert r["vigente"] is None  # se delega a mp_sep_profesional


def test_verificar_medico_mock_solo_con_flag(monkeypatch):
    from mp_expediente_clinico_nom024.client import ECEClient
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert ECEClient().verificar_medico_para_receta(cedula="1234560")["simulated"] is True


def test_validar_sistema_cumple():
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    capacidades_totales = [
        "trazabilidad_completa", "firma_electronica_avanzada", "respaldo_seguro_5_anios",
        "consentimiento_paciente_documentado", "cédula_validada_médico",
        "identificador_paciente", "controles_acceso_rbac", "registro_modificaciones",
        "autenticacion_usuarios",
    ]
    r = c.validar_sistema_ece("sys-001", capacidades_totales)
    assert r["cumple_nom024"] is True
    assert r["score"] >= 70


def test_validar_sistema_incompleto():
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    r = c.validar_sistema_ece("sys-002", ["trazabilidad_completa"])
    assert r["cumple_nom024"] is False
    assert r["obligatorios_faltantes"] > 0


def test_consentimiento_paciente_genera_token():
    from mp_expediente_clinico_nom024.client import ECEClient
    c = ECEClient()
    r = c.consentimiento_paciente(curp="HEGJ900101HDFRRN09",
                                   proposito="Consulta médica de medicina general")
    assert r["token_consentimiento"]
    assert len(r["token_consentimiento"]) == 32
    assert "HEGJ900101HDFRRN09" not in str(r)


def test_consentimiento_proposito_corto_lanza():
    from mp_expediente_clinico_nom024.client import ECEClient
    from shared.errors import ValidationError
    c = ECEClient()
    with pytest.raises(ValidationError):
        c.consentimiento_paciente(curp="HEGJ900101HDFRRN09", proposito="x")
