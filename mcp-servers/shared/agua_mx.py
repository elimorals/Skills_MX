"""Catálogo unificado de organismos operadores de agua municipales/estatales.

Universo: 600+ organismos operadores en México. Este v1 cubre los 12 más
grandes que sirven ~50% de la población urbana mexicana.

Top organismos por cobertura poblacional:
  - SACMEX (CDMX) — 9.2M usuarios
  - SIAPA (Guadalajara/Zapopan) — 5M
  - SADM/AyDM (Monterrey ZMM) — 4.5M
  - OOMAPAS (Sonora) — 2.5M
  - JAPAC (Culiacán) — 1.2M
  - JAPAY/AGUAKAN (Cancún/Mérida + QRoo) — 2M
  - OAPAS (Tlalnepantla) — 700K
  - CESPT (Tijuana) — 1.9M
  - CEAS Guanajuato — 1.5M
  - CEA Querétaro — 1M
  - SAPAL (León) — 1.8M
  - INTERAPAS (San Luis Potosí) — 800K

Pago promedio bimestral: $200-800 MXN según consumo + plaza.
Frecuencia: bimestral (mayoría) o mensual (CDMX residencial, SIAPA comercial).

Cada organismo opera con su propio sistema — heterogeneidad MÁXIMA:
  - Portales web propios (no estándar)
  - Algunos integrados con ASP.NET, otros con PHP, otros SPA
  - Identificadores variados: cuenta, contrato, NIS, NDC, padrón, predio
  - Algunos requieren login, otros consulta pública con captcha
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


# Selectores reales descubiertos 2026-06-15 (Playwright) — SIAPA Guadalajara
URL_SIAPA_CONSULTA = "https://www.siapa.gob.mx/aplicaciones/pagoenlinea/"
URL_SIAPA_FORM_ACTION = "https://www.siapa.gob.mx/aplicaciones/pagoenlinea/busca_cta-sntdr.php"
SIAPA_FIELDS = {
    "cuenta_contrato": "cuenta_contrato",
    "clavesiapa": "clavesiapa",
}
# SIAPA usa reCAPTCHA v2 checkbox. site_key verificado en vivo:
SIAPA_RECAPTCHA_SITE_KEY = "6LdsJiUUAAAAAIjV_N2F3sd58XYDYznuyNn9ROva"

# SACMEX: portal con 503 dominical persistente (2026-06-15). Reintentar lunes.
URL_SACMEX_PORTAL = "https://www.sacmex.cdmx.gob.mx"


# Métodos de consulta soportados
MetodoConsulta = Literal[
    "publica",       # consulta directa con identificador
    "publica_captcha",  # consulta pública pero con CAPTCHA
    "login",         # requiere cuenta + password
    "indirecta",     # vía sistema estatal (CEAS/CEA)
    "no_implementado",
]


@dataclass
class OrganismoAgua:
    """Configuración de un organismo operador de agua mexicano."""
    clave: str                # "sacmex", "siapa", "sadm", etc.
    nombre_completo: str
    estado: str               # entidad federativa
    municipio: str            # municipio/ciudad principal (puede cubrir varios)
    url_portal: str
    url_consulta: str = ""    # endpoint específico de consulta
    identificador_label: str = "Cuenta"  # cómo se llama el ID en este portal
    identificador_regex: str = r"^\d{4,12}$"  # validación del ID
    metodo: MetodoConsulta = "publica"
    frecuencia_recibo: Literal["mensual", "bimestral"] = "bimestral"
    poblacion_aprox: int = 0  # usuarios cubiertos
    consultable: bool = False  # ¿está implementado consultar real?
    notas: str = ""


# Catálogo principal — orden por cobertura poblacional
CATALOGO_AGUA: list[OrganismoAgua] = [
    OrganismoAgua(
        clave="sacmex",
        nombre_completo="Sistema de Aguas de la Ciudad de México",
        estado="CDMX",
        municipio="Ciudad de México (16 alcaldías)",
        url_portal="https://sacmex.cdmx.gob.mx",
        url_consulta="https://aplicacionesgam.cdmx.gob.mx/AplicacionAguaCDMX/Captura/CapturaCuenta",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{2}-\d{2}-\d{3}-\d{3}-\d{1}$|^\d{11,12}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=9200000,
        consultable=True,
        notas="ASP.NET WebForms. Permite consulta sin login con cuenta predial.",
    ),
    OrganismoAgua(
        clave="siapa",
        nombre_completo="Sistema Intermunicipal de los Servicios de Agua Potable y Alcantarillado",
        estado="JAL",
        municipio="Guadalajara, Zapopan, Tlaquepaque, Tonalá, El Salto",
        url_portal="https://www.siapa.gob.mx",
        url_consulta="https://www.siapa.gob.mx/serviciosenlinea/consultarecibos",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{6,10}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=5000000,
        consultable=True,
        notas="Servicios en línea — cuenta de 6-10 dígitos. Tarjeta de plaza.",
    ),
    OrganismoAgua(
        clave="sadm",
        nombre_completo="Servicios de Agua y Drenaje de Monterrey",
        estado="NL",
        municipio="Monterrey, San Pedro, San Nicolás, Apodaca, Guadalupe, Escobedo, Cd. Juárez NL",
        url_portal="https://sadm.gob.mx",
        url_consulta="https://sadm.gob.mx/serviciosenlinea/",
        identificador_label="Contrato",
        identificador_regex=r"^\d{6,9}$",
        metodo="publica_captcha",
        frecuencia_recibo="bimestral",
        poblacion_aprox=4500000,
        consultable=True,
        notas="Captcha sencillo. Múltiples métodos: contrato, dirección, RFC.",
    ),
    OrganismoAgua(
        clave="cespt",
        nombre_completo="Comisión Estatal de Servicios Públicos de Tijuana",
        estado="BC",
        municipio="Tijuana, Tecate, Playas de Rosarito",
        url_portal="https://www.cespt.gob.mx",
        url_consulta="https://www.cespt.gob.mx/EnLinea/Adeudo.aspx",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{6,10}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1900000,
        consultable=True,
        notas="ASP.NET WebForms — consulta pública por cuenta.",
    ),
    OrganismoAgua(
        clave="sapal",
        nombre_completo="Sistema de Agua Potable y Alcantarillado de León",
        estado="GTO",
        municipio="León",
        url_portal="https://www.sapal.gob.mx",
        url_consulta="https://www.sapal.gob.mx/oficina-virtual",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{6,9}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1800000,
        consultable=True,
    ),
    OrganismoAgua(
        clave="ceaq",
        nombre_completo="Comisión Estatal de Aguas de Querétaro",
        estado="QRO",
        municipio="Querétaro y 18 municipios",
        url_portal="https://www.ceaqueretaro.gob.mx",
        url_consulta="https://www.ceaqueretaro.gob.mx/oficina-virtual",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{6,12}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1500000,
        consultable=True,
    ),
    OrganismoAgua(
        clave="ceasg",
        nombre_completo="Comisión Estatal del Agua Guanajuato",
        estado="GTO",
        municipio="Estado de Guanajuato (varios muns)",
        url_portal="https://ceag.guanajuato.gob.mx",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{4,12}$",
        metodo="indirecta",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1500000,
        consultable=False,
        notas="Sistema estatal — varía por municipio. No único.",
    ),
    OrganismoAgua(
        clave="japac",
        nombre_completo="Junta de Agua Potable y Alcantarillado del Mpio. de Culiacán",
        estado="SIN",
        municipio="Culiacán",
        url_portal="https://www.japac.gob.mx",
        url_consulta="https://www.japac.gob.mx/oficina-virtual",
        identificador_label="Contrato",
        identificador_regex=r"^\d{6,10}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1200000,
        consultable=True,
    ),
    OrganismoAgua(
        clave="japay",
        nombre_completo="Junta de Agua Potable y Alcantarillado de Yucatán",
        estado="YUC",
        municipio="Mérida y 100+ muns",
        url_portal="http://www.japay.gob.mx",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{4,9}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1000000,
        consultable=False,
        notas="Portal legacy — pendiente discovery exacto del endpoint.",
    ),
    OrganismoAgua(
        clave="aguakan",
        nombre_completo="Aguakan (Quintana Roo)",
        estado="QROO",
        municipio="Cancún, Playa del Carmen, Tulum, Isla Mujeres",
        url_portal="https://www.aguakan.com",
        url_consulta="https://www.aguakan.com/consulta-cuenta",
        identificador_label="Contrato",
        identificador_regex=r"^\d{6,10}$",
        metodo="publica",
        frecuencia_recibo="mensual",
        poblacion_aprox=1500000,
        consultable=True,
        notas="Concesionario privado — única integración tipo SaaS.",
    ),
    OrganismoAgua(
        clave="interapas",
        nombre_completo="Intermunicipal Metropolitano de Agua Potable, Alcantarillado, Saneamiento y Servicios Conexos",
        estado="SLP",
        municipio="San Luis Potosí, Soledad, Cerro de San Pedro",
        url_portal="https://www.interapas.gob.mx",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{6,10}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=800000,
        consultable=False,
    ),
    OrganismoAgua(
        clave="oapas",
        nombre_completo="Organismo de Agua Potable, Alcantarillado y Saneamiento de Tlalnepantla",
        estado="MEX",
        municipio="Tlalnepantla",
        url_portal="https://www.oapas.gob.mx",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{4,8}$",
        metodo="publica",
        frecuencia_recibo="bimestral",
        poblacion_aprox=700000,
        consultable=False,
        notas="❌ Discovery 2026-06-15: sin portal web público — solo Facebook + pago presencial.",
    ),
    # === D.2 Agua agregados 2026-06-15 ===
    OrganismoAgua(
        clave="jmas_juarez",
        nombre_completo="Junta Municipal de Agua y Saneamiento de Juárez",
        estado="CHIH",
        municipio="Ciudad Juárez",
        url_portal="https://jmasjuarez.gob.mx",
        url_consulta="https://jmasjuarez.gob.mx/v026/saldo.php",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{4,12}$",
        metodo="publica",
        frecuencia_recibo="mensual",
        poblacion_aprox=1500000,
        consultable=True,
        notas="✅ Discovery 2026-06-15: saldo.php público, input `cuenta`, sin captcha.",
    ),
    OrganismoAgua(
        clave="ooapas",
        nombre_completo="Organismo Operador de Agua Potable y Alcantarillado de Morelia",
        estado="MICH",
        municipio="Morelia",
        url_portal="https://www.ooapas.gob.mx",
        url_consulta="https://pagoenlinea.ooapas.gob.mx/index_pago_express.php",
        identificador_label="Folio del recibo",
        identificador_regex=r"^\d{6,16}$",
        metodo="publica",
        frecuencia_recibo="mensual",
        poblacion_aprox=750000,
        consultable=True,
        notas="✅ Discovery 2026-06-15: PagoExpress sin login, input `reciboFolio`, sin captcha.",
    ),
    OrganismoAgua(
        clave="cespm",
        nombre_completo="Comisión Estatal de Servicios Públicos de Mexicali",
        estado="BC",
        municipio="Mexicali",
        url_portal="https://www.cespm.gob.mx",
        url_consulta="https://www.ecespm.gob.mx/cespm-servlinea/iniciarsesion.aspx",
        identificador_label="Usuario registrado",
        identificador_regex=r"^.+$",
        metodo="login",
        frecuencia_recibo="bimestral",
        poblacion_aprox=1050000,
        consultable=False,
        notas="❌ Discovery 2026-06-15: ASP.NET con login obligatorio (sin path público).",
    ),
    OrganismoAgua(
        clave="aguah",
        nombre_completo="Agua de Hermosillo",
        estado="SON",
        municipio="Hermosillo",
        url_portal="https://aguadehermosillo.gob.mx",
        identificador_label="Cuenta",
        identificador_regex=r"^\d{4,12}$",
        metodo="publica",
        frecuencia_recibo="mensual",
        poblacion_aprox=936000,
        consultable=False,
        notas="❌ Discovery 2026-06-15: sin portal web — consulta solo vía app móvil 'mi aguah'.",
    ),
    OrganismoAgua(
        clave="simas_saltillo",
        nombre_completo="Aguas de Saltillo (SIMAS)",
        estado="COAH",
        municipio="Saltillo",
        url_portal="https://www.aguasdesaltillo.com",
        url_consulta="https://oficina.aguasdesaltillo.com/#/main",
        identificador_label="Usuario registrado",
        identificador_regex=r"^.+$",
        metodo="login",
        frecuencia_recibo="mensual",
        poblacion_aprox=880000,
        consultable=False,
        notas="❌ Discovery 2026-06-15: Oficina Virtual SPA con login obligatorio.",
    ),
]


def buscar_organismo(clave: str) -> Optional[OrganismoAgua]:
    """Busca un organismo por clave canónica (case-insensitive)."""
    clave_norm = clave.strip().lower()
    for org in CATALOGO_AGUA:
        if org.clave == clave_norm:
            return org
    return None


def listar_organismos(solo_consultables: bool = False) -> list[OrganismoAgua]:
    """Lista todos los organismos en el catálogo."""
    if solo_consultables:
        return [o for o in CATALOGO_AGUA if o.consultable]
    return list(CATALOGO_AGUA)


def buscar_por_estado(estado: str) -> list[OrganismoAgua]:
    """Lista organismos que cubren un estado."""
    estado_norm = estado.strip().upper()
    return [o for o in CATALOGO_AGUA if o.estado.upper() == estado_norm]


def estadisticas() -> dict:
    """Stats agregadas del catálogo."""
    total = len(CATALOGO_AGUA)
    consultables = sum(1 for o in CATALOGO_AGUA if o.consultable)
    pob_total = sum(o.poblacion_aprox for o in CATALOGO_AGUA)
    pob_consultable = sum(o.poblacion_aprox for o in CATALOGO_AGUA if o.consultable)
    return {
        "total_organismos": total,
        "consultables": consultables,
        "no_consultables_aun": total - consultables,
        "poblacion_total_cubierta": pob_total,
        "poblacion_consultable_aprox": pob_consultable,
        "porcentaje_pob_nacional_consultable": round(pob_consultable / 130_000_000 * 100, 1),
    }


__all__ = [
    "OrganismoAgua",
    "MetodoConsulta",
    "CATALOGO_AGUA",
    "buscar_organismo",
    "listar_organismos",
    "buscar_por_estado",
    "estadisticas",
]
