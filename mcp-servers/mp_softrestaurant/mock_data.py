"""Mock data Soft Restaurant."""

from __future__ import annotations

from datetime import date
from typing import Any


def mock_corte_z(fecha: str) -> dict[str, Any]:
    return {
        "fecha": fecha,
        "total_dia_mxn": "28400.00",
        "comensales_total": 87,
        "ticket_promedio_mxn": "326.43",
        "metodos_pago": {
            "efectivo": "12500.00",
            "tarjeta_credito": "10200.00",
            "tarjeta_debito": "4200.00",
            "transferencia": "1500.00",
        },
        "categorias": {
            "fuertes_carne": "8500.00",
            "fuertes_pollo": "5200.00",
            "pastas": "4800.00",
            "bebidas_frias": "3500.00",
            "postres": "2400.00",
            "ensaladas": "2000.00",
            "vinos": "2000.00",
        },
        "propinas_mxn": "3200.00",
        "cancelaciones_mxn": "850.00",
        "cortesias_mxn": "450.00",
    }


def mock_ventas_periodo(desde: str, hasta: str) -> dict[str, Any]:
    return {
        "periodo": {"desde": desde, "hasta": hasta},
        "total_ventas_mxn": "548000.00",
        "total_tickets": 1632,
        "ticket_promedio_mxn": "335.78",
        "mejor_dia": {
            "fecha": "2026-03-14",
            "total_mxn": "41200.00",
            "tickets": 124,
        },
        "ventas_top_5": [
            {"folio": "T-15234", "fecha": "2026-03-14", "mesa": "12", "mesero": "Juan", "total_mxn": "4200.00", "metodo_pago": "tarjeta_credito"},
            {"folio": "T-15235", "fecha": "2026-03-14", "mesa": "8", "mesero": "Ana", "total_mxn": "3800.00", "metodo_pago": "tarjeta_credito"},
            {"folio": "T-15236", "fecha": "2026-03-14", "mesa": "5", "mesero": "Juan", "total_mxn": "3650.00", "metodo_pago": "efectivo"},
        ],
    }


def mock_inventario_actual() -> dict[str, Any]:
    return {
        "fecha_corte": date.today().isoformat(),
        "total_items_tracked": 87,
        "valor_total_inventario_mxn": "145000.00",
        "items_bajo_stock": [
            {"ingrediente": "Aguacate Hass", "stock_kg": 4.5, "punto_reorden_kg": 10, "urgencia": "alta"},
            {"ingrediente": "Tortillas maíz", "stock_kg": 8.0, "punto_reorden_kg": 15, "urgencia": "media"},
            {"ingrediente": "Pollo pechuga", "stock_kg": 6.0, "punto_reorden_kg": 12, "urgencia": "alta"},
        ],
        "items_por_vencer": [
            {"ingrediente": "Camarón fresco", "stock_kg": 3.0, "vence_dias": 1},
        ],
    }


def mock_platillos_vendidos(periodo: str) -> dict[str, Any]:
    return {
        "periodo": periodo,
        "total_platillos_distintos": 32,
        "top_5_mas_vendidos": [
            {"platillo": "Tacos al pastor", "categoria": "fuertes_carne", "cantidad": 312, "total_mxn": "45240.00"},
            {"platillo": "Pizza Margherita", "categoria": "pastas", "cantidad": 189, "total_mxn": "37800.00"},
            {"platillo": "Margarita", "categoria": "bebidas_frias", "cantidad": 156, "total_mxn": "15600.00"},
            {"platillo": "Ensalada César", "categoria": "ensaladas", "cantidad": 134, "total_mxn": "22110.00"},
            {"platillo": "Mole poblano", "categoria": "fuertes_pollo", "cantidad": 98, "total_mxn": "27440.00"},
        ],
        "top_5_menos_vendidos": [
            {"platillo": "Aguachile", "cantidad": 12, "total_mxn": "3720.00"},
            {"platillo": "Pozole verde", "cantidad": 18, "total_mxn": "3510.00"},
            {"platillo": "Tostadas tinga", "cantidad": 22, "total_mxn": "1980.00"},
        ],
    }


def mock_meseros_ventas() -> dict[str, Any]:
    return {
        "fecha": date.today().isoformat(),
        "meseros": [
            {"mesero": "Juan", "ventas_mxn": "9800.00", "tickets": 28, "ticket_promedio": "350.00", "propinas_recibidas_mxn": "850.00"},
            {"mesero": "Ana", "ventas_mxn": "7200.00", "tickets": 22, "ticket_promedio": "327.27", "propinas_recibidas_mxn": "620.00"},
            {"mesero": "Sofía", "ventas_mxn": "5300.00", "tickets": 18, "ticket_promedio": "294.44", "propinas_recibidas_mxn": "580.00"},
        ],
    }


def mock_mesas_estatus() -> dict[str, Any]:
    return {
        "total_mesas": 15,
        "distribucion": {
            "libre": 6,
            "ocupada": 2,
            "con_orden_abierta": 5,
            "cuenta_solicitada": 1,
            "pagada_no_cerrada": 0,
            "reservada": 1,
            "limpiando": 0,
        },
        "tasa_ocupacion": 0.60,
    }
