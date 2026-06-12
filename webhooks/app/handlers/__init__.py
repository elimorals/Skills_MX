"""Handlers despachan eventos validados al workflow correspondiente.

Cada handler recibe `(payload: dict, headers: dict)` y retorna un dict con:
- `action`: nombre del workflow / acción ejecutada
- `target_workflow`: str | None
- `notes`: list[str]

En esta primera versión los handlers son **stubs** que retornan la acción
recomendada. La integración real con workflows del repo se hace via
MCP / CLI / cola (TBD por proyecto).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


HandlerFn = Callable[[dict[str, Any], dict[str, str]], dict[str, Any]]
