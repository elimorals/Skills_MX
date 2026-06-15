"""Cliente mp_llave_mx — catálogo + SSO ciudadano."""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.llave_mx import (  # noqa: E402
    CATALOGO_TRAMITES_LLAVE_MX,
    CATEGORIAS_LLAVE_MX,
    URL_LLAVE_MX,
    URL_PORTAL_UNIFICADO,
    buscar_tramite,
    tramites_por_categoria,
    tramites_por_dependencia,
)
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "llave_mx"
CURP_RE = re.compile(r"^[A-Z][AEIOU][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM][A-Z]{5}[A-Z0-9]\d$")


def _validar_curp(curp: str) -> str:
    curp = (curp or "").strip().upper()
    if not CURP_RE.match(curp):
        raise ValidationError(f"CURP inválida: {curp!r}")
    return curp


class LlaveMXClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def autenticar(self, curp: str, password: str) -> dict[str, Any]:
        """Mock SSO. Path real: POST https://www.llave.gob.mx/oauth."""
        curp = _validar_curp(curp)
        if not password or len(password) < 6:
            raise ValidationError("password mínimo 6 caracteres")

        ahora = datetime.now(timezone.utc)
        token = hashlib.sha256(
            f"{curp}|{ahora.isoformat()}|llavemx-mock".encode("utf-8")
        ).hexdigest()[:48]

        self._bitacora.log("autenticar", success=True,
                           params_summary={"curp_hash": self._bitacora.hash_sensitive(curp)})
        return mark_simulated({
            "ok": True,
            "token_sso": token,
            "vigencia_horas": 8,
            "expira_en": (ahora + timedelta(hours=8)).isoformat(),
            "curp_hash": self._bitacora.hash_sensitive(curp),
            "url_portal": URL_PORTAL_UNIFICADO,
            "url_llave": URL_LLAVE_MX,
        })

    def validar_token(self, token: str) -> dict[str, Any]:
        """Mock: valida que el token tenga shape correcto."""
        if not token or len(token) != 48:
            raise ValidationError(f"token inválido (esperado 48 chars): {len(token)}")
        return mark_simulated({
            "token": token,
            "valido": True,
            "tiempo_restante_horas": 7.5,
            "puede_acceder": True,
        })

    def listar_tramites(self, categoria: str | None = None,
                        dependencia: str | None = None) -> dict[str, Any]:
        if categoria:
            items = tramites_por_categoria(categoria)
        elif dependencia:
            items = tramites_por_dependencia(dependencia)
        else:
            items = list(CATALOGO_TRAMITES_LLAVE_MX)
        return {
            "filtro": {"categoria": categoria, "dependencia": dependencia},
            "total": len(items),
            "categorias_disponibles": CATEGORIAS_LLAVE_MX,
            "tramites": [{
                "clave": t.clave, "nombre": t.nombre,
                "dependencia": t.dependencia, "categoria": t.categoria,
                "requiere_e_firma": t.requiere_e_firma,
                "requiere_cita_presencial": t.requiere_cita_presencial,
                "url_directa": t.url_directa,
            } for t in items],
        }

    def detalle_tramite(self, clave: str) -> dict[str, Any]:
        t = buscar_tramite(clave)
        if t is None:
            raise ValidationError(f"trámite no encontrado: {clave}")
        return mark_simulated({
            "clave": t.clave,
            "nombre": t.nombre,
            "dependencia": t.dependencia,
            "categoria": t.categoria,
            "requiere_e_firma": t.requiere_e_firma,
            "requiere_cita_presencial": t.requiere_cita_presencial,
            "url_directa": t.url_directa,
            "accesible_con_llave_mx": True,
            "tiempo_estimado": "5-30 min" if not t.requiere_cita_presencial else "30-60 min presencial",
        })

    def vincular_e_firma(self, curp: str) -> dict[str, Any]:
        """Mock vincular e.firma a Llave MX (requiere upload .key + .cer en real)."""
        curp = _validar_curp(curp)
        return mark_simulated({
            "curp_hash": self._bitacora.hash_sensitive(curp),
            "e_firma_vinculada": True,
            "fecha_vinculacion": datetime.now(timezone.utc).isoformat(),
            "nota": "Path real requiere upload .key + .cer + contraseña FIEL",
        })
