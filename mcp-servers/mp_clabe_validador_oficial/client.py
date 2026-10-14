"""Cliente mp_clabe_validador_oficial.

Validación CLABE = algoritmo oficial de dígito de control (pesos 3,7,1, local)
+ confirmación contra el catálogo **vigente** de participantes SPEI que publica
Banxico (`https://www.banxico.org.mx/cep/instituciones.do`). No existe un
servicio público que confirme que una cuenta concreta existe; eso solo lo
sabe el banco al recibir un SPEI.

Mock solo con PLUGINS_MX_MOCK=1. Si Banxico falla → UpstreamError.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_banxico_cep import spei  # noqa: E402
from mp_banxico_cep.clabe import validar_clabe as _validar_local  # noqa: E402
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402

NAMESPACE = "clabe_validador"


class ClabeValidadorClient:
    def __init__(self, bitacora: Bitacora | None = None, cache: FileCache | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self._cache = cache or FileCache(NAMESPACE)

    @staticmethod
    def _is_mock() -> bool:
        return os.environ.get("PLUGINS_MX_MOCK") == "1"

    def _catalogo_spei(self, fecha: date) -> list[dict[str, str]]:
        key = f"instituciones_{fecha.isoformat()}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        with spei.nuevo_cliente() as http:
            cat = spei.instituciones(http, fecha)
        self._cache.set(key, cat, ttl_hours=24)
        return cat

    def _participante(self, codigo3: str) -> dict[str, Any]:
        hoy = date.today()
        inst = spei.clave_participante(self._catalogo_spei(hoy), codigo3)
        return {
            "participante_spei": inst is not None,
            "institucion_spei": inst,
            "catalogo_fecha": hoy.isoformat(),
            "fuente": f"{spei.BASE_URL}instituciones.do",
        }

    def validar_clabe(self, clabe: str) -> dict[str, Any]:
        local = _validar_local(clabe)
        self.bitacora.log(
            "validar_clabe", success=True,
            params_summary={"clabe_hash": Bitacora.hash_sensitive(local["clabe_normalizada"])},
        )
        if self._is_mock():
            return mark_simulated({**local, "participante_spei": local["valida"]})
        out = {**local, "simulated": False}
        if local["banco_codigo"]:
            out.update(self._participante(local["banco_codigo"]))
            if not out["participante_spei"]:
                out["valida"] = False
                out["errores"] = [
                    *local["errores"],
                    f"El código {local['banco_codigo']} no es participante SPEI vigente según Banxico.",
                ]
        return out

    def info_banco_clabe(self, codigo_o_clabe: str) -> dict[str, Any]:
        valor = (codigo_o_clabe or "").strip().replace(" ", "").replace("-", "")
        if not valor.isdigit() or len(valor) not in (3, 18):
            raise ValidationError("Pasa un código de banco de 3 dígitos o una CLABE de 18.")
        codigo = valor[:3]
        self.bitacora.log("info_banco_clabe", success=True, params_summary={"codigo": codigo})
        if self._is_mock():
            return mark_simulated({"codigo": codigo, "participante_spei": True})
        return {"codigo": codigo, **self._participante(codigo), "simulated": False}
