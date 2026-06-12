#!/usr/bin/env python3
"""Smoke test de los workflows ejecutables.

Valida que cada `.workflow.js` en el repo:
1. Existe en el path declarado.
2. Tiene `export const meta = {...}` bien formado (name, description, phases).
3. No tiene errores de sintaxis JavaScript obvios (paréntesis/llaves balanceados).
4. Cada `agent('...')` recibe un prompt no vacío.

No ejecuta los workflows (eso requiere el skill Workflow + Claude Code). Solo
verifica estructura — es el equivalente a `python -m py_compile` para JS.

Uso:
    python scripts/smoke_test_workflows.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

# Workflows ejecutables conocidos
WORKFLOWS = [
    REPO_ROOT / "core-mexico" / "workflows" / "cierre-fiscal-mensual.workflow.js",
    REPO_ROOT / "core-mexico" / "workflows" / "cfdi-emision-completa.workflow.js",
    REPO_ROOT / "core-mexico" / "workflows" / "due-diligence-cliente.workflow.js",
    REPO_ROOT / "core-mexico" / "workflows" / "pago-conciliacion.workflow.js",
    REPO_ROOT / "freelancers-mx" / "workflows" / "cobranza-multinivel.workflow.js",
    REPO_ROOT / "tramites-vehiculares-mx" / "workflows" / "monitoreo-diario-vehicular.workflow.js",
    REPO_ROOT / "agencia-marketing-mx" / "workflows" / "respuesta-crisis-cm.workflow.js",
    REPO_ROOT / "core-mexico" / "workflows" / "emitir-cfdi-tras-pago.workflow.js",
    REPO_ROOT / "core-mexico" / "workflows" / "validacion-cfdis-historico.workflow.js",
    REPO_ROOT / "freelancers-mx" / "workflows" / "migracion-rfc-a-otro-regimen.workflow.js",
    REPO_ROOT / "core-mexico" / "workflows" / "auditoria-fiscal-mensual.workflow.js",
    REPO_ROOT / "talleres-mx" / "workflows" / "garantia-vehicular.workflow.js",
    REPO_ROOT / "colegios-mx" / "workflows" / "comunicacion-padres-masiva.workflow.js",
    REPO_ROOT / "agencia-marketing-mx" / "workflows" / "reporte-cliente-agencia.workflow.js",
    REPO_ROOT / "nomina-pymes-mx" / "workflows" / "dispersion-nomina.workflow.js",
    REPO_ROOT / "pf-anual-mx" / "workflows" / "pf-anual-completa.workflow.js",
]


class WorkflowError(Exception):
    pass


def validate_workflow(path: Path) -> dict:
    """Retorna dict con diagnóstico de un workflow."""
    if not path.exists():
        raise WorkflowError(f"archivo no existe: {path}")

    content = path.read_text(encoding="utf-8")

    # 1. Meta declarado
    meta_match = re.search(
        r"export\s+const\s+meta\s*=\s*\{(.*?)^\}", content, re.MULTILINE | re.DOTALL
    )
    if meta_match is None:
        raise WorkflowError(f"{path.name}: no encuentra `export const meta = {{ ... }}`")
    meta_body = meta_match.group(1)
    for required in ("name", "description"):
        if required not in meta_body:
            raise WorkflowError(f"{path.name}: meta sin `{required}`")

    # 2. Llaves balanceadas (heurística simple)
    open_braces = content.count("{")
    close_braces = content.count("}")
    if open_braces != close_braces:
        raise WorkflowError(
            f"{path.name}: llaves desbalanceadas ({open_braces} abren, {close_braces} cierran)"
        )

    open_parens = content.count("(")
    close_parens = content.count(")")
    if open_parens != close_parens:
        raise WorkflowError(
            f"{path.name}: paréntesis desbalanceados ({open_parens} abren, {close_parens} cierran)"
        )

    # 3. agent() calls con prompt no vacío
    agent_calls = re.findall(
        r"agent\s*\(\s*([`'\"])(.*?)\1", content, re.DOTALL
    )
    empty_prompts = [i for i, (_q, p) in enumerate(agent_calls) if not p.strip()]
    if empty_prompts:
        raise WorkflowError(
            f"{path.name}: agent() calls con prompt vacío en posiciones {empty_prompts}"
        )

    # 4. phase() calls
    phase_calls = re.findall(r"phase\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", content)

    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "meta_name": _extract_meta_field(meta_body, "name"),
        "agent_calls": len(agent_calls),
        "phase_calls": phase_calls,
        "lines": content.count("\n") + 1,
    }


def _extract_meta_field(meta_body: str, field: str) -> str | None:
    m = re.search(rf"{field}\s*:\s*['\"]([^'\"]+)['\"]", meta_body)
    return m.group(1) if m else None


def main() -> int:
    results = []
    errors = []

    for wf in WORKFLOWS:
        try:
            diag = validate_workflow(wf)
            results.append(diag)
            print(f"✓ {diag['meta_name']:35s} | phases={len(diag['phase_calls'])} agents={diag['agent_calls']:2d} lines={diag['lines']:3d}")
        except WorkflowError as exc:
            errors.append((wf, str(exc)))
            print(f"✗ {wf.name}: {exc}")

    if errors:
        print(f"\n❌ {len(errors)} workflow(s) con errores:")
        for wf, err in errors:
            print(f"   - {wf}: {err}")
        return 1

    print(f"\n✅ {len(results)} workflow(s) pasaron smoke test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
