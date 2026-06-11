---
description: Genera y envía aviso masivo a padres de familia vía WhatsApp Business con template apropiado por categoría y audiencia segmentada.
argument-hint: "<tipo> [grupo/grado]"
allowed-tools: Read, Write, Edit, Bash
---

# /colegios:aviso-padres

Aviso de tipo "$ARGUMENTS"

1. Invoca `comunicacion-padres-wa`.
2. Detecta tipo de aviso (académico, administrativo, operativo, emergencia) y selecciona template apropiado.
3. Pide variables específicas (fechas, montos, contexto).
4. Confirma audiencia segmentada (todo el colegio / grado / grupo / lista personalizada).
5. Estima volumen de envío.
6. Alerta si hay riesgo de saturación (3+ mensajes a esta audiencia esta semana).
7. Genera mensaje listo + lista de destinatarios + tabla CSV exportable.
8. Sugiere ventana de envío óptima (mañanas para escolares, no hora de comida, no después de 9pm).
