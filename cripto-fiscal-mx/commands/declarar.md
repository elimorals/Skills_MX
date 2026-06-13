---
description: Genera reporte completo para declaración anual cripto del ejercicio. Orquesta importación + FIFO + permutas + rendimientos + NFTs + self-custody + expediente SAT.
argument-hint: "[ejercicio] [opcional: --regenerar]"
---

Invoca el workflow ejecutable `cripto-fiscal-mx/workflows/declaracion-anual-cripto.workflow.js`.

Args esperados: `{ rfc, ejercicio: number, exchanges?: string[], wallets_self_custody?: array, regenerar?: boolean }`.

Si el usuario solo proporciona año, infiere RFC desde `_shared/contexto-cliente` y pregunta por wallets adicionales.
