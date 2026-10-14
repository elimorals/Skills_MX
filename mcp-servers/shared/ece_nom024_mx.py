"""Expediente Clínico Electrónico (SIRES) + receta — NOM-024-SSA3-2012, NOM-004-SSA3-2012 y LGS.

Fuentes verificadas el 2026-10-14:
- NOM-024-SSA3-2012 (DOF 30-11-2012, nota 5280847): 6.5.1 CURP validada como identificador (los SIRES
  no deben autogenerarla); 6.6.1 sistema de gestión de seguridad con confidencialidad, integridad,
  disponibilidad, trazabilidad y no repudio; 6.6.2 documentos electrónicos estructurados e
  inalterables y permitir la firma electrónica avanzada del profesional; 6.6.3 autenticación de
  usuarios; 6.6.4 autorización por roles; 6.6.6 exportación y control de consentimientos;
  6.1.3.1 estándares de intercambio (HL7 CDA, HL7 V3, XML) según el alcance.
- NOM-004-SSA3-2012 (DOF 15-10-2012, nota 5272787) 5.4: conservar el expediente mínimo 5 años desde
  el último acto médico.
- LGS vigente (diputados.gob.mx, últimas reformas DOF 15-01-2026):
  * Art. 226: fracciones de venta (I receta/permiso especial; II receta retenida, vigencia 30 días;
    III receta que se surte hasta 3 veces; IV resurtible; V-VI sin receta); prescripción en
    denominación genérica (párrafo adicionado DOF 30-03-2022).
  * Arts. 234 (estupefacientes), 240-241 (recetario especial con código de barras, tratamientos
    ≤ 30 días; prescriben médicos cirujanos, cirujanos dentistas y veterinarios — no se exige especialidad).
  * Art. 245 fr. III → Art. 251: receta con cédula, se surte una vez y se retiene.
  * Art. 245 fr. IV → Art. 252: receta con cédula, hasta 3 veces en 6 meses.
  * Decreto DOF 15-01-2026: agrega el Capítulo VI Bis "Salud Digital" (Arts. 71 Bis-71 Octies);
    obliga a instituciones PÚBLICAS a implementarla y fija condiciones a la telesalud. No vuelve
    obligatorio el ECE para consultorios privados.

Ubicación de cada fármaco en las listas de la LGS vigente (búsqueda en el texto, 2026-10-14):
Art. 234: morfina, fentanilo, oxicodona, metadona, buprenorfina, metilfenidato.
Art. 245 fr. III: alprazolam, clonazepam, diazepam, lorazepam, tramadol. Art. 245 fr. IV: fenobarbital.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

URL_NOM024 = "https://dof.gob.mx/nota_detalle.php?codigo=5280847&fecha=30/11/2012"
URL_NOM004 = "https://dof.gob.mx/nota_detalle.php?codigo=5272787&fecha=15/10/2012"
URL_LGS = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf"

FraccionVenta = Literal["I", "II", "III", "IV", "no_controlado"]  # LGS Art. 226
Categoria = Literal["estupefaciente_art234", "psicotropico_245_III", "psicotropico_245_IV", "no_controlado"]

# Alias para compatibilidad de imports existentes
FraccionCofepris = FraccionVenta


@dataclass
class RequisitoNOM024:
    clave: str
    descripcion: str
    obligatorio: bool = True
    seccion: str = "sistema"  # sistema / expediente / firma
    fundamento: str = ""


REQUISITOS_NOM024: list[RequisitoNOM024] = [
    RequisitoNOM024("trazabilidad_completa",
                    "SGSI que asegure confidencialidad, integridad, disponibilidad, trazabilidad y no repudio.",
                    fundamento="NOM-024 6.6.1"),
    RequisitoNOM024("registro_modificaciones",
                    "Documentos electrónicos estructurados e inalterables (registro de auditoría).",
                    fundamento="NOM-024 6.6.2 y def. 3.42"),
    RequisitoNOM024("firma_electronica_avanzada",
                    "Permitir la firma electrónica avanzada del profesional de la salud.",
                    seccion="firma", fundamento="NOM-024 6.6.2"),
    RequisitoNOM024("autenticacion_usuarios",
                    "Autenticar usuarios, organizaciones y dispositivos (mínimo usuario y contraseña).",
                    fundamento="NOM-024 6.6.3"),
    RequisitoNOM024("controles_acceso_rbac",
                    "Autorización basada en roles definidos por el prestador.",
                    fundamento="NOM-024 6.6.4"),
    RequisitoNOM024("consentimiento_paciente_documentado",
                    "Exportar información del paciente y controlar sus consentimientos.",
                    seccion="expediente", fundamento="NOM-024 6.6.6"),
    RequisitoNOM024("identificador_paciente",
                    "CURP validada como identificador único; el sistema no debe autogenerarla.",
                    seccion="expediente", fundamento="NOM-024 6.5.1"),
    RequisitoNOM024("respaldo_seguro_5_anios",
                    "Conservar el expediente mínimo 5 años desde el último acto médico.",
                    fundamento="NOM-004-SSA3-2012 5.4"),
    RequisitoNOM024("interoperabilidad_hl7",
                    "Estándares de intercambio (HL7 CDA, HL7 V3, XML) según el alcance del intercambio.",
                    obligatorio=False, fundamento="NOM-024 6.1.3.1 (\"se pueden considerar\")"),
    RequisitoNOM024("cédula_validada_médico",
                    "Validar la cédula profesional del médico emisor (buena práctica; no es numeral de la NOM-024).",
                    obligatorio=False, seccion="firma", fundamento="Buena práctica"),
    RequisitoNOM024("anonimización_estadística",
                    "Anonimización para reportes estadísticos.",
                    obligatorio=False, fundamento="Buena práctica"),
]


@dataclass
class MedicamentoControlado:
    nombre: str
    categoria: Categoria
    fraccion: FraccionVenta            # LGS Art. 226
    vigencia_receta_dias: Optional[int]
    surtidos_max: Optional[int]
    regla: str
    fundamento: str
    vigencia_meses: Optional[int] = None
    requiere_cedula_especialidad: bool = False  # ninguna regla de la LGS lo exige


_ESTUP = ("estupefaciente_art234", "I", None, 1,
          "Recetario especial con código de barras; tratamiento ≤ 30 días; solo establecimientos autorizados.",
          "LGS Arts. 226 fr. I, 234, 240-242")
_PSI3 = ("psicotropico_245_III", "II", 30, 1,
         "Receta con número de cédula; se surte una sola vez y se retiene; vigencia 30 días.",
         "LGS Arts. 226 fr. II, 245 fr. III, 251")
_PSI4 = ("psicotropico_245_IV", "III", None, 3,
         "Receta con número de cédula; hasta 3 surtidos en 6 meses; se retiene en el tercero.",
         "LGS Arts. 226 fr. III, 245 fr. IV, 252", 6)

CATALOGO_MEDICAMENTOS_CONTROLADOS: list[MedicamentoControlado] = [
    MedicamentoControlado("morfina", *_ESTUP),
    MedicamentoControlado("fentanilo", *_ESTUP),
    MedicamentoControlado("oxicodona", *_ESTUP),
    MedicamentoControlado("metadona", *_ESTUP),
    MedicamentoControlado("buprenorfina", *_ESTUP),
    MedicamentoControlado("metilfenidato", *_ESTUP),
    MedicamentoControlado("tramadol", *_PSI3),
    MedicamentoControlado("alprazolam", *_PSI3),
    MedicamentoControlado("clonazepam", *_PSI3),
    MedicamentoControlado("diazepam", *_PSI3),
    MedicamentoControlado("lorazepam", *_PSI3),
    MedicamentoControlado("fenobarbital", *_PSI4),
]


def clasificar_medicamento(nombre: str) -> MedicamentoControlado:
    """Clasificación según las listas de la LGS; fuera del catálogo → no_controlado (verificar)."""
    n = (nombre or "").strip().lower()
    for m in CATALOGO_MEDICAMENTOS_CONTROLADOS:
        if m.nombre in n:
            return m
    return MedicamentoControlado(
        nombre=nombre, categoria="no_controlado", fraccion="no_controlado",
        vigencia_receta_dias=None, surtidos_max=None,
        regla="No está en el catálogo local; confirmar su fracción (Art. 226 LGS) en el registro sanitario.",
        fundamento="LGS Art. 226",
    )


def calcular_vigencia_minima(medicamentos: list[dict]) -> Optional[int]:
    """Menor vigencia legal en días entre los medicamentos; None si ninguno tiene una fijada en ley."""
    vigencias = [v for v in (clasificar_medicamento(m.get("nombre", "")).vigencia_receta_dias
                             for m in medicamentos) if v is not None]
    return min(vigencias) if vigencias else None


def fecha_vencimiento_iso(fecha_emision_iso: str, dias: int | None = None, meses: int | None = None) -> str:
    """Suma días o meses calendario (Art. 252: "seis meses") a una fecha ISO."""
    base = datetime.strptime(fecha_emision_iso[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if meses:
        m = base.month - 1 + meses
        y, m = base.year + m // 12, m % 12 + 1
        dias_mes = [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30,
                    31, 31, 30, 31, 30, 31][m - 1]
        return base.replace(year=y, month=m, day=min(base.day, dias_mes)).strftime("%Y-%m-%d")
    return (base + timedelta(days=dias or 0)).strftime("%Y-%m-%d")


__all__ = [
    "URL_NOM024", "URL_NOM004", "URL_LGS",
    "FraccionVenta", "FraccionCofepris", "Categoria",
    "RequisitoNOM024", "REQUISITOS_NOM024",
    "MedicamentoControlado", "CATALOGO_MEDICAMENTOS_CONTROLADOS",
    "clasificar_medicamento", "calcular_vigencia_minima", "fecha_vencimiento_iso",
]
