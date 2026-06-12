---
name: cierre-contrato-checklist
description: Checklist para cierre de contrato de arrendamiento al final de su vigencia. Cubre inspección final del inmueble, evaluación de daños vs uso normal, devolución del depósito de garantía (parcial o total con justificación), entrega de llaves, finiquito de servicios, decisión de renovación vs nuevo inquilino, y registro fiscal del fin del periodo de renta. Genera reporte estructurado y notificaciones a inquilino. Usar cuando el usuario diga cierre contrato, inquilino se va, fin de contrato, devolver depósito, renovación contrato. NO usar para terminación anticipada (eso requiere protocolo distinto).
allowed-tools: Read, Write
---

# Checklist cierre contrato arrendamiento

## Cuándo activar

- Fin de vigencia (12 o 24 meses típicos)
- Inquilino notifica desocupar (con 30+ días)
- Decisión de no renovar por parte del arrendador
- Inquilino encontró otra propiedad y se va

## Pre-cierre (30 días antes)

### Paso 1 — Confirmar fecha de entrega

- Verificar fecha original del contrato
- Confirmar por escrito con inquilino
- Si renovación: invocar `actualizacion-renta-anual` + nuevo contrato

### Paso 2 — Inspección preliminar

Visita opcional para detectar problemas grandes con anticipación:
- Estructural (techos, paredes mayores)
- Plomería visible
- Instalación eléctrica
- Aire acondicionado / calefacción
- Electrodomésticos incluidos

## Día del cierre

### Paso 3 — Inspección final (con inquilino presente)

Checklist:

```
☐ Llaves entregadas (todas + duplicados)
☐ Servicios al corriente (luz, agua, gas, internet) — pedir últimos recibos
☐ Limpieza general (alfombrado, azulejo, ventanas)
☐ Estado de muebles incluidos (si aplica)
☐ Estado de electrodomésticos incluidos
☐ Pintura interior (limpia o requiere repaint)
☐ Mantillas / claves / tarjetas / controles
☐ Áreas comunes en orden (si aplica)
☐ Fotos comparativas (inventario inicial vs estado final)
```

### Paso 4 — Evaluación de depósito

Comparar inventario inicial vs estado final:

```python
total_descuentos = 0
for danio in daños_detectados:
    if es_uso_normal(danio):
        continue  # arrendador absorbe
    if requiere_reparacion(danio):
        total_descuentos += estimar_costo_reparacion(danio)

deposito_devolver = deposito_original - total_descuentos
```

Categorías típicas:
- **Uso normal** (arrendador absorbe): rayones menores, marcas de muebles en paredes, deterioro pintura por sol/aire
- **Daño deducible**: agujeros en paredes, manchas grandes que requieren repintar, electrodomésticos descompuestos por mal uso, vidrios rotos, mascotas que dañaron

⚠ Sin pruebas (fotos comparativas, recibos de reparación), inquilino puede reclamar y SAT/jueces tienden a favorecer al inquilino.

### Paso 5 — Devolución del depósito

Plazo recomendado: 30 días post-entrega.

Forma: transferencia SPEI a CLABE del inquilino (mismo monto que se recibió + intereses si corresponde).

Si hay descuento: enviar justificación con fotos + estimado de reparaciones.

### Paso 6 — Cancelación de servicios a nombre del inquilino

Recordar al inquilino:
- Solicitar cambio de titular o cancelación (luz, internet, gas)
- Si está a nombre del arrendador: notificar nuevo inquilino o seguir pagando

### Paso 7 — Decisión: renovar o nuevo inquilino

#### Si renueva (mismo inquilino):
- Generar nuevo contrato (vía `contrato-arrendamiento-residencial`)
- Aplicar actualización de renta INPC (vía `actualizacion-renta-anual`)
- Mantener depósito o solicitar incremento si renta subió

#### Si NO renueva o nuevo inquilino:
- Marcar propiedad como vacante en tracker
- Iniciar publicación (vía `mp_inmuebles24`)
- Considerar mejoras antes del próximo inquilino (pintura general)
- Próximo flujo: nuevo screening con `screening-inquilino-completo`

## Output

```json
{
  "operation": "cierre_contrato",
  "propiedad_id": "RN-1A",
  "inquilino_id_hash": "...",
  "fecha_cierre": "2026-08-31",
  "duracion_contrato_meses": 12,
  "inspeccion_resultado": {
    "estado_general": "BUENO",
    "danios_detectados": [
      {"descripcion": "Pintura interior requiere repintado", "costo_estimado_mxn": "3000.00", "deducible": true},
      {"descripcion": "Rayones menores en azulejo cocina", "costo_estimado_mxn": "0", "deducible": false, "razon": "uso normal"}
    ],
    "fotos_comparativas_count": 25
  },
  "deposito_original_mxn": "12000.00",
  "descuentos_mxn": "3000.00",
  "deposito_a_devolver_mxn": "9000.00",
  "fecha_devolucion_planeada": "2026-09-15",
  "decision_post_cierre": "buscar_nuevo_inquilino",
  "siguiente_skill_recomendado": "publicar-en-inmuebles24",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Inquilino se va sin aviso (abandono) | Documentar antes de re-entrar (testigos), declarar abandono al notario, depósito puede quedar como compensación |
| Daños mayores (vidrios rotos, paredes destruidas) | Documentar todo, posiblemente requiere demanda — abogado |
| Inquilino reclama daños que no son su responsabilidad | Fotos comparativas son clave — sin ellas, mediar |
| Mascotas no autorizadas que dañaron | Depósito + posible aviso a próximo arrendador |
| Inquilino paga "renta del último mes" con depósito | NO permitido por estándar — depósito es garantía, no renta. Cobrar último mes regular y devolver depósito al cierre |
| Renovación con incremento INPC | Invocar workflow de renovación con `actualizacion-renta-anual` |

## Dependencias

- Tracker de propiedades + pagos
- `actualizacion-renta-anual` (si renueva)
- `contrato-arrendamiento-residencial` (si renueva)
- `mp_inmuebles24` (si busca nuevo inquilino)
- `mp_meta_whatsapp` (notificaciones)

## ⚠ Compliance

- Fotos comparativas SON la principal prueba en disputa
- Devolución de depósito debe documentarse (recibo + transferencia)
- Si descuento es alto (> 20% del depósito): explicar por escrito con presupuestos
- Conservar todos los recibos por 5 años (prescripción)
