"""Catálogos Soft Restaurant POS (MX)."""

from __future__ import annotations


TIPOS_OPERACION: dict[str, str] = {
    "venta": "Venta normal (mesa, barra)",
    "cancelacion": "Cancelación de cuenta",
    "cortesia": "Cortesía / regalo",
    "merma": "Merma reportada",
    "anticipo": "Anticipo recibido (reserva)",
    "devolucion": "Devolución / refund",
}


ESTATUS_MESA: dict[str, str] = {
    "libre": "Sin uso",
    "ocupada": "Cliente sentado, sin orden",
    "con_orden_abierta": "Orden en curso",
    "cuenta_solicitada": "Cliente pidió la cuenta",
    "pagada_no_cerrada": "Pagada pero pendiente cierre admin",
    "reservada": "Reservada futuro",
    "limpiando": "En limpieza",
}


CATEGORIAS_MENU: dict[str, str] = {
    "entradas": "Entradas y aperitivos",
    "ensaladas": "Ensaladas",
    "sopas": "Sopas y caldos",
    "fuertes_carne": "Platos fuertes de carne",
    "fuertes_mar": "Platos fuertes de mar",
    "fuertes_pollo": "Platos fuertes de pollo",
    "pastas": "Pastas y risottos",
    "postres": "Postres",
    "bebidas_frias": "Bebidas frías",
    "bebidas_calientes": "Cafés y tés",
    "vinos": "Vinos y cavas",
    "destilados": "Destilados (tequila, whisky, etc.)",
    "cervezas": "Cervezas",
    "menu_dia": "Menú del día",
    "extras_adicionales": "Add-ons",
}


METODOS_PAGO_SR: dict[str, str] = {
    "efectivo": "Efectivo",
    "tarjeta_credito": "Tarjeta de crédito",
    "tarjeta_debito": "Tarjeta de débito",
    "transferencia": "Transferencia SPEI",
    "vale_didi": "Vale DiDi (descuento app)",
    "vale_rappi": "Vale Rappi",
    "vale_ubereats": "Vale UberEats",
    "tarjeta_regalo": "Tarjeta de regalo",
    "cortesia": "Cortesía (no es pago real)",
}


# Soft Restaurant exporta a Excel/CSV principalmente. No tiene API REST.
METODOS_EXPORT: dict[str, str] = {
    "corte_z_excel": "Corte Z del día exportado a Excel desde Soft Restaurant",
    "ventas_periodo_csv": "Ventas por periodo, exportado a CSV",
    "inventario_csv": "Inventario actual exportado a CSV",
    "platillos_vendidos_csv": "Platillos vendidos por periodo",
    "meseros_ventas_csv": "Ventas por mesero",
    "sql_server_directo": "Conexión ODBC al SQL Server (más complejo)",
}
