"""Catálogos SAT vigentes para validar payloads de CFDI 4.0 antes de timbrar.

Origen: Anexo 20 de la Resolución Miscelánea Fiscal (vigente desde abr 2023).

⚠ Datos a verificar vigentes antes de producción:
- UsoCFDI: el SAT actualiza periódicamente. Validar contra el portal SAT
  o contra los catálogos que tu PAC publica.
- RegimenFiscal: 626 RESICO fue agregado en 2022; futuros regímenes podrían sumarse.
- TipoRelacion: estable desde 2017 pero validar.
- Motivos cancelación: 01-04 son los oficiales desde 2022.

Estructura: cada catálogo es un dict {clave: descripción} para listings legibles.
Las matrices de compatibilidad (ej. UsoCFDI × Régimen) se exponen aparte como funciones.
"""

from __future__ import annotations

# ---------- USO_CFDI (c_UsoCFDI) ----------

USO_CFDI: dict[str, str] = {
    "G01": "Adquisición de mercancías",
    "G02": "Devoluciones, descuentos o bonificaciones",
    "G03": "Gastos en general",
    "I01": "Construcciones",
    "I02": "Mobiliario y equipo de oficina por inversiones",
    "I03": "Equipo de transporte",
    "I04": "Equipo de cómputo y accesorios",
    "I05": "Dados, troqueles, moldes, matrices y herramental",
    "I06": "Comunicaciones telefónicas",
    "I07": "Comunicaciones satelitales",
    "I08": "Otra maquinaria y equipo",
    "D01": "Honorarios médicos, dentales y gastos hospitalarios",
    "D02": "Gastos médicos por incapacidad o discapacidad",
    "D03": "Gastos funerales",
    "D04": "Donativos",
    "D05": "Intereses reales pagados por créditos hipotecarios",
    "D06": "Aportaciones voluntarias al SAR",
    "D07": "Primas por seguros de gastos médicos",
    "D08": "Gastos de transportación escolar obligatoria",
    "D09": "Depósitos en cuentas para ahorro / pensiones",
    "D10": "Pagos por servicios educativos (colegiaturas)",
    "S01": "Sin efectos fiscales",
    "CP01": "Pagos (REP — complemento de pago)",
    "CN01": "Nómina",
}

# Usos que solo aplican a PF (deducciones personales Art. 151 LISR)
USO_CFDI_SOLO_PF = {"D01", "D02", "D03", "D05", "D06", "D07", "D08", "D09", "D10"}

# Usos obligatorios por tipo de comprobante
USO_CFDI_OBLIGATORIO_POR_TIPO: dict[str, str] = {
    "P": "CP01",
    "N": "CN01",
}


# ---------- FORMA_PAGO (c_FormaPago) ----------

FORMA_PAGO: dict[str, str] = {
    "01": "Efectivo",
    "02": "Cheque nominativo",
    "03": "Transferencia electrónica de fondos (SPEI)",
    "04": "Tarjeta de crédito",
    "05": "Monedero electrónico",
    "06": "Dinero electrónico",
    "08": "Vales de despensa",
    "12": "Dación en pago",
    "13": "Pago por subrogación",
    "14": "Pago por consignación",
    "15": "Condonación",
    "17": "Compensación",
    "23": "Novación",
    "24": "Confusión",
    "25": "Remisión de deuda",
    "26": "Prescripción o caducidad",
    "27": "A satisfacción del acreedor",
    "28": "Tarjeta de débito",
    "29": "Tarjeta de servicios",
    "30": "Aplicación de anticipos",
    "31": "Intermediario pagos",
    "99": "Por definir",
}


# ---------- METODO_PAGO (c_MetodoPago) ----------

METODO_PAGO: dict[str, str] = {
    "PUE": "Pago en una sola exhibición",
    "PPD": "Pago en parcialidades o diferido",
}


# ---------- TIPO_COMPROBANTE ----------

TIPO_COMPROBANTE: dict[str, str] = {
    "I": "Ingreso",
    "E": "Egreso (nota de crédito, devolución, bonificación)",
    "T": "Traslado (movimiento mercancía sin transferencia propiedad)",
    "N": "Nómina (requiere complemento Nómina 1.2)",
    "P": "Pago (complemento Pagos 2.0)",
}


# ---------- REGIMEN_FISCAL (c_RegimenFiscal) ----------

REGIMEN_FISCAL: dict[str, str] = {
    "601": "General de Ley Personas Morales",
    "603": "Personas Morales con Fines no Lucrativos",
    "605": "Sueldos y Salarios e Ingresos Asimilados a Salarios",
    "606": "Arrendamiento",
    "607": "Régimen de Enajenación o Adquisición de Bienes",
    "608": "Demás ingresos",
    "610": "Residentes en el Extranjero sin Establecimiento Permanente",
    "611": "Ingresos por Dividendos (socios y accionistas)",
    "612": "Personas Físicas con Actividades Empresariales y Profesionales (PFAE)",
    "614": "Ingresos por intereses",
    "615": "Régimen de obtención de premios",
    "616": "Sin obligaciones fiscales",
    "620": "Sociedades Cooperativas de Producción",
    "621": "Incorporación Fiscal (RIF) — sin nuevas altas desde 2022",
    "622": "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras",
    "623": "Opcional para Grupos de Sociedades",
    "624": "Coordinados (autotransporte)",
    "625": "Régimen de Actividades Empresariales con ingresos a través de Plataformas Tecnológicas",
    "626": "Régimen Simplificado de Confianza (RESICO)",
}

# Para validación tipo persona (regímenes que solo aplican a PF o PM)
REGIMEN_SOLO_PF = {"605", "606", "607", "608", "611", "612", "614", "615", "616", "621", "625"}
REGIMEN_SOLO_PM = {"601", "603", "620", "622", "623", "624"}
# 610 y 626 aplican a ambos (residentes extranjeros + RESICO PF/PM)


# ---------- OBJETO_IMP ----------

OBJETO_IMP: dict[str, str] = {
    "01": "No objeto del impuesto",
    "02": "Sí objeto del impuesto",
    "03": "Sí objeto del impuesto y no obligado al desglose",
    "04": "Sí objeto del impuesto y no causa impuesto",
}


# ---------- EXPORTACION ----------

EXPORTACION: dict[str, str] = {
    "01": "No aplica",
    "02": "Definitiva con clave A1",
    "03": "Temporal",
    "04": "Definitiva con clave distinta a A1 o sin pedimento",
}


# ---------- TIPO_RELACION (c_TipoRelacion) ----------

TIPO_RELACION: dict[str, str] = {
    "01": "Nota de crédito de los documentos relacionados",
    "02": "Nota de débito de los documentos relacionados",
    "03": "Devolución de mercancía sobre facturas o traslados previos",
    "04": "Sustitución de los CFDI previos",
    "05": "Traslados de mercancías facturados previamente",
    "06": "Factura generada por los traslados previos",
    "07": "CFDI por aplicación de anticipo",
}


# ---------- MOTIVOS_CANCELACION ----------

MOTIVOS_CANCELACION: dict[str, str] = {
    "01": "Comprobante emitido con errores con relación (requiere folio sustituto)",
    "02": "Comprobante emitido con errores sin relación",
    "03": "No se llevó a cabo la operación",
    "04": "Operación nominativa relacionada en una factura global",
}


# ---------- MONEDA (c_Moneda) ----------

MONEDA: dict[str, str] = {
    "MXN": "Peso Mexicano",
    "USD": "Dólar Estadounidense",
    "EUR": "Euro",
    "GBP": "Libra Esterlina",
    "JPY": "Yen Japonés",
    "CAD": "Dólar Canadiense",
    "CNY": "Yuan Chino",
    "XXX": "Sin denominación",
}


# ---------- CLAVE_UNIDAD más comunes ----------

CLAVE_UNIDAD_COMUNES: dict[str, str] = {
    "H87": "Pieza",
    "E48": "Unidad de servicio",
    "ACT": "Actividad",
    "KGM": "Kilogramo",
    "MTR": "Metro",
    "MTK": "Metro cuadrado",
    "MTQ": "Metro cúbico",
    "LTR": "Litro",
    "HUR": "Hora",
    "DAY": "Día",
    "MON": "Mes",
    "ANN": "Año",
}


# ---------- CLAVE_PROD_SERV patrones más usados (subset) ----------

# Este NO es el catálogo completo (52k+ claves) — son los más comunes por giro.
# Para uso productivo, complementar con catálogo completo del SAT.
CLAVE_PROD_SERV_COMUNES: dict[str, str] = {
    # Servicios profesionales
    "80141600": "Servicios de consultoría empresarial",
    "80111600": "Servicios de personal de tecnología de información",
    "80101500": "Servicios de consultoría gerencial",
    "81111500": "Servicios de programación de computadoras",
    "81111800": "Diseño y desarrollo de software",
    "82141500": "Servicios de mercadotecnia",
    "82101500": "Publicidad impresa",
    "82121500": "Servicios de diseño gráfico",
    "93151501": "Servicios de gestión de proyectos",
    # Salud
    "85121500": "Servicios de medicina",
    "85121600": "Servicios de psicología",
    "85121700": "Servicios de nutrición",
    "85121800": "Servicios odontológicos",
    # Educación
    "86111600": "Servicios de educación preescolar",
    "86111700": "Servicios de educación primaria",
    "86111800": "Servicios de educación secundaria",
    "86111900": "Servicios de profesional técnico",
    "86121500": "Servicios de educación profesional (bachillerato general)",
    "86131500": "Capacitación y entrenamiento",
    # Automotriz
    "25172500": "Refacciones y accesorios para vehículos automotores",
    "78180100": "Servicios de mantenimiento y reparación de vehículos",
    # Anticipo / venta global
    "84111506": "Servicios de facturación (anticipo / venta global)",
    "01010101": "No existe en el catálogo (uso especial venta global)",
}


# ---------- helpers de lookup ----------


def describe_uso_cfdi(clave: str) -> str | None:
    return USO_CFDI.get(clave)


def describe_forma_pago(clave: str) -> str | None:
    return FORMA_PAGO.get(clave)


def describe_metodo_pago(clave: str) -> str | None:
    return METODO_PAGO.get(clave)


def describe_regimen(clave: str) -> str | None:
    return REGIMEN_FISCAL.get(clave)


def describe_tipo_comprobante(clave: str) -> str | None:
    return TIPO_COMPROBANTE.get(clave)


def describe_motivo_cancelacion(clave: str) -> str | None:
    return MOTIVOS_CANCELACION.get(clave)


def regimen_compatible_con_tipo_persona(regimen: str, tipo: str) -> bool:
    """Verifica si un régimen aplica al tipo de persona (PF/PM).

    Retorna True si compatible (o si no hay restricción conocida).
    """
    tipo = tipo.upper()
    if regimen in REGIMEN_SOLO_PF:
        return tipo == "PF"
    if regimen in REGIMEN_SOLO_PM:
        return tipo == "PM"
    # Régimen acepta ambos (ej. 610, 626) o régimen no conocido
    return True


def uso_cfdi_compatible_con_persona(uso: str, tipo: str) -> bool:
    """Verifica si un UsoCFDI puede usarlo este tipo de persona.

    Los D0X solo aplican a PF (deducciones personales del Art. 151 LISR).
    """
    tipo = tipo.upper()
    if uso in USO_CFDI_SOLO_PF and tipo != "PF":
        return False
    return True
