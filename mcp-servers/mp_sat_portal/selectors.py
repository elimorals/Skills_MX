"""Registro versionado de selectores del portal SAT.

Los selectores del portal SAT cambian cada 3-6 meses. Este módulo separa la
"data" (qué selectores usar) del "code" (cómo usarlos), siguiendo el patrón
"selector strategy" mencionado en SETUP_PLAYWRIGHT_REAL.md.

## Cómo actualizar cuando un selector rompe

1. Identificar versión vigente del portal (mirar `?version=` o inspeccionar HTML).
2. Crear nueva clase `SelectorsV{N+1}` heredando de la previa.
3. Sobrescribir solo los selectores que cambiaron.
4. Bumpear `CURRENT_VERSION`.
5. Actualizar fixture HTML en `tests/fixtures/sat_portal_login_v{N+1}.html`.
6. Correr `detector_breakage` contra el nuevo fixture para validar.

## Por qué no embeber los selectores en el cliente

- Permite tests sin tocar el cliente.
- Permite el equivalente a Strategy Pattern: para regresar a versión previa
  basta cambiar `SatPlaywrightClient(selectors=SelectorsV3())`.
- Facilita versionar el "estado del portal" en commits independientes
  del lifecycle del MCP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SelectorsV1:
    """Selectores conocidos del portal SAT — captura inicial 2026-Q2.

    ⚠ Estos selectores son una **hipótesis inicial razonable** basada en la
    estructura habitual del portal. Deben validarse contra el portal vigente
    al momento de implementar el scraping real (`_real_*` en
    `playwright_client.py`).

    Cada selector lleva nombre semántico que el cliente usa, no el selector
    CSS/XPath en sí. Esto permite cambiar la implementación sin tocar el
    código que los consume.
    """

    version: str = "v1-2026-Q2-hypothetical"

    # ---------- Login con e.firma ----------
    login_url: str = "https://siat.sat.gob.mx/PTSC/auth/login.jsf"
    """URL de login con e.firma (FIEL)."""

    login_input_cer: str = "input[type='file'][accept*='.cer']"
    """Input para subir el certificado .cer."""

    login_input_key: str = "input[type='file'][accept*='.key']"
    """Input para subir la llave privada .key."""

    login_input_password: str = "input[type='password'][name*='password']"
    """Campo de contraseña de e.firma."""

    login_button_submit: str = "button[type='submit']:has-text('Iniciar')"
    """Botón submit del formulario de login."""

    login_success_indicator: str = "text=Bienvenido"
    """Texto/selector que confirma login exitoso (ajustar tras validar portal)."""

    login_error_indicator: str = ".error-message, .alert-danger"
    """Selector para detectar error de credenciales."""

    # ---------- CSF (Constancia de Situación Fiscal) ----------
    csf_menu_link: str = "a:has-text('Constancia de Situación Fiscal')"

    csf_button_descargar: str = "button:has-text('Generar Constancia')"

    csf_download_link: str = "a[href$='.pdf'][download]"

    # ---------- Buzón Tributario ----------
    buzon_url: str = "https://buzonservicios.sat.gob.mx"

    buzon_lista_notificaciones: str = ".lista-notificaciones tr, [role='listitem'].notificacion"

    buzon_notificacion_no_leida: str = ".no-leida, [data-status='unread']"

    buzon_notificacion_titulo: str = ".titulo, .subject"

    buzon_notificacion_fecha: str = ".fecha, time"

    # ---------- Descarga masiva CFDIs ----------
    cfdi_descarga_url: str = "https://portalcfdi.facturaelectronica.sat.gob.mx"

    cfdi_radio_emitidos: str = "input[type='radio'][value='emitidos']"

    cfdi_radio_recibidos: str = "input[type='radio'][value='recibidos']"

    cfdi_input_fecha_inicio: str = "input[name*='fechaInicial']"

    cfdi_input_fecha_fin: str = "input[name*='fechaFinal']"

    cfdi_button_buscar: str = "button:has-text('Buscar CFDI')"

    cfdi_resultados_tabla: str = "table.tabla-resultados, [data-testid='resultados']"

    cfdi_button_descargar_seleccion: str = "button:has-text('Descarga masiva')"

    # ---------- Acuse de declaración ----------
    acuse_input_folio: str = "input[name*='folio']"

    acuse_button_consultar: str = "button:has-text('Consultar Acuse')"

    acuse_download_link: str = "a[href*='acuse'][href$='.pdf']"

    # ---------- Genérico ----------
    loading_spinner: str = ".spinner, .loading, [aria-busy='true']"
    """Selector del spinner global — para esperar a que termine cualquier acción."""

    timeout_navigation_ms: int = 30_000
    """Timeout de navegación en milisegundos."""

    timeout_action_ms: int = 15_000
    """Timeout de cada acción (click, fill, etc.)."""

    def as_dict(self) -> dict[str, Any]:
        """Exporta todos los selectores como dict — útil para detector_breakage."""
        return {
            k: getattr(self, k)
            for k in self.__dataclass_fields__
            if not k.startswith("_")
        }

    def login_selectors(self) -> list[str]:
        """Subset de selectores requeridos para el flujo de login.

        Esto permite que el detector de breakage corra checks por flujo
        (validar login sin tocar Buzón, etc.).
        """
        return [
            self.login_input_cer,
            self.login_input_key,
            self.login_input_password,
            self.login_button_submit,
        ]

    def csf_selectors(self) -> list[str]:
        return [self.csf_menu_link, self.csf_button_descargar, self.csf_download_link]

    def buzon_selectors(self) -> list[str]:
        return [
            self.buzon_lista_notificaciones,
            self.buzon_notificacion_titulo,
            self.buzon_notificacion_fecha,
        ]

    def cfdi_masivo_selectors(self) -> list[str]:
        return [
            self.cfdi_radio_emitidos,
            self.cfdi_radio_recibidos,
            self.cfdi_input_fecha_inicio,
            self.cfdi_input_fecha_fin,
            self.cfdi_button_buscar,
        ]


# Cuando el portal cambie, crear SelectorsV2(SelectorsV1) heredando y
# sobrescribiendo solo lo que rompió:
#
# @dataclass(frozen=True)
# class SelectorsV2(SelectorsV1):
#     version: str = "v2-2026-Q4-after-redesign"
#     login_button_submit: str = "button.btn-primary[data-action='login']"


CURRENT_VERSION: type[SelectorsV1] = SelectorsV1
"""Selectores actuales — actualizar cuando el portal cambie."""


def default_selectors() -> SelectorsV1:
    """Devuelve la instancia de la versión vigente."""
    return CURRENT_VERSION()
