"""Path real de donatarias: parser XLSX (stdlib) + descarga con respx + live.

El XLSX de prueba replica la estructura de Dir_2026.xlsx (validada 2026-10-14):
título, nota del Anexo 14, catálogo A-M, encabezado en fila con "RFC" en la
columna D, una fila por (RFC, actividad), fecha de oficio como serial Excel.
"""

from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

import httpx
import pytest
import respx

from mp_donatarias_sat.client import (
    URL_DIRECTORIO_SAT,
    DonatariasSatClient,
    parsear_directorio_xlsx,
)
from shared.bitacora import Bitacora
from shared.cache import FileCache
from shared.errors import UpstreamError

FILAS = [
    ["DIRECTORIO DE DONATARIAS AUTORIZADAS 2026"],
    ["CORRESPONDIENTE A LA PUBLICACIÓN DEL ANEXO 14 DE LA RESOLUCIÓN MISCELÁNEA FISCAL, EN EL DIARIO OFICIAL DE LA FEDERACIÓN DE 09 DE ENERO DE 2026."],
    ["A. Organizaciones civiles y fideicomisos asistenciales (artículo 79, fracción VI de la Ley del ISR)"],
    ["ENTIDAD FEDERATIVA*", "ADMINISTRACIÓN DESCONCENTRADA*", "ACTIVIDAD O FIN AUTORIZADO", "RFC",
     "DENOMINACIÓN O RAZÓN SOCIAL*", "DOMICILIO FISCAL*", "OFICIO DE AUTORIZACIÓN", "FECHA DE OFICIO",
     "OBJETO SOCIAL AUTORIZADO", "REPRESENTANTE LEGAL", "NÚMERO TELEFÓNICO*", "E-MAIL*", "ACREDITAMIENTO",
     "ESTADO DE LOCALIZACIÓN DEL DOMICILIO*", "ESTADO DEL CONTRIBUYENTE EN EL RFC*"],
    ["Aguascalientes", "Aguascalientes 1", "A", "AAC101117RP1", "Aacafiq, AC", "Gomez Morin, Sn", "700-02-01-00-00-2021-07389", 44428, "obj", "rep", "1", "a@b", "x", "Domicilio sin Verificar", "Activo"],
    ["Aguascalientes", "Aguascalientes 1", "M", "AAC101117RP1", "Aacafiq, AC", "Gomez Morin, Sn", "700-02-01-00-00-2021-07389", 44428, "obj", "rep", "1", "a@b", "x", "Domicilio sin Verificar", "Activo"],
    ["Ciudad de Mexico", "Distrito Federal 1", "B", "CEN990101AB1", "Centro Educativo Norte, AC", "Calle 1", "600-01", 40000, "obj", "rep", "1", "c@d", "x", "No Localizado", "Suspendido"],
    ["Veracruz de Ignacio de la Llav", "Veracruz 1", "F", "ECO000101XY2", "Ecologia Viva, AC", "Calle 2", "600-02", 41000, "obj", "rep", "1", "e@f", "x", "Localizado", "Activo"],
]


def _xlsx(filas) -> bytes:
    compartidas: list[str] = []
    xml_filas = []
    for i, fila in enumerate(filas, start=1):
        celdas = []
        for j, v in enumerate(fila):
            ref = f"{chr(65 + j)}{i}"
            if isinstance(v, (int, float)):
                celdas.append(f'<c r="{ref}"><v>{v}</v></c>')
            else:
                compartidas.append(v)
                celdas.append(f'<c r="{ref}" t="s"><v>{len(compartidas) - 1}</v></c>')
        xml_filas.append(f'<row r="{i}">{"".join(celdas)}</row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/sharedStrings.xml", f"<sst {ns}>" + "".join(f"<si><t>{escape(s)}</t></si>" for s in compartidas) + "</sst>")
        z.writestr("xl/worksheets/sheet1.xml", f"<worksheet {ns}><sheetData>{''.join(xml_filas)}</sheetData></worksheet>")
    return buf.getvalue()


PAGINA = '<a href="documentos/padron_donatarias/Dir_2026.xlsx">2026</a><a href="documentos/padron_donatarias/Dir_2025_2.xlsx">2025</a>'
URL_XLSX = "https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/documentos/padron_donatarias/Dir_2026.xlsx"


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    return DonatariasSatClient(
        cache=FileCache("don_test", root=tmp_path / "cache"),
        bitacora=Bitacora("don_test", root=tmp_path / "bita"),
    )


def test_parser_agrupa_por_rfc():
    d = parsear_directorio_xlsx(_xlsx(FILAS))
    assert "ANEXO 14" in d["publicacion"]
    assert len(d["donatarias"]) == 3
    r = d["donatarias"]["AAC101117RP1"]
    assert r["entidad"] == "AGS" and r["actividades"] == ["A", "M"]
    assert r["rubros"] == ["asistencia_social", "convenio_eua"]
    assert r["fecha_autorizacion"] == "2021-08-20"
    assert d["donatarias"]["ECO000101XY2"]["entidad"] == "VER"


def test_parser_sin_encabezado_falla():
    with pytest.raises(UpstreamError):
        parsear_directorio_xlsx(_xlsx(FILAS[:3]))


@respx.mock
def test_real_consulta_busca_lista_stats(cliente):
    pagina = respx.get(URL_DIRECTORIO_SAT).respond(200, html=PAGINA)
    respx.get(URL_XLSX).respond(200, content=_xlsx(FILAS))

    r = cliente.consultar_donataria("AAC101117RP1")
    assert r["simulated"] is False and r["autorizada"] is True and r["rubro"] == "asistencia_social"
    assert r["url_consultado"] == URL_XLSX

    s = cliente.consultar_donataria("CEN990101AB1")
    assert any("Suspendido" in a for a in s["advertencias"])
    assert any("NO LOCALIZADO" in a for a in s["advertencias"])

    assert cliente.consultar_donataria("XAXX010101000")["autorizada"] is False
    assert cliente.buscar_donatarias("ecologia")["total_encontrados"] == 1
    assert cliente.listar_por_entidad("CDMX")["total"] == 1
    st = cliente.estadisticas_padron()
    assert st["total_donatarias"] == 3 and st["por_entidad_top10"]["AGS"] == 1
    assert pagina.call_count == 1  # directorio en cache


@respx.mock
def test_real_sin_red_es_error(cliente):
    respx.get(URL_DIRECTORIO_SAT).mock(side_effect=httpx.ConnectError("x"))
    with pytest.raises(UpstreamError):
        cliente.consultar_donataria("AAC101117RP1")


@respx.mock
def test_real_pagina_sin_xlsx_es_error(cliente):
    respx.get(URL_DIRECTORIO_SAT).respond(200, html="<html>rediseño</html>")
    with pytest.raises(UpstreamError):
        cliente.estadisticas_padron()


@pytest.mark.live
def test_live_directorio(cliente):
    st = cliente.estadisticas_padron()
    assert st["simulated"] is False and st["total_donatarias"] > 5000
