"""Utilidades para SAT Web Services — descarga masiva de CFDI.

Servicio oficial del SAT para descarga masiva (hasta 200K CFDIs por solicitud).
Endpoints SOAP autenticados con e.firma (certificado SAT del contribuyente).

Flujo (4 fases):
  1. **Autenticación** → token de sesión (5 min de vigencia).
     POST https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/Autenticacion/Autenticacion.svc
  2. **Solicitar descarga** → idSolicitud (queue del SAT).
     POST https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/SolicitaDescargaService.svc
  3. **Verificar estado** → polling hasta CodEstatusSolicitud=3 (terminada).
     POST https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/VerificaSolicitudDescargaService.svc
  4. **Descargar paquete** → ZIP con CFDIs en XML.
     POST https://cfdidescargamasiva.clouda.sat.gob.mx/DescargaMasivaService.svc

Universo: despacho-contable (200+ clientes × cierre mensual), ERPs con
reconciliación CFDI, auditoría fiscal.

Alternativa comercial sin e.firma: facturama PAC (ya implementado en
mp_facturama_extendido) — solo timbra los CFDIs propios, no descarga masivos.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


# Endpoints oficiales SAT (validados Q2 2026)
URL_AUTENTICACION = "https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/Autenticacion/Autenticacion.svc"
URL_SOLICITAR_DESCARGA = "https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/SolicitaDescargaService.svc"
URL_VERIFICAR_SOLICITUD = "https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/VerificaSolicitudDescargaService.svc"
URL_DESCARGAR_MASIVA = "https://cfdidescargamasiva.clouda.sat.gob.mx/DescargaMasivaService.svc"

# Endpoint legacy aún operativo para pruebas:
URL_PRUEBAS_BASE = "https://srvprodescargacfdi.clouda.sat.gob.mx"


# Estados de la solicitud SAT (código numérico oficial)
ESTADO_ACEPTADA = 1       # aceptada por el SAT, en cola
ESTADO_EN_PROCESO = 2     # procesándose
ESTADO_TERMINADA = 3      # ✅ lista para descarga
ESTADO_ERROR = 4          # error en el procesamiento
ESTADO_RECHAZADA = 5      # rechazada (validación falló)
ESTADO_VENCIDA = 6        # > 7 días, expiró

ESTADO_NOMBRE: dict[int, str] = {
    1: "ACEPTADA",
    2: "EN_PROCESO",
    3: "TERMINADA",
    4: "ERROR",
    5: "RECHAZADA",
    6: "VENCIDA",
}


# Tipos de comprobante (oficiales SAT)
TipoComprobante = Literal["I", "E", "T", "P", "N"]
TipoSolicitud = Literal["Metadata", "CFDI"]  # XML completos o solo metadatos


@dataclass
class SolicitudDescarga:
    """Parámetros de una solicitud de descarga masiva al SAT."""
    rfc_emisor: str           # RFC del contribuyente que descarga
    fecha_inicial: str        # "2026-01-01T00:00:00"
    fecha_final: str          # "2026-01-31T23:59:59"
    tipo_solicitud: TipoSolicitud = "CFDI"
    tipo_comprobante: TipoComprobante | None = None  # None = todos
    rfc_receptor: str = ""    # filtrar por receptor específico
    rfc_emisor_filtro: str = ""  # filtrar por emisor (si soy receptor)

    def validar(self) -> None:
        """Validaciones básicas pre-envío al SAT."""
        if not re.match(r"^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$", self.rfc_emisor.upper()):
            raise ValueError(f"RFC emisor inválido: {self.rfc_emisor}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", self.fecha_inicial):
            raise ValueError(f"fecha_inicial debe ser ISO YYYY-MM-DDTHH:MM:SS: {self.fecha_inicial}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", self.fecha_final):
            raise ValueError(f"fecha_final debe ser ISO YYYY-MM-DDTHH:MM:SS: {self.fecha_final}")
        if self.fecha_final < self.fecha_inicial:
            raise ValueError("fecha_final no puede ser anterior a fecha_inicial")


def parsear_estado_solicitud(codigo: int) -> str:
    """Devuelve el nombre human-readable de un código de estado SAT."""
    return ESTADO_NOMBRE.get(codigo, f"DESCONOCIDO_{codigo}")


def estado_es_terminal(codigo: int) -> bool:
    """¿El estado significa que ya no va a cambiar más? (terminada/error/rechazada/vencida)."""
    return codigo in (ESTADO_TERMINADA, ESTADO_ERROR, ESTADO_RECHAZADA, ESTADO_VENCIDA)


__all__ = [
    "URL_AUTENTICACION",
    "URL_SOLICITAR_DESCARGA",
    "URL_VERIFICAR_SOLICITUD",
    "URL_DESCARGAR_MASIVA",
    "ESTADO_NOMBRE",
    "ESTADO_ACEPTADA",
    "ESTADO_EN_PROCESO",
    "ESTADO_TERMINADA",
    "ESTADO_ERROR",
    "ESTADO_RECHAZADA",
    "ESTADO_VENCIDA",
    "SolicitudDescarga",
    "TipoComprobante",
    "TipoSolicitud",
    "parsear_estado_solicitud",
    "estado_es_terminal",
]
