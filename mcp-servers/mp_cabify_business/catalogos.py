"""Catálogos Cabify Business."""

from __future__ import annotations


TIPO_VEHICULO: dict[str, dict] = {
    "lite": {"nombre": "Cabify Lite", "capacidad": 4, "tarifa_base_mxn": 50},
    "premium": {"nombre": "Cabify Premium", "capacidad": 4, "tarifa_base_mxn": 90},
    "executive": {"nombre": "Cabify Executive", "capacidad": 4, "tarifa_base_mxn": 150},
    "group": {"nombre": "Cabify Group (van)", "capacidad": 7, "tarifa_base_mxn": 200},
}


RIDE_STATUS: dict[str, str] = {
    "scheduled": "Agendado para el futuro",
    "searching_driver": "Buscando conductor",
    "driver_assigned": "Conductor asignado en camino",
    "driver_arrived": "Conductor llegó al punto de recolección",
    "in_progress": "En curso",
    "completed": "Finalizado",
    "cancelled_by_user": "Cancelado por usuario",
    "cancelled_by_driver": "Cancelado por conductor",
    "no_show": "Pasajero no llegó (cobro penalización)",
}


PAYMENT_METHOD: dict[str, str] = {
    "corporate_account": "Cuenta corporativa (factura mensual al RH)",
    "user_card": "Tarjeta del usuario (rebolsable)",
    "voucher": "Voucher pre-pagado",
}


CIUDADES_OPERATIVAS: list[str] = [
    "Ciudad de México", "Guadalajara", "Monterrey", "Puebla",
    "Querétaro", "León", "Tijuana", "Cancún", "Mérida",
]
