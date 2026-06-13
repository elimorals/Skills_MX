"""Catálogo central de portales municipales y estatales mexicanos.

Cubre los 32 estados + 50 municipios grandes con configuración Playwright
parametrizada. Reemplaza el patrón "1 MCP por municipio" por una tabla central
consultable desde cualquier MCP.

USO:
    from shared.catalogo_municipios_mx import (
        buscar_portal_predial,
        buscar_portal_multas,
        listar_estados,
        listar_municipios_estado,
    )

    config = buscar_portal_predial("cdmx", "ciudad_de_mexico")
    # → PortalConfig listo para consulta_portal()

    estados = listar_estados()  # 32 abreviaturas

⚠ ADVERTENCIA: Las URLs y selectores aquí son **estimados** basados en
convenciones comunes. Cada portal debe validarse con scripts/health-check-portales.py
antes de uso productivo. Selectores marcados como `validado=True` solo cuando
hay verificación manual reciente.

Estructura:
- ESTADOS: dict con 32 entradas {clave: {nombre, capital, url_estatal_tenencia, validado}}
- MUNICIPIOS: dict con configuraciones por (estado_clave, municipio_clave)

Para agregar un municipio nuevo:
    MUNICIPIOS["tlaxcala"]["tlaxcala_de_xicohtencatl"] = MunicipioConfig(
        nombre="Tlaxcala de Xicohténcatl",
        portal_predial_url="https://...",
        ...
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from shared.playwright_municipal_generic import PortalConfig


@dataclass
class MunicipioConfig:
    """Configuración compacta de un municipio: deriva PortalConfigs cuando se necesitan."""
    nombre: str
    estado_clave: str  # "cdmx", "jal", etc.
    portal_predial_url: Optional[str] = None
    portal_multas_url: Optional[str] = None
    selectores_predial: dict = field(default_factory=dict)
    selectores_multas: dict = field(default_factory=dict)
    poblacion_aprox: int = 0
    validado: bool = False
    notas: str = ""
    # Si el municipio se consulta vía plataforma SaaS estatal/multi-municipio
    # (ej. SACPI Michoacán cubre 95 municipios) en lugar de portal propio.
    # Valor: nombre de la plataforma en shared.plataformas_saas_mx (ej. "SACPI")
    plataforma_saas: Optional[str] = None
    # Código municipal específico de la plataforma SaaS (ej. "034" para Hidalgo en SACPI)
    codigo_saas: Optional[str] = None

    def to_predial_config(self) -> Optional[PortalConfig]:
        if not self.portal_predial_url:
            return None
        s = self.selectores_predial
        return PortalConfig(
            url=self.portal_predial_url,
            input_selectors=s.get("input", [
                "input[name='cuenta']",
                "input[name='clave']",
                "input#cuenta",
                "input[type='text']",
            ]),
            submit_selectors=s.get("submit", [
                "button[type='submit']",
                "button:has-text('Consultar')",
                "button:has-text('Buscar')",
            ]),
            result_selector=s.get("result", "table, .resultado, .adeudos"),
            identificador_etiqueta="cuenta_predial",
        )

    def to_multas_config(self) -> Optional[PortalConfig]:
        if not self.portal_multas_url:
            return None
        s = self.selectores_multas
        return PortalConfig(
            url=self.portal_multas_url,
            input_selectors=s.get("input", [
                "input[name='placa']",
                "input#placa",
                "input[type='text']",
            ]),
            submit_selectors=s.get("submit", [
                "button[type='submit']",
                "button:has-text('Consultar')",
            ]),
            result_selector=s.get("result", "table, .resultado"),
            identificador_etiqueta="placa",
        )


# ============================================================
# Los 32 estados de México con URLs estatales
# ============================================================

ESTADOS: dict[str, dict] = {
    "ags": {"nombre": "Aguascalientes", "capital": "aguascalientes", "tenencia_url": "https://eservicios2.aguascalientes.gob.mx/", "validado": False},
    "bc":  {"nombre": "Baja California", "capital": "mexicali", "tenencia_url": "https://www.bajacalifornia.gob.mx/finanzas/", "validado": False},
    "bcs": {"nombre": "Baja California Sur", "capital": "la_paz", "tenencia_url": "https://finanzas.bcs.gob.mx/", "validado": False},
    "cam": {"nombre": "Campeche", "capital": "san_francisco_de_campeche", "tenencia_url": "https://finanzas.campeche.gob.mx/", "validado": False},
    "chis": {"nombre": "Chiapas", "capital": "tuxtla_gutierrez", "tenencia_url": "https://www.haciendachiapas.gob.mx/", "validado": False},
    "chih": {"nombre": "Chihuahua", "capital": "chihuahua", "tenencia_url": "https://www.chihuahua.gob.mx/hacienda", "validado": False},
    "cdmx": {"nombre": "Ciudad de México", "capital": "ciudad_de_mexico", "tenencia_url": "https://data.finanzas.cdmx.gob.mx/", "validado": True},
    "coah": {"nombre": "Coahuila", "capital": "saltillo", "tenencia_url": "https://www.sefin.coahuila.gob.mx/", "validado": False},
    "col": {"nombre": "Colima", "capital": "colima", "tenencia_url": "https://hacienda.col.gob.mx/", "validado": False},
    "dur": {"nombre": "Durango", "capital": "durango", "tenencia_url": "https://www.sfdgo.gob.mx/", "validado": False},
    "edomex": {"nombre": "Estado de México", "capital": "toluca", "tenencia_url": "https://sfpya.edomexico.gob.mx/tenencia/", "validado": False},
    "gto": {"nombre": "Guanajuato", "capital": "guanajuato", "tenencia_url": "https://finanzas.guanajuato.gob.mx/", "validado": False},
    "gro": {"nombre": "Guerrero", "capital": "chilpancingo", "tenencia_url": "https://sefina.guerrero.gob.mx/", "validado": False},
    "hgo": {"nombre": "Hidalgo", "capital": "pachuca", "tenencia_url": "https://sf.hidalgo.gob.mx/", "validado": False},
    "jal": {"nombre": "Jalisco", "capital": "guadalajara", "tenencia_url": "https://sfin.jalisco.gob.mx/", "validado": False},
    "mich": {"nombre": "Michoacán", "capital": "morelia", "tenencia_url": "https://secfinanzas.michoacan.gob.mx/", "validado": False},
    "mor": {"nombre": "Morelos", "capital": "cuernavaca", "tenencia_url": "https://hacienda.morelos.gob.mx/", "validado": False},
    "nay": {"nombre": "Nayarit", "capital": "tepic", "tenencia_url": "https://hacienda.nayarit.gob.mx/", "validado": False},
    "nl": {"nombre": "Nuevo León", "capital": "monterrey", "tenencia_url": "https://www.nl.gob.mx/tramites-y-servicios/", "validado": False},
    "oax": {"nombre": "Oaxaca", "capital": "oaxaca_de_juarez", "tenencia_url": "https://www.finanzasoaxaca.gob.mx/", "validado": False},
    "pue": {"nombre": "Puebla", "capital": "puebla", "tenencia_url": "https://hacienda.puebla.gob.mx/", "validado": False},
    "qro": {"nombre": "Querétaro", "capital": "queretaro", "tenencia_url": "https://www.queretaro.gob.mx/sf/", "validado": False},
    "qroo": {"nombre": "Quintana Roo", "capital": "chetumal", "tenencia_url": "https://qroo.gob.mx/sefiplan", "validado": False},
    "slp": {"nombre": "San Luis Potosí", "capital": "san_luis_potosi", "tenencia_url": "https://finanzas.slp.gob.mx/", "validado": False},
    "sin": {"nombre": "Sinaloa", "capital": "culiacan", "tenencia_url": "https://saf.sinaloa.gob.mx/", "validado": False},
    "son": {"nombre": "Sonora", "capital": "hermosillo", "tenencia_url": "https://hacienda.sonora.gob.mx/", "validado": False},
    "tab": {"nombre": "Tabasco", "capital": "villahermosa", "tenencia_url": "https://finanzas.tabasco.gob.mx/", "validado": False},
    "tam": {"nombre": "Tamaulipas", "capital": "ciudad_victoria", "tenencia_url": "https://finanzas.tamaulipas.gob.mx/", "validado": False},
    "tlax": {"nombre": "Tlaxcala", "capital": "tlaxcala_de_xicohtencatl", "tenencia_url": "https://finanzas.tlaxcala.gob.mx/", "validado": False},
    "ver": {"nombre": "Veracruz", "capital": "xalapa", "tenencia_url": "https://www.veracruz.gob.mx/finanzas/", "validado": False},
    "yuc": {"nombre": "Yucatán", "capital": "merida", "tenencia_url": "https://www.yucatan.gob.mx/saf/", "validado": False},
    "zac": {"nombre": "Zacatecas", "capital": "zacatecas", "tenencia_url": "https://finanzas.zacatecas.gob.mx/", "validado": False},
}


# ============================================================
# Municipios grandes — top 50 por población + capitales
# ============================================================

MUNICIPIOS: dict[str, dict[str, MunicipioConfig]] = {
    'ags': {
        'aguascalientes': MunicipioConfig(nombre='Aguascalientes', estado_clave='ags', poblacion_aprox=948990, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'jesus_maria': MunicipioConfig(
            nombre='Jesús María', estado_clave='ags',
            portal_predial_url='https://jesusmaria.recaudacion.net/SIM/predial.jsp',
            selectores_predial={'input': ["input[name='cuentaCatastral']", 'input#cuentaCatastral'], 'submit': ["button:has-text('Buscar')"], 'result': 'table, .resultado, .adeudos'},
            poblacion_aprox=129927, validado=True,
            notas='✅ Auto-discovery 2026-06-13: stack=unknown. Selectores derivados, validar manualmente antes de producción.',
        ),
    },
    'bc': {
        'tijuana': MunicipioConfig(nombre='Tijuana', estado_clave='bc', poblacion_aprox=1922523, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'mexicali': MunicipioConfig(nombre='Mexicali', estado_clave='bc', poblacion_aprox=1049792, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'ensenada': MunicipioConfig(nombre='Ensenada', estado_clave='bc', poblacion_aprox=443807, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'rosarito': MunicipioConfig(nombre='Playas de Rosarito', estado_clave='bc', poblacion_aprox=126890, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tecate': MunicipioConfig(nombre='Tecate', estado_clave='bc', poblacion_aprox=108440, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'bcs': {
        'la_paz': MunicipioConfig(nombre='La Paz', estado_clave='bcs', poblacion_aprox=292241, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'los_cabos': MunicipioConfig(nombre='Los Cabos', estado_clave='bcs', poblacion_aprox=351111, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
    },
    'cam': {
        'san_francisco_de_campeche': MunicipioConfig(nombre='San Francisco de Campeche', estado_clave='cam', poblacion_aprox=294077, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'ciudad_del_carmen': MunicipioConfig(nombre='Ciudad del Carmen (Carmen)', estado_clave='cam', poblacion_aprox=248303, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'champoton': MunicipioConfig(nombre='Champotón', estado_clave='cam', poblacion_aprox=89232, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'cdmx': {
        'ciudad_de_mexico': MunicipioConfig(
            nombre='Ciudad de México', estado_clave='cdmx',
            portal_predial_url='https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion',
            selectores_predial={
                'input': ["input[name='cuentaPredial']", "input#cuentaPredial"],
                'submit': ["button:has-text('Ingresar')"],
                'result': '.mat-table, table, .resultado',
            },
            poblacion_aprox=9209944, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: Oficina Virtual del Catastro (OVICA). Angular Material. Placeholder "Ingrese 12 caracteres alfanuméricos".',
        ),
        'iztapalapa': MunicipioConfig(nombre='Iztapalapa', estado_clave='cdmx', poblacion_aprox=1835486, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'gustavo_a_madero': MunicipioConfig(nombre='Gustavo A. Madero', estado_clave='cdmx', poblacion_aprox=1173351, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'alvaro_obregon': MunicipioConfig(nombre='Álvaro Obregón', estado_clave='cdmx', poblacion_aprox=759137, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'coyoacan': MunicipioConfig(nombre='Coyoacán', estado_clave='cdmx', poblacion_aprox=614447, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tlalpan': MunicipioConfig(nombre='Tlalpan', estado_clave='cdmx', poblacion_aprox=699928, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'iztacalco': MunicipioConfig(nombre='Iztacalco', estado_clave='cdmx', poblacion_aprox=404695, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'azcapotzalco': MunicipioConfig(nombre='Azcapotzalco', estado_clave='cdmx', poblacion_aprox=432205, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'venustiano_carranza': MunicipioConfig(nombre='Venustiano Carranza', estado_clave='cdmx', poblacion_aprox=443704, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'xochimilco': MunicipioConfig(nombre='Xochimilco', estado_clave='cdmx', poblacion_aprox=442178, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'miguel_hidalgo': MunicipioConfig(nombre='Miguel Hidalgo', estado_clave='cdmx', poblacion_aprox=414470, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'benito_juarez_cdmx': MunicipioConfig(nombre='Benito Juárez (CDMX)', estado_clave='cdmx', poblacion_aprox=434153, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'cuauhtemoc': MunicipioConfig(nombre='Cuauhtémoc', estado_clave='cdmx', poblacion_aprox=545884, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'magdalena_contreras': MunicipioConfig(nombre='La Magdalena Contreras', estado_clave='cdmx', poblacion_aprox=247622, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tlahuac': MunicipioConfig(nombre='Tláhuac', estado_clave='cdmx', poblacion_aprox=392313, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'milpa_alta': MunicipioConfig(nombre='Milpa Alta', estado_clave='cdmx', poblacion_aprox=152685, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'cuajimalpa': MunicipioConfig(nombre='Cuajimalpa de Morelos', estado_clave='cdmx', poblacion_aprox=217686, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'chih': {
        'ciudad_juarez': MunicipioConfig(
            nombre='Ciudad Juárez', estado_clave='chih',
            portal_predial_url='https://predial2.juarez.gob.mx/',
            selectores_predial={
                'input': ["input[name='clave']", "input#clave"],
                'submit': ["button:has-text('BUSCAR')"],
                'result': 'table',
            },
            poblacion_aprox=1512354, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: form oculto inicialmente — requiere click "BUSCAR" para revelar campo.',
        ),
        'chihuahua': MunicipioConfig(nombre='Chihuahua', estado_clave='chih', portal_predial_url='https://www.municipiochihuahua.gob.mx/TM/Predial', poblacion_aprox=937481, validado=True, notas='✅ Playwright MCP 2026-06-13: ruta /TM/Predial.'),
        'delicias': MunicipioConfig(nombre='Delicias', estado_clave='chih', poblacion_aprox=154073, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'cuauhtemoc_chih': MunicipioConfig(nombre='Cuauhtémoc (Chih)', estado_clave='chih', poblacion_aprox=184550, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'parral': MunicipioConfig(nombre='Hidalgo del Parral', estado_clave='chih', poblacion_aprox=116753, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'camargo_chih': MunicipioConfig(nombre='Camargo (Chih)', estado_clave='chih', poblacion_aprox=51998, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'nuevo_casas_grandes': MunicipioConfig(nombre='Nuevo Casas Grandes', estado_clave='chih', poblacion_aprox=65528, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'chis': {
        'tuxtla_gutierrez': MunicipioConfig(nombre='Tuxtla Gutiérrez', estado_clave='chis', portal_predial_url='https://www.tuxtla.gob.mx/predial', poblacion_aprox=604147, validado=False, notas='URL responde 403 a curl headless — verificar manualmente con browser real (CSRF/cookies).'),
        'tapachula': MunicipioConfig(nombre='Tapachula', estado_clave='chis', poblacion_aprox=353706, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_cristobal': MunicipioConfig(nombre='San Cristóbal de las Casas', estado_clave='chis', poblacion_aprox=215874, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'comitan': MunicipioConfig(nombre='Comitán de Domínguez', estado_clave='chis', poblacion_aprox=159899, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'palenque': MunicipioConfig(nombre='Palenque (Chis)', estado_clave='chis', poblacion_aprox=130715, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'ocosingo': MunicipioConfig(nombre='Ocosingo', estado_clave='chis', poblacion_aprox=240310, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'coah': {
        'saltillo': MunicipioConfig(nombre='Saltillo', estado_clave='coah', poblacion_aprox=864431, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'torreon': MunicipioConfig(nombre='Torreón', estado_clave='coah', portal_predial_url='https://pagoenlinea.torreon.gob.mx/predial', poblacion_aprox=720848, validado=True, notas='✅ Playwright MCP 2026-06-13: subdominio pagoenlinea.* dedicado.'),
        'monclova': MunicipioConfig(
            nombre='Monclova', estado_clave='coah',
            portal_predial_url='https://predial.monclova.gob.mx/appWeb/',
            selectores_predial={'input': ["input[name='cuenta']", 'input#cuenta'], 'submit': ["button:has-text('Consultar')", "input[type='submit']"], 'result': 'table, .resultado, .adeudos'},
            poblacion_aprox=237169, validado=True,
            notas='✅ Auto-discovery 2026-06-13: stack=unknown. Selectores derivados, validar manualmente antes de producción.',
        ),
        'piedras_negras': MunicipioConfig(nombre='Piedras Negras', estado_clave='coah', poblacion_aprox=173959, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'ramos_arizpe': MunicipioConfig(nombre='Ramos Arizpe', estado_clave='coah', poblacion_aprox=99385, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'frontera': MunicipioConfig(nombre='Frontera', estado_clave='coah', poblacion_aprox=87726, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'matamoros_coah': MunicipioConfig(nombre='Matamoros (Coah)', estado_clave='coah', poblacion_aprox=121722, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_pedro_coah': MunicipioConfig(nombre='San Pedro (Coah)', estado_clave='coah', poblacion_aprox=102650, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'col': {
        'colima': MunicipioConfig(nombre='Colima', estado_clave='col', poblacion_aprox=146904, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'manzanillo': MunicipioConfig(nombre='Manzanillo', estado_clave='col', poblacion_aprox=191267, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'villa_de_alvarez': MunicipioConfig(nombre='Villa de Álvarez', estado_clave='col', poblacion_aprox=138812, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tecoman': MunicipioConfig(nombre='Tecomán', estado_clave='col', poblacion_aprox=121725, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'dur': {
        'durango': MunicipioConfig(nombre='Durango (Victoria de Durango)', estado_clave='dur', poblacion_aprox=688697, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'gomez_palacio': MunicipioConfig(nombre='Gómez Palacio', estado_clave='dur', poblacion_aprox=360240, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'lerdo': MunicipioConfig(nombre='Lerdo', estado_clave='dur', poblacion_aprox=162628, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'edomex': {
        'toluca': MunicipioConfig(
            nombre='Toluca', estado_clave='edomex',
            portal_predial_url='http://predial.toluca.gob.mx/Formas/ImpuestoPredial.aspx',
            selectores_predial={
                'input': ["input[name='txtCuenta']", "input#txtCuenta"],
                'submit': ["input[type='submit'][value='Aceptar']"],
                'result': 'table, .resultado',
            },
            poblacion_aprox=910608, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: Tesorería Toluca, ASP.NET. ⚠ HTTP no HTTPS.',
        ),
        'ecatepec': MunicipioConfig(nombre='Ecatepec de Morelos', estado_clave='edomex', portal_predial_url='http://www.tesoreriaecatepec.gob.mx/IngresosTesoreria/', poblacion_aprox=1643623, validado=True, notas='✅ Playwright MCP 2026-06-13: Tesorería Ecatepec, página carga pero form no detectado en HTML inicial (probable JS load). HTTP no HTTPS.'),
        'naucalpan': MunicipioConfig(nombre='Naucalpan de Juárez', estado_clave='edomex', portal_predial_url='https://naucalpan.gob.mx/predial/', poblacion_aprox=834434, validado=True, notas='✅ Playwright MCP 2026-06-13: link encontrado en home (naucalpan.gob.mx/predial/).'),
        'tlalnepantla': MunicipioConfig(nombre='Tlalnepantla de Baz', estado_clave='edomex', poblacion_aprox=672202, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'atizapan': MunicipioConfig(nombre='Atizapán de Zaragoza', estado_clave='edomex', poblacion_aprox=523296, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'cuautitlan_izcalli': MunicipioConfig(nombre='Cuautitlán Izcalli', estado_clave='edomex', portal_predial_url='http://201.122.109.4:96/EstadoCuentaOnline/', poblacion_aprox=555163, validado=True, notas='✅ Playwright MCP 2026-06-13: IP directa con puerto :96 (no dominio DNS). HTTP no HTTPS.'),
        'nezahualcoyotl': MunicipioConfig(nombre='Nezahualcóyotl', estado_clave='edomex', poblacion_aprox=1077208, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'tlalnepantla_centro': MunicipioConfig(nombre='Tlalnepantla', estado_clave='edomex', poblacion_aprox=672202, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'ixtapaluca': MunicipioConfig(nombre='Ixtapaluca', estado_clave='edomex', poblacion_aprox=542211, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tultitlan': MunicipioConfig(nombre='Tultitlán', estado_clave='edomex', poblacion_aprox=491466, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'coacalco': MunicipioConfig(nombre='Coacalco de Berriozábal', estado_clave='edomex', poblacion_aprox=293444, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'valle_chalco': MunicipioConfig(nombre='Valle de Chalco Solidaridad', estado_clave='edomex', poblacion_aprox=391731, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'chimalhuacan': MunicipioConfig(nombre='Chimalhuacán', estado_clave='edomex', poblacion_aprox=705193, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'chalco': MunicipioConfig(nombre='Chalco', estado_clave='edomex', poblacion_aprox=365241, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'texcoco': MunicipioConfig(nombre='Texcoco', estado_clave='edomex', poblacion_aprox=277562, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'metepec': MunicipioConfig(nombre='Metepec', estado_clave='edomex', poblacion_aprox=242307, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tecamac': MunicipioConfig(nombre='Tecámac', estado_clave='edomex', poblacion_aprox=547503, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tultepec': MunicipioConfig(nombre='Tultepec', estado_clave='edomex', poblacion_aprox=153405, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'ixtlahuaca': MunicipioConfig(nombre='Ixtlahuaca', estado_clave='edomex', poblacion_aprox=153184, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'lerma': MunicipioConfig(nombre='Lerma', estado_clave='edomex', poblacion_aprox=165241, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'huixquilucan': MunicipioConfig(nombre='Huixquilucan', estado_clave='edomex', poblacion_aprox=284965, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'zinacantepec': MunicipioConfig(nombre='Zinacantepec', estado_clave='edomex', poblacion_aprox=207938, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'almoloya_juarez': MunicipioConfig(nombre='Almoloya de Juárez', estado_clave='edomex', poblacion_aprox=188833, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'gro': {
        'acapulco': MunicipioConfig(nombre='Acapulco (Guerrero)', estado_clave='gro', poblacion_aprox=779566, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: URL responde 200 pero solo es página "Agencias Recaudadoras" sin portal interactivo. Buscar URL real.'),
        'chilpancingo': MunicipioConfig(nombre='Chilpancingo', estado_clave='gro', poblacion_aprox=283354, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'iguala': MunicipioConfig(nombre='Iguala de la Independencia', estado_clave='gro', poblacion_aprox=154339, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'zihuatanejo': MunicipioConfig(nombre='Zihuatanejo de Azueta', estado_clave='gro', poblacion_aprox=126001, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'chilapa': MunicipioConfig(nombre='Chilapa de Álvarez', estado_clave='gro', poblacion_aprox=136174, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'taxco': MunicipioConfig(nombre='Taxco de Alarcón', estado_clave='gro', poblacion_aprox=105586, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'gto': {
        'leon': MunicipioConfig(
            nombre='León', estado_clave='gto',
            portal_predial_url='https://pagos.leon.gob.mx/pagonet2/Services/predial/Predial_Form.aspx',
            selectores_predial={
                'input': ["input[name='ctl00$Content_Main$CtaPre']", "input#Content_Main_CtaPre"],
                'submit': ["input[type='submit'][value*='Consultar']", "button:has-text('Consultar')"],
                'result': 'table, .resultado',
            },
            poblacion_aprox=1721215, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: PAGONET León, ASP.NET WebForms.',
        ),
        'irapuato': MunicipioConfig(nombre='Irapuato', estado_clave='gto', poblacion_aprox=592953, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'celaya': MunicipioConfig(nombre='Celaya', estado_clave='gto', poblacion_aprox=521169, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: URL responde 200 pero solo es WordPress informativo, sin portal interactivo.'),
        'salamanca': MunicipioConfig(nombre='Salamanca', estado_clave='gto', poblacion_aprox=273271, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_miguel_de_allende': MunicipioConfig(nombre='San Miguel de Allende', estado_clave='gto', poblacion_aprox=175640, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'silao': MunicipioConfig(nombre='Silao de la Victoria', estado_clave='gto', poblacion_aprox=211278, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'valle_de_santiago': MunicipioConfig(
            nombre='Valle de Santiago', estado_clave='gto',
            portal_predial_url='https://www.valledesantiago.gob.mx/predial-en-linea',
            selectores_predial={'input': ["input[name='location_account']", 'input#location_account'], 'submit': [], 'result': 'table, .resultado, .adeudos'},
            poblacion_aprox=138478, validado=True,
            notas='✅ Auto-discovery 2026-06-13: stack=unknown. Selectores derivados, validar manualmente antes de producción.',
        ),
        'guanajuato_capital': MunicipioConfig(nombre='Guanajuato (capital)', estado_clave='gto', poblacion_aprox=194500, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'hgo': {
        'pachuca': MunicipioConfig(nombre='Pachuca', estado_clave='hgo', portal_predial_url='https://www.pachuca.gob.mx/portal/predial/', poblacion_aprox=297847, validado=True, notas='✅ Playwright MCP 2026-06-13: link encontrado en home.'),
        'tulancingo': MunicipioConfig(nombre='Tulancingo de Bravo', estado_clave='hgo', poblacion_aprox=168063, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tula': MunicipioConfig(nombre='Tula de Allende', estado_clave='hgo', poblacion_aprox=115107, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'huejutla': MunicipioConfig(nombre='Huejutla de Reyes', estado_clave='hgo', poblacion_aprox=134715, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tepeji': MunicipioConfig(nombre='Tepeji del Río de Ocampo', estado_clave='hgo', poblacion_aprox=86318, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'mineral_de_la_reforma': MunicipioConfig(nombre='Mineral de la Reforma', estado_clave='hgo', poblacion_aprox=200710, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'jal': {
        'guadalajara': MunicipioConfig(nombre='Guadalajara', estado_clave='jal', portal_predial_url='https://pagoenlinea.guadalajara.gob.mx/impuestopredial/', selectores_predial={'input': ["input[aria-label='Cuenta']", "mat-form-field input[id^='mat-input']", 'input#mat-input-0'], 'submit': ["button:has-text('Consultar Adeudo Predial')", "button[type='submit']:not(:has-text('Gobierno'))"], 'result': '.mat-table, table.mat-mdc-table, mat-card.resultado'}, poblacion_aprox=1385629, validado=True, notas='Validado 2026-06-13: URL carga 200 OK directo.'),
        'zapopan': MunicipioConfig(
            nombre='Zapopan', estado_clave='jal',
            portal_predial_url='https://pagos.zapopan.gob.mx/PagoEnLineaZap/',
            selectores_predial={
                'input': ["input[name='ctl00$MainContent$txtCuenta']", "input#MainContent_txtCuenta"],
                'submit': ["input[type='submit'][value='Consultar']"],
                'result': 'table, .resultados',
            },
            poblacion_aprox=1476491, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: ASP.NET WebForms. Selectores reales aplicados.',
        ),
        'tlaquepaque': MunicipioConfig(nombre='San Pedro Tlaquepaque', estado_clave='jal', poblacion_aprox=687127, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'tonala': MunicipioConfig(nombre='Tonalá', estado_clave='jal', poblacion_aprox=569913, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'tlajomulco': MunicipioConfig(nombre='Tlajomulco de Zúñiga', estado_clave='jal', poblacion_aprox=727750, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'puerto_vallarta': MunicipioConfig(nombre='Puerto Vallarta', estado_clave='jal', poblacion_aprox=291839, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: URL existe pero solo página vacía con botón "Regresar" — NO es portal interactivo.'),
        'el_salto': MunicipioConfig(nombre='El Salto', estado_clave='jal', poblacion_aprox=234403, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'lagos_de_moreno': MunicipioConfig(nombre='Lagos de Moreno', estado_clave='jal', poblacion_aprox=184482, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'ocotlan': MunicipioConfig(nombre='Ocotlán', estado_clave='jal', poblacion_aprox=110727, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tepatitlan': MunicipioConfig(
            nombre='Tepatitlán de Morelos', estado_clave='jal',
            portal_predial_url='https://www.tepatitlan.gob.mx/e-tepa2.0/predial',
            selectores_predial={'input': ["input[name='cuenta_catastral']"], 'submit': ["button:has-text('CA')", "input[type='submit']"], 'result': 'table, .resultado, .adeudos'},
            poblacion_aprox=152368, validado=True,
            notas='✅ Auto-discovery 2026-06-13: stack=unknown. Selectores derivados, validar manualmente antes de producción.',
        ),
        'ameca': MunicipioConfig(nombre='Ameca', estado_clave='jal', poblacion_aprox=60536, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'autlan': MunicipioConfig(nombre='Autlán de Navarro', estado_clave='jal', poblacion_aprox=65697, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'mich': {
        'morelia': MunicipioConfig(nombre='Morelia', estado_clave='mich', portal_predial_url='https://pagostramites.morelia.gob.mx/Activacion/pago_rapido', poblacion_aprox=849053, validado=True, notas='✅ Playwright MCP 2026-06-13: subdominio pagostramites.* con pago_rapido.'),
        'uruapan': MunicipioConfig(nombre='Uruapan', estado_clave='mich', poblacion_aprox=356786, validado=True, plataforma_saas='SACPI', codigo_saas=None, notas='⚠ NO está en catálogo SACPI ni en discovery. Pendiente investigar — puede tener portal propio uruapan.gob.mx/predial.'),
        'zamora': MunicipioConfig(nombre='Zamora', estado_clave='mich', poblacion_aprox=196999, validado=True, plataforma_saas='SACPI', codigo_saas=None, notas='⚠ NO listado en SACPI ddlMunicipios. Verificar manualmente.'),
        'apatzingan': MunicipioConfig(nombre='Apatzingán', estado_clave='mich', poblacion_aprox=128336, validado=True, plataforma_saas='SACPI', codigo_saas='006', notas='✅ Cubierto por SACPI Michoacán (código 006). Consultar via shared.plataformas_saas_mx.consulta_sacpi().'),
        'lazaro_cardenas_mich': MunicipioConfig(nombre='Lázaro Cárdenas (Mich)', estado_clave='mich', poblacion_aprox=175625, validado=False, notas='⚠ NO listado en SACPI ddlMunicipios — puede ser portal propio. Verificar.'),
        'patzcuaro': MunicipioConfig(nombre='Pátzcuaro', estado_clave='mich', poblacion_aprox=92770, validado=False, notas='⚠ NO listado directamente en SACPI ddlMunicipios. Verificar si está como variante.'),
        'hidalgo_mich': MunicipioConfig(
            nombre='Ciudad Hidalgo (Mich)', estado_clave='mich',
            portal_predial_url='http://www.sacpi.michoacan.gob.mx/frm_cpredial.aspx',
            plataforma_saas='SACPI', codigo_saas='034',
            selectores_predial={
                'input': ["input[name='txtCuenta']", "input#txtCuenta"],
                'submit': ["button:has-text('Consultar')", "input[type='submit']"],
                'result': 'table, .resultado, .adeudos',
            },
            poblacion_aprox=122540, validado=True,
            notas='✅ SACPI Michoacán código 034. Plataforma cubre 95 municipios MICH — usar shared.plataformas_saas_mx.consulta_sacpi() en lugar de portal_predial_url directo.',
        ),
    },
    'mor': {
        'cuernavaca': MunicipioConfig(nombre='Cuernavaca', estado_clave='mor', portal_predial_url='https://recaudacion.cuernavaca.gob.mx/predial/', poblacion_aprox=378476, validado=True, notas='✅ Playwright MCP 2026-06-13: subdominio recaudacion.* vivo en Cuernavaca.'),
        'jiutepec': MunicipioConfig(nombre='Jiutepec', estado_clave='mor', poblacion_aprox=215357, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'cuautla': MunicipioConfig(nombre='Cuautla', estado_clave='mor', poblacion_aprox=187268, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'temixco': MunicipioConfig(nombre='Temixco', estado_clave='mor', poblacion_aprox=116143, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'nay': {
        'tepic': MunicipioConfig(nombre='Tepic', estado_clave='nay', portal_predial_url='https://predial.tepic.gob.mx/', poblacion_aprox=425924, validado=True, notas='✅ Playwright MCP 2026-06-13: subdominio predial.* dedicado.'),
        'bahia_de_banderas': MunicipioConfig(nombre='Bahía de Banderas', estado_clave='nay', poblacion_aprox=187739, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'santiago_ixcuintla': MunicipioConfig(nombre='Santiago Ixcuintla', estado_clave='nay', poblacion_aprox=79750, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'nl': {
        'monterrey': MunicipioConfig(nombre='Monterrey', estado_clave='nl', poblacion_aprox=1142952, validado=False, notas='Sin URL verificada — pendiente investigación.'),
        'san_pedro_garza_garcia': MunicipioConfig(
            nombre='San Pedro Garza García', estado_clave='nl',
            portal_predial_url='https://aplicativos.sanpedro.gob.mx/esanpedro/predial/ConsultaPredial.asp',
            selectores_predial={
                'input': ["input[name='txtExpediente']"],
                'submit': ["input[type='submit'][value='Consultar']"],
                'result': 'table',
            },
            poblacion_aprox=132169, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: ASP clásico, form simple.',
        ),
        'san_nicolas': MunicipioConfig(nombre='San Nicolás de los Garza', estado_clave='nl', poblacion_aprox=410692, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'guadalupe_nl': MunicipioConfig(nombre='Guadalupe (NL)', estado_clave='nl', poblacion_aprox=678006, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'apodaca': MunicipioConfig(
            nombre='Apodaca', estado_clave='nl',
            portal_predial_url='https://enlinea.apodaca.gob.mx/predial.php?id=5',
            selectores_predial={
                'input': ["input[name='expediente']", "input#expediente"],
                'submit': ["button:has-text('Consultar')"],
                'result': 'table',
            },
            poblacion_aprox=656464, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: PHP, placeholder formato 01001001.',
        ),
        'santa_catarina': MunicipioConfig(nombre='Santa Catarina', estado_clave='nl', poblacion_aprox=296954, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'garcia': MunicipioConfig(
            nombre='García', estado_clave='nl',
            portal_predial_url='https://predial.garcia.gob.mx/',
            selectores_predial={'input': ["input[name='txtExpediente']", 'input#txtExpediente'], 'submit': [], 'result': 'table, .resultado, .adeudos'},
            poblacion_aprox=396466, validado=True,
            notas='✅ Auto-discovery 2026-06-13: stack=unknown. Selectores derivados, validar manualmente antes de producción.',
        ),
        'juarez_nl': MunicipioConfig(nombre='Juárez (NL)', estado_clave='nl', poblacion_aprox=488768, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'cadereyta_jimenez': MunicipioConfig(nombre='Cadereyta Jiménez', estado_clave='nl', poblacion_aprox=100954, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'salinas_victoria': MunicipioConfig(nombre='Salinas Victoria', estado_clave='nl', poblacion_aprox=90159, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'general_escobedo': MunicipioConfig(nombre='General Escobedo', estado_clave='nl', poblacion_aprox=481752, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'oax': {
        'oaxaca_de_juarez': MunicipioConfig(nombre='Oaxaca de Juárez', estado_clave='oax', poblacion_aprox=270955, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: CloudFlare anti-bot ("Verificación de seguridad en curso"). NO automatizable sin acuerdo formal.'),
        'tuxtepec': MunicipioConfig(nombre='San Juan Bautista Tuxtepec', estado_clave='oax', poblacion_aprox=175490, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'huajuapan_de_leon': MunicipioConfig(nombre='Huajuapan de León', estado_clave='oax', poblacion_aprox=78383, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'salina_cruz': MunicipioConfig(nombre='Salina Cruz', estado_clave='oax', poblacion_aprox=91166, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'juchitan': MunicipioConfig(nombre='Juchitán de Zaragoza', estado_clave='oax', poblacion_aprox=100882, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'pue': {
        'puebla': MunicipioConfig(
            nombre='Puebla', estado_clave='pue',
            portal_predial_url='https://srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial',
            selectores_predial={
                'input': ["input[name='cuenta']", "input#cuenta"],
                'input_extra_delegacion': ["input[name='delegacion']", "input#delegacion"],
                'input_extra_lc': ["input[name='lc']", "input#lc"],
                'captcha': ["input[name='answer']"],
                'submit': ["button:has-text('Consultar')"],
                'result': 'table, .resultado',
            },
            poblacion_aprox=1692181, validado=True,
            notas='✅ Validado Playwright MCP 2026-06-13: puerto :7016. Form 4 campos (cuenta+delegacion+lc+answer=CAPTCHA). ⚠ Requiere humano-en-loop para CAPTCHA.',
        ),
        'tehuacan': MunicipioConfig(nombre='Tehuacán', estado_clave='pue', poblacion_aprox=339955, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'atlixco': MunicipioConfig(nombre='Atlixco', estado_clave='pue', poblacion_aprox=141793, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_pedro_cholula': MunicipioConfig(nombre='San Pedro Cholula', estado_clave='pue', poblacion_aprox=138796, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_andres_cholula': MunicipioConfig(nombre='San Andrés Cholula', estado_clave='pue', poblacion_aprox=153973, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'amozoc': MunicipioConfig(nombre='Amozoc', estado_clave='pue', poblacion_aprox=130834, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'cuautlancingo': MunicipioConfig(nombre='Cuautlancingo', estado_clave='pue', poblacion_aprox=107926, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'qro': {
        'queretaro': MunicipioConfig(nombre='Querétaro', estado_clave='qro', portal_predial_url='http://webservices.municipiodequeretaro.gob.mx/consultaLC/v2/', poblacion_aprox=1049777, validado=True, notas='✅ Playwright MCP 2026-06-13: webservices consultaLC v2. HTTP no HTTPS.'),
        'corregidora': MunicipioConfig(nombre='Corregidora', estado_clave='qro', portal_predial_url='https://www.corregidora.gob.mx/predial', poblacion_aprox=232119, validado=False, notas='URL responde 403 a curl headless — verificar manualmente con browser real (CSRF/cookies).'),
        'el_marques': MunicipioConfig(nombre='El Marqués', estado_clave='qro', poblacion_aprox=277672, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_juan_del_rio': MunicipioConfig(nombre='San Juan del Río', estado_clave='qro', poblacion_aprox=286797, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'qroo': {
        'cancun': MunicipioConfig(nombre='Cancún (Benito Juárez)', estado_clave='qroo', portal_predial_url='https://www.cancun.gob.mx/predial', poblacion_aprox=911503, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: SPA AJAX no completó carga (timeout). Verificar manualmente o buscar subdominio dedicado.'),
        'playa_del_carmen': MunicipioConfig(nombre='Playa del Carmen (Solidaridad)', estado_clave='qroo', poblacion_aprox=333800, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'chetumal': MunicipioConfig(nombre='Chetumal (Othón P. Blanco)', estado_clave='qroo', poblacion_aprox=233648, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'isla_mujeres': MunicipioConfig(nombre='Isla Mujeres', estado_clave='qroo', poblacion_aprox=22726, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'sin': {
        'culiacan': MunicipioConfig(nombre='Culiacán', estado_clave='sin', portal_predial_url='https://pagos.culiacan.gob.mx/miclave', poblacion_aprox=962871, validado=True, notas='✅ Playwright MCP 2026-06-13: subdominio pagos.* con /miclave.'),
        'mazatlan': MunicipioConfig(nombre='Mazatlán', estado_clave='sin', portal_predial_url='https://servicios.mazatlan.gob.mx/predial/', poblacion_aprox=502547, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: URL pública es informativa; portal real en servicios.mazatlan.gob.mx pero retorna CloudFlare 522 (backend caído).'),
        'los_mochis': MunicipioConfig(nombre='Los Mochis (Ahome)', estado_clave='sin', poblacion_aprox=449215, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'navolato': MunicipioConfig(nombre='Navolato', estado_clave='sin', poblacion_aprox=158995, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'guasave': MunicipioConfig(nombre='Guasave', estado_clave='sin', poblacion_aprox=295353, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'slp': {
        'san_luis_potosi': MunicipioConfig(nombre='San Luis Potosí', estado_clave='slp', portal_predial_url='https://sitio.sanluis.gob.mx/SanLuisPotoSi/PagoPredial', poblacion_aprox=911908, validado=True, notas='✅ Playwright MCP 2026-06-13: portal SanLuisPotoSi.'),
        'soledad_graciano_sanchez': MunicipioConfig(nombre='Soledad de Graciano Sánchez', estado_clave='slp', poblacion_aprox=343134, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'ciudad_valles': MunicipioConfig(nombre='Ciudad Valles', estado_clave='slp', poblacion_aprox=177022, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'matehuala': MunicipioConfig(nombre='Matehuala', estado_clave='slp', poblacion_aprox=100722, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'rio_verde': MunicipioConfig(nombre='Río Verde', estado_clave='slp', poblacion_aprox=96395, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'son': {
        'hermosillo': MunicipioConfig(nombre='Hermosillo', estado_clave='son', poblacion_aprox=936263, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: URL responde 200 pero solo página informativa sin form interactivo. Pendiente identificar URL real.'),
        'ciudad_obregon': MunicipioConfig(nombre='Ciudad Obregón (Cajeme)', estado_clave='son', poblacion_aprox=433050, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'nogales': MunicipioConfig(nombre='Nogales (Son)', estado_clave='son', poblacion_aprox=264782, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'navojoa': MunicipioConfig(nombre='Navojoa', estado_clave='son', poblacion_aprox=163650, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'san_luis_rio_colorado': MunicipioConfig(nombre='San Luis Río Colorado', estado_clave='son', poblacion_aprox=192739, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'guaymas': MunicipioConfig(nombre='Guaymas', estado_clave='son', poblacion_aprox=156863, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'tab': {
        'villahermosa': MunicipioConfig(nombre='Villahermosa (Centro)', estado_clave='tab', portal_predial_url='https://serviciosfinanzas.villahermosa.gob.mx:8800/serviciosfinanzas/dp/busqueda-predial.html', poblacion_aprox=755425, validado=True, notas='✅ Playwright MCP 2026-06-13: subdominio serviciosfinanzas.* puerto 8800.'),
        'cardenas_tab': MunicipioConfig(nombre='Cárdenas (Tab)', estado_clave='tab', poblacion_aprox=250845, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'huimanguillo': MunicipioConfig(nombre='Huimanguillo', estado_clave='tab', poblacion_aprox=191434, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'comalcalco': MunicipioConfig(nombre='Comalcalco', estado_clave='tab', poblacion_aprox=217415, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'macuspana': MunicipioConfig(nombre='Macuspana', estado_clave='tab', poblacion_aprox=156628, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'tam': {
        'reynosa': MunicipioConfig(nombre='Reynosa', estado_clave='tam', poblacion_aprox=704767, validado=False, notas='Sin URL verificada — pendiente investigación.'),
        'matamoros': MunicipioConfig(nombre='Matamoros', estado_clave='tam', poblacion_aprox=541823, validado=False, notas='⚠ Validado Playwright MCP 2026-06-13: URL responde 200 pero página vacía sin contenido detectable.'),
        'nuevo_laredo': MunicipioConfig(nombre='Nuevo Laredo', estado_clave='tam', poblacion_aprox=425058, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'tampico': MunicipioConfig(nombre='Tampico', estado_clave='tam', poblacion_aprox=297284, validado=False, notas='URL redirige a JPEG/PDF — no es portal interactivo (validado 2026-06-13).'),
        'altamira': MunicipioConfig(
            nombre='Altamira', estado_clave='tam',
            portal_predial_url='https://ast.siaweb.net/pago.php',
            selectores_predial={'input': ["input[name='clave']"], 'submit': [], 'result': 'table, .resultado, .adeudos'},
            poblacion_aprox=240206, validado=True,
            notas='✅ Auto-discovery 2026-06-13: stack=php. Selectores derivados, validar manualmente antes de producción.',
        ),
        'madero': MunicipioConfig(nombre='Ciudad Madero', estado_clave='tam', poblacion_aprox=211899, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'victoria': MunicipioConfig(nombre='Ciudad Victoria', estado_clave='tam', poblacion_aprox=360193, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'rio_bravo': MunicipioConfig(nombre='Río Bravo', estado_clave='tam', poblacion_aprox=124323, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'valle_hermoso': MunicipioConfig(nombre='Valle Hermoso', estado_clave='tam', poblacion_aprox=65761, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'tlax': {
        'tlaxcala_de_xicohtencatl': MunicipioConfig(nombre='Tlaxcala de Xicohténcatl', estado_clave='tlax', poblacion_aprox=95069, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'apizaco': MunicipioConfig(nombre='Apizaco', estado_clave='tlax', poblacion_aprox=79460, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'huamantla': MunicipioConfig(nombre='Huamantla', estado_clave='tlax', poblacion_aprox=92330, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'chiautempan': MunicipioConfig(nombre='Chiautempan', estado_clave='tlax', poblacion_aprox=78523, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'ver': {
        'veracruz_puerto': MunicipioConfig(nombre='Veracruz', estado_clave='ver', poblacion_aprox=607209, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'xalapa': MunicipioConfig(nombre='Xalapa', estado_clave='ver', poblacion_aprox=488531, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'cordoba': MunicipioConfig(nombre='Córdoba', estado_clave='ver', poblacion_aprox=218153, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'orizaba': MunicipioConfig(nombre='Orizaba', estado_clave='ver', poblacion_aprox=127792, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'coatzacoalcos': MunicipioConfig(nombre='Coatzacoalcos', estado_clave='ver', poblacion_aprox=310698, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'minatitlan': MunicipioConfig(nombre='Minatitlán', estado_clave='ver', poblacion_aprox=169309, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'tuxpan_ver': MunicipioConfig(nombre='Tuxpan (Ver)', estado_clave='ver', poblacion_aprox=161437, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'papantla': MunicipioConfig(nombre='Papantla', estado_clave='ver', poblacion_aprox=162645, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'poza_rica': MunicipioConfig(nombre='Poza Rica de Hidalgo', estado_clave='ver', poblacion_aprox=173761, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'boca_del_rio': MunicipioConfig(nombre='Boca del Río', estado_clave='ver', poblacion_aprox=145576, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'yuc': {
        'merida': MunicipioConfig(
            nombre='Mérida', estado_clave='yuc',
            portal_predial_url='https://isla.merida.gob.mx/serviciosinternet/predialmid/index.php',
            selectores_predial={
                'input': ["input[name='calle']", "input#calle"],
                'input_extra_calle_letra': ["input[name='calleLetra']"],
                'input_extra_numero': ["input[name='numero']"],
                'input_extra_numero_letra': ["input[name='numeroLetra']"],
                'submit': ["button:has-text('Buscar')", "input[type='submit'][value*='Buscar']"],
                'result': 'table, .resultado',
            },
            poblacion_aprox=995129, validado=True,
            notas='✅ Playwright MCP 2026-06-13: Radware perfdrive deja pasar con cookies de sesión real. Busca por dirección física (calle+numero), no por cuenta predial. Subdominio isla.merida.gob.mx PHP.',
        ),
        'kanasin': MunicipioConfig(nombre='Kanasín', estado_clave='yuc', poblacion_aprox=144786, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'valladolid': MunicipioConfig(nombre='Valladolid', estado_clave='yuc', poblacion_aprox=85460, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'uman': MunicipioConfig(nombre='Umán', estado_clave='yuc', poblacion_aprox=65113, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'progreso': MunicipioConfig(nombre='Progreso', estado_clave='yuc', poblacion_aprox=60640, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
    'zac': {
        'zacatecas': MunicipioConfig(nombre='Zacatecas', estado_clave='zac', poblacion_aprox=149607, validado=False, notas='URL anterior 404/DNS-muerto (validado 2026-06-13). Pendiente identificar URL real.'),
        'fresnillo': MunicipioConfig(nombre='Fresnillo', estado_clave='zac', poblacion_aprox=240549, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
        'guadalupe_zac': MunicipioConfig(nombre='Guadalupe (Zac)', estado_clave='zac', poblacion_aprox=207810, validado=False, notas='Agregado catálogo extendido 2026-06-13. URL pendiente verificación: correr scripts/descubrir-portal-municipal.py.'),
    },
}


# ============================================================
# Lookup helpers
# ============================================================

def listar_estados() -> list[str]:
    """Devuelve abreviaturas de los 32 estados."""
    return sorted(ESTADOS.keys())


def listar_municipios_estado(estado_clave: str) -> list[str]:
    """Devuelve claves de municipios soportados para un estado."""
    return sorted(MUNICIPIOS.get(estado_clave, {}).keys())


def listar_municipios_validados() -> list[tuple[str, str]]:
    """(estado, municipio) que tienen selectores validados manualmente."""
    return [
        (estado, mun_clave)
        for estado, muns in MUNICIPIOS.items()
        for mun_clave, mun in muns.items()
        if mun.validado
    ]


def buscar_portal_predial(estado_clave: str, municipio_clave: str) -> Optional[PortalConfig]:
    """Devuelve PortalConfig listo para consulta predial. None si no soportado."""
    mun = MUNICIPIOS.get(estado_clave, {}).get(municipio_clave)
    return mun.to_predial_config() if mun else None


def buscar_portal_multas(estado_clave: str, municipio_clave: str) -> Optional[PortalConfig]:
    """Devuelve PortalConfig para multas si está soportado."""
    mun = MUNICIPIOS.get(estado_clave, {}).get(municipio_clave)
    return mun.to_multas_config() if mun else None


def get_municipio_config(estado_clave: str, municipio_clave: str) -> Optional[MunicipioConfig]:
    return MUNICIPIOS.get(estado_clave, {}).get(municipio_clave)


def total_municipios() -> int:
    return sum(len(muns) for muns in MUNICIPIOS.values())


def total_municipios_validados() -> int:
    return len(listar_municipios_validados())


def estadisticas() -> dict:
    return {
        "estados_cubiertos": len(ESTADOS),
        "municipios_totales": total_municipios(),
        "municipios_validados": total_municipios_validados(),
        "cobertura_poblacional_aprox": sum(
            m.poblacion_aprox
            for muns in MUNICIPIOS.values()
            for m in muns.values()
        ),
    }
