---
name: cumplimiento-rab-cdmx
description: Cumplimiento del RAB (Registro de Anfitriones) en CDMX, obligatorio desde 2025 para hosts de alquiler temporal (< 30 días). Sin RAB activo, las plataformas no permiten publicar la propiedad y aplican multas $5,000-$40,000 MXN. Cubre proceso de registro inicial, renovación anual, número RAB obligatorio en publicaciones, y reportes periódicos a SEDUVI. Aplica solo a CDMX hasta que otros estados repliquen. Usar cuando el usuario diga RAB CDMX, registro anfitriones, regulación airbnb cdmx, cumplimiento.
allowed-tools: Read, Write
---

# Cumplimiento RAB CDMX

## Qué es

Registro de Anfitriones (RAB) — obligatorio en CDMX desde 2025 para hosts de alquiler temporal (estancias < 30 días).

## Requisitos para registro

- **Propietario o inquilino con autorización del propietario**
- Propiedad en CDMX
- Pago de derechos anuales (~$1,500-$5,000 MXN según unidades)
- Comprobante de cumplimiento de uso de suelo (en algunas alcaldías)
- Pólizas de seguro civil (recomendado, requerido en algunos casos)
- Reglamento de propiedad en condominio que permita Airbnb

## Restricciones

- Máximo **180 noches al año** por unidad (estancias < 30 días)
- Habitación / cuarto: máximo 50% de la unidad
- NO se puede operar en zonas turísticas prioritarias (Chapultepec, Coyoacán, etc.) sin permiso especial

## Multas

| Infracción | Multa |
|---|---|
| Operar sin RAB | $5,000-$40,000 MXN |
| Falsedad en declaración | hasta $50,000 MXN |
| Exceder 180 noches/año | suspensión RAB |
| No mostrar RAB en publicación | $3,000-$10,000 MXN |

## Output

```json
{
  "rab_status": "registrado",
  "rab_numero": "RAB-XXX-12345",
  "propiedad": "Roma Norte 1A",
  "fecha_registro": "2025-03-15",
  "vigencia_hasta": "2026-03-15",
  "dias_para_renovacion": 280,
  "noches_consumidas_anio": 90,
  "noches_restantes_anio": 90,
  "porcentaje_consumido": 50.0,
  "alertas": [
    "Si superas 180 noches/año, RAB se suspende"
  ],
  "publicacion_airbnb_muestra_rab": true,
  "siguiente_renovacion": "2026-03-15",
  "vigencia_validada": false
}
```

## Cómo registrarse (HUMANO)

1. Acudir o gestionar en línea con SEDUVI CDMX (https://www.seduvi.cdmx.gob.mx)
2. Presentar:
   - Comprobante de propiedad o contrato + autorización propietario
   - ID oficial
   - Comprobante de domicilio
   - Folio fiscal de la propiedad (predial al corriente)
   - Comprobante uso de suelo si lo requiere alcaldía
3. Pagar derechos
4. Recibir número RAB
5. **Actualizar el número RAB en TODAS las publicaciones de Airbnb/Vrbo/Booking**

## Casos edge

| Caso | Acción |
|---|---|
| Propietario fuera de CDMX | Designar representante legal con poder notarial |
| Habitación rentada (no unidad completa) | Aplica con restricciones de área |
| Más de 1 propiedad | Cada propiedad requiere su propio RAB |
| Renovación olvidada | RAB se suspende, plataformas remueven publicación |

## ⚠ Compliance

- RAB es obligatorio CDMX desde 2025 — validar vigencia normativa
- Otros estados (QRoo, Jalisco) tienen regulaciones similares pero distintas — extender este skill a sus equivalentes
- Multas SI son cobrables a través de plataformas (Airbnb retiene)
