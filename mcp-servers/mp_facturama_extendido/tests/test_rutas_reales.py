"""Rutas reales de la API web de Facturama.

Contrato tomado de satcfdi.pacs.facturama (MIT, v26.8.0), que opera contra producción:
descargas y cancelación usan el Id interno de Facturama, que se resuelve por UUID en el listado.
"""

from __future__ import annotations

import base64

import pytest
import respx

from mp_facturama_extendido.client import FacturamaClient
from shared.errors import NotFoundError

B = "https://apisandbox.facturama.mx"
UUID = "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ITEM = {"Id": "fact-123", "Uuid": UUID, "Status": "active", "Folio": "7", "Date": "2026-10-10T12:00:00"}


@pytest.fixture
def cliente() -> FacturamaClient:
    return FacturamaClient(user="u", password="p")


def _listado(items=(ITEM,)):
    return respx.get(f"{B}/api/Cfdi").respond(200, json=list(items))


@respx.mock
async def test_cancelar_usa_id_y_type_issued(cliente) -> None:
    lista = _listado()
    ruta = respx.delete(f"{B}/api/Cfdi/fact-123").respond(200, json={"Status": "canceled"})
    await cliente.cancelar_cfdi(UUID, "02")
    assert lista.calls.last.request.url.params["keyword"] == UUID
    q = ruta.calls.last.request.url.params
    assert q["type"] == "issued" and q["motive"] == "02"


@respx.mock
async def test_descargas_por_id(cliente) -> None:
    _listado()
    contenido = base64.b64encode(b"%PDF-1.4").decode()
    respx.get(f"{B}/api/Cfdi/pdf/issued/fact-123").respond(200, json={"Content": contenido})
    respx.get(f"{B}/api/Cfdi/xml/issued/fact-123").respond(200, json={"Content": "<cfdi/>"})
    assert (await cliente.descargar_pdf(UUID))["pdf_base64"] == contenido
    assert (await cliente.descargar_xml(UUID))["xml"] == "<cfdi/>"


@respx.mock
async def test_estatus_sale_del_listado(cliente) -> None:
    _listado()
    r = await cliente.consultar_estatus(UUID)
    assert r["estatus"] == "active" and r["simulated"] is False


@respx.mock
async def test_uuid_inexistente(cliente) -> None:
    _listado(items=())
    with pytest.raises(NotFoundError):
        await cliente.descargar_xml(UUID)


@respx.mock
async def test_buscar_filtra_fechas_y_limite(cliente) -> None:
    viejo = {**ITEM, "Id": "f-0", "Date": "2026-01-01T00:00:00"}
    ruta = _listado(items=(ITEM, viejo))
    r = await cliente.buscar_cfdis(rfc_receptor="XAXX010101000", fecha_desde="2026-10-01", limit=5)
    q = ruta.calls.last.request.url.params
    assert q["type"] == "issued" and q["keyword"] == "XAXX010101000"
    assert [x["Id"] for x in r["cfdis"]] == ["fact-123"]
