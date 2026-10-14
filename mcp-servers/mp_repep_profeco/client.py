"""Cliente mp_repep_profeco — REPEP (PROFECO): handoff humano + filtro contra lista oficial.

Hallazgo 2026-10-14 (repep.profeco.gob.mx/Solicitudnumero.jsp): la consulta de un número
es para el titular de la línea y tiene controles anti-automatización deliberados
(redirección a audit.jsp, nombre del campo aleatorio por sesión, beacon JS a /c,
bloqueo de pegado y conteo de movimientos de mouse/touch en j_consulta.js). No es un
CAPTCHA, pero es el mismo tipo de barrera: no se emula. Para empresas, PROFECO vende
la lista oficial ("Comprar listas REPEP", cuenta de proveedor); con ese archivo el
filtrado sí es real y local.

Mock solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "repep_profeco"
URL_REPEP = "https://repep.profeco.gob.mx"
URL_CONSULTA = "https://repep.profeco.gob.mx/Solicitudnumero.jsp"
URL_REGISTRO = "https://repep.profeco.gob.mx/registrar_telefono.jsp"
URL_LISTAS = "https://repep.profeco.gob.mx/Busquedalista.jsp"
URL_LFPC = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf"

TEL_RE = re.compile(r"^\d{10}$")
_TEL_EN_TEXTO = re.compile(r"(?<!\d)\d{10}(?!\d)")


def _normalizar_telefono(tel: str) -> str:
    t = re.sub(r"[\s\-()]", "", tel or "")
    if t.startswith("+52"):
        t = t[3:]
    if t.startswith("52") and len(t) == 12:
        t = t[2:]
    if not TEL_RE.match(t):
        raise ValidationError(f"Teléfono inválido (10 dígitos esperados): {tel!r}")
    return t


def cargar_lista_repep(path: str | Path) -> set[str]:
    """Lee el archivo oficial descargado de PROFECO y extrae los números de 10 dígitos."""
    p = Path(path).expanduser()
    if not p.is_file():
        raise ValidationError(f"No existe la lista REPEP: {p}")
    numeros = set(_TEL_EN_TEXTO.findall(p.read_text(encoding="utf-8", errors="replace")))
    if not numeros:
        # Un archivo mal leído no debe convertirse en "todos contactables".
        raise ValidationError(
            "No se encontraron números de 10 dígitos en la lista REPEP; revisa el formato "
            "(si viene lada y número en columnas separadas, únelos antes)."
        )
    return numeros


class REPEPClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar(self, telefono: str) -> dict[str, Any]:
        tel = _normalizar_telefono(telefono)
        if is_mock_mode([], default_when_no_creds=False):
            inscrito = int(tel[-1]) % 3 != 0
            return mark_simulated({"telefono": tel, "inscrito_repep": inscrito,
                                   "puede_contactar": not inscrito})
        self._bitacora.log("consultar_handoff", success=True,
                           params_summary={"tel_hash": self._bitacora.hash_sensitive(tel)})
        return {
            "telefono": tel,
            "inscrito_repep": None,
            "puede_contactar": None,
            "handoff_humano": True,
            "motivo": ("La consulta individual de PROFECO es para el titular de la línea y "
                       "bloquea la automatización; no se evade."),
            "url": URL_CONSULTA,
            "pasos": [
                "El titular abre la URL, escribe el número a 10 dígitos (sin pegar) y pulsa Consultar.",
                "Para campañas: usar repep_filtrar_lote con la lista oficial comprada en PROFECO.",
            ],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def filtrar_lote(self, telefonos: list[str], lista_repep_path: str | None = None) -> dict[str, Any]:
        """Separa contactables vs inscritos usando la lista oficial descargada de PROFECO."""
        if not telefonos:
            raise ValidationError("Lote vacío")
        if len(telefonos) > 5000:
            raise ValidationError("Lote excede límite de 5000 teléfonos")
        validos, invalidos = [], []
        for t in telefonos:
            try:
                validos.append(_normalizar_telefono(t))
            except ValidationError:
                invalidos.append(t)

        if is_mock_mode([], default_when_no_creds=False):
            bloq = [t for t in validos if int(t[-1]) % 3 != 0]
            return mark_simulated({"total_input": len(telefonos),
                                   "contactables": [t for t in validos if t not in bloq],
                                   "bloqueados_repep": bloq, "invalidos": invalidos})

        if not lista_repep_path:
            return {
                "total_input": len(telefonos),
                "filtrado": False,
                "handoff_humano": True,
                "motivo": "Sin la lista oficial REPEP no se puede afirmar que un número es contactable.",
                "url": URL_LISTAS,
                "pasos": [
                    "Registrarse como proveedor en repep.profeco.gob.mx y comprar la lista REPEP.",
                    "Pasar la ruta del archivo descargado en lista_repep_path.",
                ],
                "simulated": False,
            }

        inscritos = cargar_lista_repep(lista_repep_path)
        bloqueados = [t for t in validos if t in inscritos]
        contactables = [t for t in validos if t not in inscritos]
        return {
            "total_input": len(telefonos),
            "filtrado": True,
            "contactables": contactables,
            "bloqueados_repep": bloqueados,
            "invalidos": invalidos,
            "stats": {
                "lista_repep_numeros": len(inscritos),
                "contactables_count": len(contactables),
                "bloqueados_count": len(bloqueados),
                "tasa_bloqueo_pct": round(100 * len(bloqueados) / max(1, len(validos)), 1),
            },
            "nota": "Vigencia del resultado = fecha de la lista descargada; actualízala con la frecuencia que exija PROFECO.",
            "fuente": URL_LISTAS,
            "simulated": False,
        }

    def inscribir(self, telefono: str, propietario_curp: str | None = None) -> dict[str, Any]:
        """Nunca inscribe: devuelve los canales oficiales para que el titular lo haga."""
        tel = _normalizar_telefono(telefono)
        return {
            "telefono": tel,
            "inscrito": False,
            "handoff_humano": True,
            "motivo": "La inscripción la hace el titular de la línea; este MCP es de solo lectura.",
            "url": URL_REGISTRO,
            "pasos": [
                "Registrar en línea en la URL, o llamar desde la línea al 96 28 00 00 "
                "(CDMX, Guadalajara, Monterrey) o al 800 962 8000 (resto del país).",
            ],
            "fuente": URL_REPEP,
        }

    def estadisticas(self) -> dict[str, Any]:
        """Sin cifras inventadas: el número de inscritos no se publica en el portal."""
        return {
            "inscritos_publicados": None,
            "nota": "PROFECO no publica el total de inscritos en repep.profeco.gob.mx (revisado 2026-10-14).",
            "no_competencia_profeco": ("Llamadas de servicios financieros, bancos, seguros, afores, "
                                       "cobranza, organizaciones políticas, beneficencia y encuestadores "
                                       "(aviso en la portada del REPEP)."),
            "base_legal": "Arts. 18 y 18 BIS Ley Federal de Protección al Consumidor",
            "fuente": URL_REPEP,
            "ley": URL_LFPC,
        }
