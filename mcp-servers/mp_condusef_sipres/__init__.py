"""mp_condusef_sipres — MCP standalone para CONDUSEF SIPRES.

SIPRES = Sistema de Registro de Prestadores de Servicios Financieros.
Padrón público de entidades financieras autorizadas en México.

Universo: KYC institucional, validación fintech, due-diligence aseguradoras.

Portal: https://webapps.condusef.gob.mx/SIPRES/jsp/pub/index.jsp
Endpoint backend: POST /SIPRES/jsp/pub/resulbusq.jsp

SIN CAPTCHA, SIN XSRF — cliente httpx puro, latencia ~300ms.
"""
__all__: list[str] = []
