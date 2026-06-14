"""Cliente unificado para validación de cédulas profesionales SEP (RNP).

Auto-routing por modo de consulta:
1. **Por cédula** (8 dígitos): consulta directa más rápida.
2. **Por datos**: nombre + apellidos + opcional CURP. Útil cuando solo se tiene el nombre del profesionista.
3. **Por CURP**: 18 chars validación estructural + consulta SEP.

Caché de 30 días — los datos del RNP cambian raramente.

Validado Playwright MCP 2026-06-13: portal https://cedulaprofesional.sep.gob.mx/
SIN CAPTCHA — totalmente automatizable.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.playwright_real import is_public_real_enabled  # noqa: E402
from shared.sep_cedula import (  # noqa: E402
    URL_SEP_CEDULA,
    consultar_cedula_sep,
    validar_formato_cedula,
)


NAMESPACE = "sep_profesional"

# Validación CURP estructural (mismo patrón que mp_curp_renapo)
CURP_REGEX = re.compile(
    r"^[A-Z][AEIOUX][A-Z]{2}\d{2}"
    r"(0[1-9]|1[0-2])"
    r"(0[1-9]|[12]\d|3[01])"
    r"[HM]"
    r"(AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)"
    r"[B-DF-HJ-NP-TV-Z]{3}"
    r"[A-Z0-9]\d$"
)

# Profesiones reguladas que requieren validación de cédula obligatoria
PROFESIONES_REGULADAS = {
    "salud": [
        "Médico Cirujano", "Médico Especialista", "Cirujano Dentista",
        "Psicólogo", "Psicoterapeuta", "Enfermería", "Nutriólogo",
        "Optometría", "Químico Farmacéutico Biólogo",
    ],
    "legal": [
        "Licenciado en Derecho", "Abogado",
    ],
    "contable_fiscal": [
        "Contador Público", "Licenciado en Contaduría",
    ],
    "ingenierias_riesgo": [
        "Ingeniero Civil", "Arquitecto",  # firma planos
        "Ingeniero Químico", "Ingeniero Industrial",
    ],
    "educacion": [
        "Licenciado en Educación", "Pedagogo",
    ],
}


def _normalizar(s: str) -> str:
    """NFKD + strip acentos + lowercase. Matching estable contra UTF-8 con/sin acentos."""
    nfkd = unicodedata.normalize("NFKD", s or "")
    sin_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_acentos.lower().strip()


def _profesion_es_regulada(profesion: str) -> Optional[str]:
    """Devuelve la categoría si la profesión está regulada, None si no.

    Normaliza ambos lados (acentos + lowercase) y hace match bidireccional.
    """
    if not profesion:
        return None
    profesion_norm = _normalizar(profesion)
    if not profesion_norm:
        return None
    for cat, lista in PROFESIONES_REGULADAS.items():
        for p in lista:
            p_norm = _normalizar(p)
            if p_norm and (p_norm in profesion_norm or profesion_norm in p_norm):
                return cat
    return None


class SepProfesionalClient:
    """Cliente unificado SEP RNP."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        # Hash de cédula/CURP para bitácora (datos personales sensibles)
        safe = dict(params)
        for k in ("cedula", "curp"):
            if k in safe and safe[k]:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(safe.pop(k)))
        self._bitacora.log(op, success=True, params_summary=safe)

    # ============================================================
    # Tools principales
    # ============================================================

    def consultar_cedula(
        self,
        cedula: str,
        validar_vigencia: bool = True,
    ) -> dict[str, Any]:
        """Consulta cédula profesional por número (8 dígitos).

        Args:
            cedula: número de cédula 7-8 dígitos numéricos
            validar_vigencia: si True, agrega flag de profesión regulada

        Returns:
            Dict con: cedula, nombre_completo, profesion, institucion,
                      fecha_expedicion, vigente, categoria_regulada, simulated
        """
        if not validar_formato_cedula(cedula):
            raise ValidationError(
                f"Cédula '{cedula}' no tiene formato válido (7-8 dígitos numéricos)."
            )

        cache_key = f"cedula_{cedula}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("consultar_cedula", {"cedula": cedula})

        resultado = consultar_cedula_sep(cedula=cedula)

        # Enriquecer con categoría regulada
        if validar_vigencia and resultado.get("profesion"):
            cat = _profesion_es_regulada(resultado["profesion"])
            resultado["categoria_regulada"] = cat
            resultado["requiere_validacion_obligatoria"] = cat is not None

        self._cache.set(cache_key, resultado, ttl_minutes=43200)  # 30 días
        return resultado

    def consultar_por_datos(
        self,
        nombre: str,
        primer_apellido: str,
        segundo_apellido: Optional[str] = None,
        curp: Optional[str] = None,
    ) -> dict[str, Any]:
        """Consulta cédula por nombre + apellidos (útil cuando no se tiene el número).

        Args:
            nombre: nombre(s)
            primer_apellido: apellido paterno
            segundo_apellido: apellido materno (opcional)
            curp: CURP del profesionista (opcional, mejora precisión)
        """
        if not nombre or not primer_apellido:
            raise ValidationError("nombre y primer_apellido son requeridos.")

        if curp and not CURP_REGEX.match(curp.upper()):
            raise ValidationError(f"CURP '{curp}' no tiene formato válido.")

        self._log("consultar_por_datos", {
            "nombre": nombre[:20], "primer_apellido": primer_apellido[:20],
            "curp": curp,
        })

        resultado = consultar_cedula_sep(
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            curp=curp,
        )

        if resultado.get("profesion"):
            cat = _profesion_es_regulada(resultado["profesion"])
            resultado["categoria_regulada"] = cat
            resultado["requiere_validacion_obligatoria"] = cat is not None

        return resultado

    def validar_medico_para_consulta(
        self,
        cedula: str,
        cedula_especialidad: Optional[str] = None,
    ) -> dict[str, Any]:
        """Validación específica para telemedicina-mx (NOM-004 + Acuerdo COFEPRIS 2024).

        Para que un médico pueda dar consulta de telemedicina, debe:
        1. Tener cédula profesional vigente (médico cirujano u homólogo)
        2. Si va a recetar medicamentos de control: cédula de especialidad

        Returns:
            {
                "puede_dar_consulta": bool,
                "cedula_general_ok": bool,
                "cedula_especialidad_ok": bool,
                "advertencias": [...],
                "cedulas_validadas": [...]
            }
        """
        self._log("validar_medico_para_consulta", {
            "cedula": cedula, "cedula_especialidad": cedula_especialidad,
        })

        advertencias = []
        cedulas_validadas = []

        # 1. Cédula general
        try:
            general = self.consultar_cedula(cedula)
        except (ValidationError, UpstreamError) as e:
            return {
                "puede_dar_consulta": False,
                "razon": f"Cédula general inválida: {e}",
                "cedula_general_ok": False,
            }

        cedula_general_ok = general.get("vigente", False) and (
            general.get("categoria_regulada") == "salud"
        )
        cedulas_validadas.append({
            "tipo": "general",
            "cedula": cedula,
            "vigente": general.get("vigente"),
            "profesion": general.get("profesion"),
            "ok": cedula_general_ok,
        })

        if not cedula_general_ok:
            advertencias.append(
                "Cédula general no corresponde a profesión de salud. "
                f"Profesión detectada: {general.get('profesion', 'desconocida')}"
            )

        # 2. Cédula de especialidad (opcional pero requerida para medicamentos controlados)
        cedula_especialidad_ok = True
        if cedula_especialidad:
            try:
                esp = self.consultar_cedula(cedula_especialidad)
                cedula_especialidad_ok = esp.get("vigente", False)
                cedulas_validadas.append({
                    "tipo": "especialidad",
                    "cedula": cedula_especialidad,
                    "vigente": esp.get("vigente"),
                    "profesion": esp.get("profesion"),
                    "ok": cedula_especialidad_ok,
                })
                if not cedula_especialidad_ok:
                    advertencias.append("Cédula de especialidad NO vigente — no podrá recetar medicamentos controlados.")
            except Exception as e:
                cedula_especialidad_ok = False
                advertencias.append(f"Error validando especialidad: {e}")

        puede = cedula_general_ok  # mínimo cédula general

        return {
            "puede_dar_consulta": puede,
            "cedula_general_ok": cedula_general_ok,
            "cedula_especialidad_ok": cedula_especialidad_ok,
            "puede_recetar_controlados": cedula_general_ok and cedula_especialidad_ok and bool(cedula_especialidad),
            "advertencias": advertencias,
            "cedulas_validadas": cedulas_validadas,
            "nombre_titular": general.get("nombre_completo"),
            "cumple_nom_004": cedula_general_ok,
            "cumple_cofepris_2024": cedula_general_ok,
        }

    def listar_profesiones_reguladas(self) -> dict[str, Any]:
        """Lista profesiones reguladas que requieren validación obligatoria."""
        return {
            "categorias": list(PROFESIONES_REGULADAS.keys()),
            "profesiones_por_categoria": PROFESIONES_REGULADAS,
            "total": sum(len(v) for v in PROFESIONES_REGULADAS.values()),
            "url_consulta": URL_SEP_CEDULA,
        }
