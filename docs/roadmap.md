# Roadmap

**Propósito**: qué sigue en el monorepo después de la oleada 1.

**Pre-lectura**: [README raíz](../README.md) (sección Pendientes) y [plan-mock-a-real.md](plan-mock-a-real.md).

El roadmap de junio de 2026 (verticales por trimestre, métricas de negocio) quedó en [historial/roadmap-2026-06.md](historial/roadmap-2026-06.md). Los 40 verticales que ahí se planeaban ya existen.

---

## Hecho (2026-10)

- **Oleada 1, de mock a real**: sin fallback silencioso a datos de ejemplo, estado real documentado por MCP y generado a `mcp-servers/CATALOGO.md` ([ADR 008](adrs/008-estado-real-sin-fallback-silencioso.md)).
- **Entrega a humano unificada** para portales con CAPTCHA o login (`shared/portal_handoff.py`) y **solver de CAPTCHA opt-in** (`shared/captcha_solver.py`).
- **Distribución portable**: marketplace instalable con `/plugin marketplace add elimorals/Skills_MX` y MCPs lanzados con `uv` desde GitHub, sin rutas locales.

## Siguiente

| Tema | Qué falta | Depende de |
|---|---|---|
| **Login de usuario final (grupo G del plan)** | IMSS, INFONAVIT, bancos, Buró, CFE y Telmex | Credenciales de prueba y una captura HAR de cada flujo. Para bancos, evaluar un agregador (Belvo, Finerio) en vez de scraping |
| **Validación en vivo** | Los 13 MCPs "real sin validar" y los portales con solver | Una credencial o llave por proveedor para la primera prueba real |
| **MCPs sin "Estado real"** | Los 11 marcados "sin verificar" (grupo de login más `aspel_contpaqi` y `softrestaurant`) | Exports de muestra del software local |
| **Oleada 3: documentos** | Extracción de PDFs (CSF, opinión 32-D, recibos CFE/Telmex) donde las skills reciben documentos | — |
| **Calidad de skills** | Ampliar los evals de salida (corrección de la respuesta, no solo triggering) y dar lógica propia a los verticales que hoy solo tienen estructura | Validación de contador o abogado por vertical |

## Criterio para llamar "producción" a un vertical

1. Sus MCPs están en estado real validado en [`CATALOGO.md`](../mcp-servers/CATALOGO.md).
2. Sus skills fiscales o legales fueron revisadas por un experto del sector.
3. Sus cálculos tienen casos golden (`scripts/eval-golden.py`) y evals de salida.

---

## Ver también

- [plan-mock-a-real.md](plan-mock-a-real.md): grupos y oleadas
- [INDEX.md](INDEX.md): índice general
