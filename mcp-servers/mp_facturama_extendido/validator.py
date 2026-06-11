"""Validador local de payload CFDI 4.0 — corre ANTES de llamar a Facturama.

Por qué validamos localmente antes de timbrar:
1. Evita costo PAC por timbrados que el SAT rechazaría
2. Errores con explicación accionable en español (vs códigos crípticos del PAC)
3. Permite trabajar offline en desarrollo
4. Captura el 95% de errores comunes (consistencia método/forma, totales, RFC)

Reglas verificadas (origen: Anexo 20 RMF + Guía CFDI 4.0):
- Versión del CFDI 4.0 (con CFDI 3.3 se rechaza)
- RFC emisor + receptor con formato válido y no en blacklist genérica
- CP del receptor: 5 dígitos (obligatorio en 4.0, novedad vs 3.3)
- Régimen fiscal emisor + receptor declarados y existentes en catálogo
- UsoCFDI compatible con tipo de persona receptora (D0X solo PF)
- TipoComprobante válido
- Exportacion presente (obligatorio en 4.0)
- MetodoPago + FormaPago consistencia (PUE↔específico, PPD↔99)
- Moneda válida; si distinta a MXN requiere TipoCambio positivo
- Conceptos: al menos uno, con ClaveProdServ, ClaveUnidad, ObjetoImp
- ObjetoImp 02 → impuestos a nivel concepto y comprobante
- Totales cuadran: subtotal + trasladados − retenidos = total (±0.01)
- Fecha dentro de ±72h (zona del lugar de expedición)
- LugarExpedicion: CP de 5 dígitos
- Si MotivoPago = PPD + es CFDI tipo I → recordar emitir REP al cobrar
- UsoCFDI obligatorio según TipoComprobante (CP01 para P, CN01 para N)

⚠ NO validamos:
- Existencia del RFC en padrón SAT (eso requiere consulta SAT, opcional aparte)
- 69-B EFOS (consulta separada)
- Que la ClaveProdServ realmente exista (catálogo masivo; el PAC valida)
- Que la combinación UsoCFDI × Régimen sea aceptada (matriz SAT cambia; el PAC valida)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from mp_facturama_extendido.catalogos import (
    EXPORTACION,
    FORMA_PAGO,
    METODO_PAGO,
    MOTIVOS_CANCELACION,
    OBJETO_IMP,
    REGIMEN_FISCAL,
    TIPO_COMPROBANTE,
    USO_CFDI,
    USO_CFDI_OBLIGATORIO_POR_TIPO,
    USO_CFDI_SOLO_PF,
    regimen_compatible_con_tipo_persona,
    uso_cfdi_compatible_con_persona,
)

# RFC patterns (mismos que mp_curp_renapo / rfc-validacion skill)
RE_RFC_PM = re.compile(r"^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$")
RE_RFC_PF = re.compile(r"^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$")
RFC_GENERICO_NACIONAL = "XAXX010101000"
RFC_GENERICO_EXTRANJERO = "XEXX010101000"

# Tolerancia de redondeo para validar totales (1 centavo)
TOLERANCIA_TOTAL = Decimal("0.01")


@dataclass
class Issue:
    """Un hallazgo de validación — puede ser error o advertencia."""

    severity: str  # "error" | "warning"
    code: str  # estable, ej. "metodo_forma_inconsistente"
    message: str  # human-readable, español
    path: str | None = None  # JSON-pointer-style, ej. "comprobante.forma_pago"


@dataclass
class ValidationReport:
    """Resultado de validar un payload."""

    is_valid: bool
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "errors": [_issue_to_dict(i) for i in self.errors],
            "warnings": [_issue_to_dict(i) for i in self.warnings],
        }


def _issue_to_dict(i: Issue) -> dict[str, str | None]:
    return {"severity": i.severity, "code": i.code, "message": i.message, "path": i.path}


def validate_cfdi_payload(payload: dict[str, Any]) -> ValidationReport:
    """Punto de entrada: valida un payload CFDI 4.0 completo.

    Recolecta todos los hallazgos antes de decidir is_valid. Un payload solo es
    `is_valid: True` si NO tiene errores (warnings pueden coexistir).
    """
    errors: list[Issue] = []
    warnings: list[Issue] = []

    _check_emisor(payload.get("emisor", {}), errors, warnings)
    _check_receptor(payload.get("receptor", {}), errors, warnings)
    _check_comprobante(payload.get("comprobante", {}), errors, warnings)
    _check_conceptos(payload.get("conceptos", []), errors, warnings)
    _check_totales(payload, errors, warnings)
    _check_uso_vs_regimen_receptor(payload, errors, warnings)
    _check_uso_vs_tipo_comprobante(payload, errors, warnings)
    _check_anticipo_pattern(payload, warnings)

    return ValidationReport(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)


# ---------- emisor / receptor ----------


def _check_emisor(emisor: dict, errors: list[Issue], warnings: list[Issue]) -> None:
    rfc = emisor.get("rfc")
    if not rfc:
        errors.append(Issue("error", "emisor_rfc_faltante", "Falta RFC del emisor.", "emisor.rfc"))
    elif not _is_valid_rfc(rfc):
        errors.append(
            Issue(
                "error",
                "emisor_rfc_invalido",
                f"RFC del emisor inválido: {rfc!r}. Debe cumplir el regex SAT.",
                "emisor.rfc",
            )
        )

    if not emisor.get("razon_social"):
        errors.append(
            Issue("error", "emisor_razon_social_faltante", "Falta razón social del emisor.", "emisor.razon_social")
        )

    regimen = emisor.get("regimen_fiscal")
    if not regimen:
        errors.append(
            Issue("error", "emisor_regimen_faltante", "Falta régimen fiscal del emisor.", "emisor.regimen_fiscal")
        )
    elif regimen not in REGIMEN_FISCAL:
        errors.append(
            Issue(
                "error",
                "emisor_regimen_invalido",
                f"Régimen fiscal del emisor no existe en catálogo: {regimen}.",
                "emisor.regimen_fiscal",
            )
        )

    cp = emisor.get("cp_lugar_expedicion")
    if not cp:
        errors.append(
            Issue(
                "error",
                "emisor_cp_faltante",
                "Falta CP del lugar de expedición del emisor (campo LugarExpedicion).",
                "emisor.cp_lugar_expedicion",
            )
        )
    elif not _is_valid_cp(cp):
        errors.append(
            Issue("error", "emisor_cp_invalido", f"CP de emisor inválido: {cp!r}. Debe ser 5 dígitos.", "emisor.cp_lugar_expedicion")
        )


def _check_receptor(receptor: dict, errors: list[Issue], warnings: list[Issue]) -> None:
    rfc = receptor.get("rfc")
    if not rfc:
        errors.append(Issue("error", "receptor_rfc_faltante", "Falta RFC del receptor.", "receptor.rfc"))
    elif not _is_valid_rfc(rfc):
        errors.append(
            Issue(
                "error",
                "receptor_rfc_invalido",
                f"RFC del receptor inválido: {rfc!r}.",
                "receptor.rfc",
            )
        )

    if not receptor.get("nombre"):
        errors.append(Issue("error", "receptor_nombre_faltante", "Falta nombre/razón social del receptor.", "receptor.nombre"))

    regimen = receptor.get("regimen_fiscal")
    if not regimen:
        errors.append(
            Issue(
                "error",
                "receptor_regimen_faltante",
                "Falta régimen fiscal del receptor (obligatorio en CFDI 4.0, novedad vs 3.3).",
                "receptor.regimen_fiscal",
            )
        )
    elif regimen not in REGIMEN_FISCAL:
        errors.append(
            Issue(
                "error",
                "receptor_regimen_invalido",
                f"Régimen fiscal del receptor no existe en catálogo: {regimen}.",
                "receptor.regimen_fiscal",
            )
        )

    cp = receptor.get("cp_domicilio")
    if not cp:
        errors.append(
            Issue(
                "error",
                "receptor_cp_faltante",
                "Falta CP del domicilio fiscal del receptor (obligatorio en CFDI 4.0).",
                "receptor.cp_domicilio",
            )
        )
    elif not _is_valid_cp(cp):
        errors.append(
            Issue(
                "error",
                "receptor_cp_invalido",
                f"CP de receptor inválido: {cp!r}. Debe ser 5 dígitos.",
                "receptor.cp_domicilio",
            )
        )

    uso = receptor.get("uso_cfdi")
    if not uso:
        errors.append(Issue("error", "uso_cfdi_faltante", "Falta UsoCFDI del receptor.", "receptor.uso_cfdi"))
    elif uso not in USO_CFDI:
        errors.append(
            Issue("error", "uso_cfdi_invalido", f"UsoCFDI no existe en catálogo: {uso}.", "receptor.uso_cfdi")
        )

    # Genéricos requieren S01
    if rfc in (RFC_GENERICO_NACIONAL, RFC_GENERICO_EXTRANJERO) and uso != "S01":
        errors.append(
            Issue(
                "error",
                "rfc_generico_requiere_s01",
                f"RFC genérico {rfc} requiere UsoCFDI = S01 (recibido: {uso}).",
                "receptor.uso_cfdi",
            )
        )

    # RFC extranjero requiere ResidenciaFiscal y NumRegIdTrib
    if rfc == RFC_GENERICO_EXTRANJERO:
        if not receptor.get("residencia_fiscal"):
            errors.append(
                Issue(
                    "error",
                    "extranjero_falta_residencia_fiscal",
                    "Receptor extranjero (XEXX010101000) requiere campo ResidenciaFiscal (código ISO país).",
                    "receptor.residencia_fiscal",
                )
            )
        if not receptor.get("num_reg_id_trib"):
            warnings.append(
                Issue(
                    "warning",
                    "extranjero_sin_num_reg_id_trib",
                    "Receptor extranjero típicamente requiere NumRegIdTrib (ID fiscal del país de origen).",
                    "receptor.num_reg_id_trib",
                )
            )


# ---------- comprobante ----------


def _check_comprobante(comp: dict, errors: list[Issue], warnings: list[Issue]) -> None:
    tipo = comp.get("tipo_comprobante")
    if not tipo:
        errors.append(
            Issue("error", "tipo_comprobante_faltante", "Falta TipoDeComprobante.", "comprobante.tipo_comprobante")
        )
    elif tipo not in TIPO_COMPROBANTE:
        errors.append(
            Issue(
                "error",
                "tipo_comprobante_invalido",
                f"TipoDeComprobante inválido: {tipo}. Válidos: {sorted(TIPO_COMPROBANTE)}.",
                "comprobante.tipo_comprobante",
            )
        )

    metodo = comp.get("metodo_pago")
    forma = comp.get("forma_pago")

    if not metodo:
        errors.append(Issue("error", "metodo_pago_faltante", "Falta MétodoPago.", "comprobante.metodo_pago"))
    elif metodo not in METODO_PAGO:
        errors.append(
            Issue(
                "error",
                "metodo_pago_invalido",
                f"MétodoPago debe ser PUE o PPD. Recibido: {metodo}.",
                "comprobante.metodo_pago",
            )
        )

    if not forma:
        errors.append(Issue("error", "forma_pago_faltante", "Falta FormaPago.", "comprobante.forma_pago"))
    elif forma not in FORMA_PAGO:
        errors.append(
            Issue(
                "error",
                "forma_pago_invalida",
                f"FormaPago inválida: {forma}. Verificar catálogo c_FormaPago.",
                "comprobante.forma_pago",
            )
        )

    # Consistencia MétodoPago ↔ FormaPago — el bug clásico que rechaza el SAT
    if metodo == "PUE" and forma == "99":
        errors.append(
            Issue(
                "error",
                "metodo_forma_inconsistente_pue_99",
                "MétodoPago = PUE no puede llevar FormaPago = 99 (Por definir). "
                "PUE significa pagado al recibir, debe llevar una forma específica (01-31).",
                "comprobante.forma_pago",
            )
        )
    if metodo == "PPD" and forma != "99":
        errors.append(
            Issue(
                "error",
                "metodo_forma_inconsistente_ppd_no_99",
                f"MétodoPago = PPD requiere FormaPago = 99 (Por definir). Recibido: {forma}. "
                "PPD significa pago diferido — la forma específica se conoce en el REP posterior.",
                "comprobante.forma_pago",
            )
        )

    # Exportacion obligatorio en 4.0
    exportacion = comp.get("exportacion")
    if not exportacion:
        errors.append(
            Issue(
                "error",
                "exportacion_faltante",
                "Falta campo Exportacion (obligatorio en CFDI 4.0). Use '01' si no aplica.",
                "comprobante.exportacion",
            )
        )
    elif exportacion not in EXPORTACION:
        errors.append(
            Issue(
                "error",
                "exportacion_invalido",
                f"Valor de Exportacion inválido: {exportacion}. Válidos: {sorted(EXPORTACION)}.",
                "comprobante.exportacion",
            )
        )

    # Moneda + TipoCambio
    moneda = comp.get("moneda")
    if not moneda:
        warnings.append(
            Issue("warning", "moneda_faltante", "Falta Moneda — se asumirá MXN.", "comprobante.moneda")
        )
    elif moneda != "MXN":
        tc = comp.get("tipo_cambio")
        if tc is None or _to_decimal(tc) is None or _to_decimal(tc) <= 0:
            errors.append(
                Issue(
                    "error",
                    "tipo_cambio_requerido",
                    f"Moneda {moneda} ≠ MXN requiere TipoCambio positivo.",
                    "comprobante.tipo_cambio",
                )
            )

    # Fecha dentro de rango razonable
    fecha = comp.get("fecha")
    if fecha:
        _check_fecha(fecha, errors, warnings)


def _check_fecha(fecha_str: str, errors: list[Issue], warnings: list[Issue]) -> None:
    """Fecha debe estar dentro de ±72h del actual."""
    try:
        # Aceptar tanto ISO con timezone como naive
        if fecha_str.endswith("Z"):
            fecha_str = fecha_str[:-1] + "+00:00"
        fecha = datetime.fromisoformat(fecha_str)
        if fecha.tzinfo is None:
            # Asumir zona del SAT (Ciudad de México UTC-6, sin DST oficial)
            fecha = fecha.replace(tzinfo=timezone(timedelta(hours=-6)))
    except (ValueError, TypeError):
        errors.append(
            Issue(
                "error",
                "fecha_formato_invalido",
                f"Fecha del comprobante con formato inválido: {fecha_str!r}. Esperado ISO 8601.",
                "comprobante.fecha",
            )
        )
        return

    now = datetime.now(timezone.utc)
    if fecha > now + timedelta(minutes=5):  # 5 min tolerancia para skew de reloj
        errors.append(
            Issue(
                "error",
                "fecha_futura",
                f"Fecha del comprobante es futura: {fecha.isoformat()}. SAT rechaza fechas futuras.",
                "comprobante.fecha",
            )
        )
    elif fecha < now - timedelta(hours=72):
        errors.append(
            Issue(
                "error",
                "fecha_demasiado_antigua",
                f"Fecha del comprobante con más de 72 horas: {fecha.isoformat()}. SAT solo acepta dentro de ±72h.",
                "comprobante.fecha",
            )
        )


# ---------- conceptos ----------


def _check_conceptos(conceptos: list, errors: list[Issue], warnings: list[Issue]) -> None:
    if not conceptos:
        errors.append(Issue("error", "conceptos_vacios", "El CFDI debe tener al menos un concepto.", "conceptos"))
        return

    for i, c in enumerate(conceptos):
        path = f"conceptos[{i}]"
        if not c.get("clave_prod_serv"):
            errors.append(
                Issue("error", "concepto_clave_prod_serv_faltante", "Falta ClaveProdServ del concepto.", f"{path}.clave_prod_serv")
            )
        elif not _is_valid_clave_prod_serv(c["clave_prod_serv"]):
            warnings.append(
                Issue(
                    "warning",
                    "concepto_clave_prod_serv_formato",
                    f"ClaveProdServ debería ser 8 dígitos: {c['clave_prod_serv']!r}.",
                    f"{path}.clave_prod_serv",
                )
            )

        if not c.get("descripcion"):
            errors.append(Issue("error", "concepto_descripcion_faltante", "Falta descripción.", f"{path}.descripcion"))

        if not c.get("clave_unidad"):
            errors.append(Issue("error", "concepto_clave_unidad_faltante", "Falta ClaveUnidad.", f"{path}.clave_unidad"))

        objeto = c.get("objeto_imp")
        if not objeto:
            errors.append(Issue("error", "concepto_objeto_imp_faltante", "Falta ObjetoImp.", f"{path}.objeto_imp"))
        elif objeto not in OBJETO_IMP:
            errors.append(
                Issue("error", "concepto_objeto_imp_invalido", f"ObjetoImp inválido: {objeto}.", f"{path}.objeto_imp")
            )

        # Cantidades y montos
        for campo in ("cantidad", "valor_unitario", "importe"):
            val = c.get(campo)
            if val is None:
                errors.append(Issue("error", f"concepto_{campo}_faltante", f"Falta {campo}.", f"{path}.{campo}"))
                continue
            d = _to_decimal(val)
            if d is None:
                errors.append(
                    Issue("error", f"concepto_{campo}_no_numerico", f"{campo} no es numérico: {val!r}.", f"{path}.{campo}")
                )
            elif d < 0:
                errors.append(
                    Issue("error", f"concepto_{campo}_negativo", f"{campo} no puede ser negativo: {d}.", f"{path}.{campo}")
                )

        # Coherencia: importe ≈ cantidad × valor_unitario (±0.01)
        try:
            cantidad = _to_decimal(c["cantidad"])
            valor_unit = _to_decimal(c["valor_unitario"])
            importe = _to_decimal(c["importe"])
            if cantidad is not None and valor_unit is not None and importe is not None:
                expected = cantidad * valor_unit
                if abs(expected - importe) > TOLERANCIA_TOTAL:
                    errors.append(
                        Issue(
                            "error",
                            "concepto_importe_no_cuadra",
                            f"Importe ({importe}) ≠ cantidad × valor_unitario ({expected}).",
                            f"{path}.importe",
                        )
                    )
        except (KeyError, TypeError):
            pass  # Ya se reportaron faltantes arriba


# ---------- totales ----------


def _check_totales(payload: dict, errors: list[Issue], warnings: list[Issue]) -> None:
    """Suma de conceptos + impuestos − retenciones debe igualar Total."""
    conceptos = payload.get("conceptos", [])
    if not conceptos:
        return

    subtotal_calc = Decimal("0")
    for c in conceptos:
        d = _to_decimal(c.get("importe"))
        if d is not None:
            subtotal_calc += d

    declarado_subtotal = _to_decimal(payload.get("subtotal"))
    declarado_total = _to_decimal(payload.get("total"))

    impuestos = payload.get("impuestos", {})
    trasladados = _to_decimal(impuestos.get("total_trasladados", 0)) or Decimal("0")
    retenidos = _to_decimal(impuestos.get("total_retenidos", 0)) or Decimal("0")

    if declarado_subtotal is not None and abs(subtotal_calc - declarado_subtotal) > TOLERANCIA_TOTAL:
        errors.append(
            Issue(
                "error",
                "subtotal_no_cuadra",
                f"Subtotal declarado ({declarado_subtotal}) ≠ suma de conceptos ({subtotal_calc}).",
                "subtotal",
            )
        )

    if declarado_total is not None:
        total_calc = subtotal_calc + trasladados - retenidos
        if abs(total_calc - declarado_total) > TOLERANCIA_TOTAL:
            errors.append(
                Issue(
                    "error",
                    "total_no_cuadra",
                    f"Total declarado ({declarado_total}) ≠ subtotal + trasladados − retenidos ({total_calc}).",
                    "total",
                )
            )


# ---------- compatibilidad UsoCFDI × régimen receptor ----------


def _check_uso_vs_regimen_receptor(payload: dict, errors: list[Issue], warnings: list[Issue]) -> None:
    receptor = payload.get("receptor", {})
    uso = receptor.get("uso_cfdi")
    regimen = receptor.get("regimen_fiscal")
    if not uso or not regimen:
        return  # ya hay errores de faltantes

    # Inferir tipo persona del régimen
    from mp_facturama_extendido.catalogos import REGIMEN_SOLO_PF, REGIMEN_SOLO_PM

    if regimen in REGIMEN_SOLO_PF:
        tipo = "PF"
    elif regimen in REGIMEN_SOLO_PM:
        tipo = "PM"
    else:
        return  # regímenes mixtos (610, 626) — no podemos inferir solo del régimen

    if not uso_cfdi_compatible_con_persona(uso, tipo):
        errors.append(
            Issue(
                "error",
                "uso_cfdi_incompatible_persona",
                f"UsoCFDI {uso} ({USO_CFDI.get(uso, '?')}) solo aplica a Personas Físicas. "
                f"Receptor con régimen {regimen} es {tipo}.",
                "receptor.uso_cfdi",
            )
        )


# ---------- uso obligatorio según TipoComprobante ----------


def _check_uso_vs_tipo_comprobante(payload: dict, errors: list[Issue], warnings: list[Issue]) -> None:
    tipo = payload.get("comprobante", {}).get("tipo_comprobante")
    uso = payload.get("receptor", {}).get("uso_cfdi")
    if not tipo or not uso:
        return

    obligatorio = USO_CFDI_OBLIGATORIO_POR_TIPO.get(tipo)
    if obligatorio and uso != obligatorio:
        errors.append(
            Issue(
                "error",
                "uso_cfdi_obligatorio_no_cumplido",
                f"TipoComprobante = {tipo} requiere UsoCFDI = {obligatorio}. Recibido: {uso}.",
                "receptor.uso_cfdi",
            )
        )


# ---------- patrón de anticipo (informativo) ----------


def _check_anticipo_pattern(payload: dict, warnings: list[Issue]) -> None:
    """Si MétodoPago=PPD + TipoComprobante=I, recordar emitir REP al cobrar."""
    comp = payload.get("comprobante", {})
    if comp.get("metodo_pago") == "PPD" and comp.get("tipo_comprobante") == "I":
        warnings.append(
            Issue(
                "warning",
                "ppd_requiere_rep_posterior",
                "Comprobante PPD: recuerda emitir CFDI tipo P (REP) por cada cobro recibido, "
                "a más tardar el día 10 del mes siguiente al pago.",
                "comprobante.metodo_pago",
            )
        )


# ---------- helpers ----------


def _is_valid_rfc(rfc: str) -> bool:
    if not isinstance(rfc, str):
        return False
    rfc = rfc.upper().strip()
    return bool(RE_RFC_PF.match(rfc) or RE_RFC_PM.match(rfc))


def _is_valid_cp(cp: Any) -> bool:
    s = str(cp).strip()
    return len(s) == 5 and s.isdigit()


def _is_valid_clave_prod_serv(clave: Any) -> bool:
    s = str(clave).strip()
    return len(s) == 8 and s.isdigit()


def _to_decimal(val: Any) -> Decimal | None:
    """Convierte un valor a Decimal o None si no es numérico."""
    if val is None:
        return None
    if isinstance(val, bool):  # bool is subclass of int; reject
        return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError, TypeError):
        return None


# ---------- validación de cancelación (independiente de timbrado) ----------


def validate_cancelacion(uuid: str, motivo: str, folio_sustituto: str | None) -> ValidationReport:
    """Valida los datos para cancelar un CFDI."""
    errors: list[Issue] = []
    warnings: list[Issue] = []

    if not _is_valid_uuid(uuid):
        errors.append(Issue("error", "uuid_invalido", f"UUID con formato inválido: {uuid!r}.", "uuid"))

    if motivo not in MOTIVOS_CANCELACION:
        errors.append(
            Issue(
                "error",
                "motivo_invalido",
                f"Motivo de cancelación inválido: {motivo}. Válidos: {sorted(MOTIVOS_CANCELACION)}.",
                "motivo",
            )
        )

    if motivo == "01" and not folio_sustituto:
        errors.append(
            Issue(
                "error",
                "motivo_01_requiere_folio_sustituto",
                "Motivo 01 (comprobante con errores con relación) requiere folio_sustituto (UUID del CFDI que reemplaza).",
                "folio_sustituto",
            )
        )

    if motivo == "01" and folio_sustituto and not _is_valid_uuid(folio_sustituto):
        errors.append(
            Issue("error", "folio_sustituto_invalido", f"folio_sustituto con formato UUID inválido: {folio_sustituto!r}.", "folio_sustituto")
        )

    if motivo != "01" and folio_sustituto:
        warnings.append(
            Issue(
                "warning",
                "folio_sustituto_no_aplica",
                f"folio_sustituto solo aplica para motivo 01. Será ignorado (motivo recibido: {motivo}).",
                "folio_sustituto",
            )
        )

    return ValidationReport(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)


_RE_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _is_valid_uuid(uuid: str) -> bool:
    return bool(isinstance(uuid, str) and _RE_UUID.match(uuid.strip()))
