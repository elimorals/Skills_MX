---
name: pedimento-tracker
description: Lleva un registro local de pedimentos pendientes y despachados - clave de pedimento (A1, IN, AF, F4, F5, V1), agente aduanal y patente, aduana, semáforo, plazos de retorno IMMEX y documentos del expediente electrónico. Usar cuando el usuario diga pedimento tracker, seguimiento de pedimentos, estatus de mi importación, plazos de importación temporal, control de pedimentos, qué clave de pedimento uso.
allowed-tools: Read, Write
---

# Pedimento Tracker

Registro local (archivo del usuario). Este plugin no tiene MCP de VUCEM/SAAI: el estatus en aduana lo captura el usuario o su agente aduanal.

## Claves de pedimento frecuentes (Apéndice 2, Anexo 22 RGCE 2026)

- **A1**: importación o exportación definitiva.
- **IN**: importación temporal de bienes para elaboración, transformación o reparación (IMMEX).
- **AF**: importación temporal de activo fijo (Art. 108 fr. III Ley Aduanera).
- **F4**: cambio de régimen de temporal a definitiva de insumos (IMMEX), antes de vencer el plazo de retorno.
- **F5**: cambio de régimen de temporal a definitiva de activo fijo (IMMEX).
- **V1**: transferencias virtuales entre empresas IMMEX y figuras afines.

Para otras claves, consulta el Apéndice 2 del Anexo 22 vigente.

## Qué registrar por pedimento

Número (aduana-patente-año-consecutivo), clave, fecha de pago, agente aduanal y patente, fracciones, contribuciones pagadas, resultado del mecanismo de selección automatizado (desaduanamiento libre o reconocimiento aduanero), y para temporales la fecha límite de retorno (IMMEX: 18 meses para insumos en general, Art. 108 Ley Aduanera; **verificar** plazos especiales tras la reforma vigente 2026 y el Anexo II del Decreto IMMEX).

Alertar 30 días antes del vencimiento del plazo de retorno: vencido, la mercancía se considera ilegal en el país y se causan contribuciones y multas.

## Output esperado

```json
{
  "operation": "pedimento-tracker",
  "data": {"pedimentos": [{"numero": "", "clave": "", "aduana": "", "patente": "", "fecha_pago": "", "semaforo": "", "vence_retorno": null}]},
  "vigencia_validada": false
}
```

## Casos edge

- Usuario sin padrón de importadores activo (o suspendido) → no puede importar a su nombre; revisar en el portal del SAT.
- Mercancía de padrón sectorial (Anexo 10 RGCE) → confirmar inscripción en el sector.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `acreditacion-iva-importacion` para el IVA pagado en cada pedimento
