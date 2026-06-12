"""mp_rappi_partners — MCP para restaurantes / comercios en Rappi México.

Rappi tiene API privada para partners (no pública). Las credenciales se
obtienen contactando a su equipo de Partners. Mock-first: sin credenciales
retorna datos plausibles del comercio (órdenes recientes, productos del menú,
ranking de la zona).

Tools cubiertos:
- listar_ordenes(estado, limite)
- consultar_orden(id)
- listar_productos_menu()
- actualizar_disponibilidad(producto_id, disponible)
- consultar_ranking_zona()
- estimar_comisiones_mes()

⚠ Sin API key oficial: este MCP es estructura clonable. La integración real
requiere onboarding como Partner de Rappi (proceso comercial humano).
"""
