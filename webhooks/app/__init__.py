"""plugins-mx webhook receiver.

FastAPI app que recibe webhooks de 12 servicios externos, valida firma,
maneja idempotencia y dispara handlers que invocan workflows del repo.

Diseño:
- `main.py` arma la app y monta routers.
- `config.py` carga env vars con pydantic-settings.
- `idempotency.py` deduplica eventos por (source, event_id).
- `validators/` valida firmas HMAC por servicio.
- `handlers/` despacha cada evento al workflow correspondiente.
"""

__version__ = "0.1.0"
