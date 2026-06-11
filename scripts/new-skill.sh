#!/usr/bin/env bash
# new-skill.sh — scaffoldea un skill nuevo en el lugar correcto.
#
# Uso:
#   ./scripts/new-skill.sh shared <nombre>
#   ./scripts/new-skill.sh vertical <vertical> <nombre>
#
# Ejemplos:
#   ./scripts/new-skill.sh shared clabe-validacion
#   ./scripts/new-skill.sh vertical freelancers-mx nuevo-skill

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ $# -lt 2 ]; then
  echo "Uso: $0 shared <nombre>"
  echo "     $0 vertical <vertical> <nombre>"
  exit 1
fi

TYPE="$1"

if [ "$TYPE" = "shared" ]; then
  NAME="$2"
  TARGET_DIR="$ROOT/_shared/$NAME"
elif [ "$TYPE" = "vertical" ]; then
  if [ $# -lt 3 ]; then
    echo "vertical requiere <vertical> y <nombre>"
    exit 1
  fi
  VERTICAL="$2"
  NAME="$3"
  TARGET_DIR="$ROOT/$VERTICAL/skills/$NAME"
  if [ ! -d "$ROOT/$VERTICAL/.claude-plugin" ]; then
    echo "Vertical no existe: $VERTICAL"
    exit 1
  fi
else
  echo "Tipo inválido: $TYPE (use 'shared' o 'vertical')"
  exit 1
fi

if [ -d "$TARGET_DIR" ]; then
  echo "Skill ya existe: $TARGET_DIR"
  exit 1
fi

# Validar nombre kebab-case
if ! [[ "$NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
  echo "Nombre debe ser kebab-case (minúsculas, números, guiones): $NAME"
  exit 1
fi

mkdir -p "$TARGET_DIR/references"

cat > "$TARGET_DIR/SKILL.md" <<EOF
---
name: $NAME
description: [TODO: describir qué hace este skill, cuándo se invoca, sinónimos en español MX e inglés, casos de NO usar. Mínimo 80 caracteres para triggering útil. Ver guia-desarrollo.md sección "Estilo de descripción para triggering".]
allowed-tools: Read, Write, Edit
---

# $(echo "$NAME" | sed -E 's/-/ /g; s/.*/\u&/')

[TODO: 1-2 párrafos. Qué hace este skill y por qué importa.]

## Cuándo usar este skill

[Triggers explícitos y casos de uso típicos.]

## Cuándo NO usar

[Disambiguación con skills adyacentes.]

## Conocimiento base obligatorio

[Reglas, catálogos, normas que el skill aplica.]

## Reglas / Validaciones críticas

[Checks que evitan errores silenciosos.]

## Flujo

[Paso a paso de cómo opera.]

## Casos edge

[Mínimo 3-5 con cómo manejarlos.]

## Salida esperada

[Estructura del output, idealmente JSON intermedio + presentación legible.]

## Integración con otros skills

[Skills relacionados y cómo se enlazan.]

## ⚠ Datos que requieren verificación vigente

[Lista de datos que necesitan validación contra fuente oficial actual antes de uso en producción.]

## Tono

[Si aplica, indicaciones de tono al comunicar resultados al usuario.]
EOF

echo "✓ Skill scaffoldeado en: $TARGET_DIR"
echo ""
echo "Siguientes pasos:"
echo "1. Editar $TARGET_DIR/SKILL.md (description en frontmatter es CRÍTICO)"

if [ "$TYPE" = "shared" ]; then
  echo "2. Agregar a plugin.json de los plugins que lo usarán:"
  echo "   \"skills/$NAME\""
  echo "3. Correr: ./scripts/sync-shared.sh"
elif [ "$TYPE" = "vertical" ]; then
  echo "2. Agregar a $VERTICAL/.claude-plugin/plugin.json:"
  echo "   \"skills/$NAME\""
fi

echo "4. Validar: ./scripts/lint-skills.sh"
echo "5. Crear eval: evals/$([ "$TYPE" = "shared" ] && echo "_shared" || echo "$VERTICAL")/$NAME.eval.json"
echo "6. (Opcional) crear fixtures: tests/fixtures/$NAME/"
