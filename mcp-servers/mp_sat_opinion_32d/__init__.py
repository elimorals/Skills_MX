"""mp_sat_opinion_32d — MCP para Consulta Pública SAT Opinión 32-D.

La "opinión 32-D" es el cumplimiento de obligaciones fiscales del contribuyente
ante el SAT (Art. 32-D del Código Fiscal de la Federación).

Es OBLIGATORIO para cualquier proveedor que contrate con el gobierno federal
y práctica estándar B2B para due-diligence de proveedores nuevos.

Portal: https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico — SIN CAPTCHA,
público (solo aparece el resultado si el contribuyente autorizó publicación).

Backend descubierto: POST /ConsultaPublico/Index con FormData → JSON o HTML+PDF
firmado por SAT. Latencia ~200ms (sin browser).

Universo: TODO proveedor B2B/B2G mexicano.
"""
__all__: list[str] = []
