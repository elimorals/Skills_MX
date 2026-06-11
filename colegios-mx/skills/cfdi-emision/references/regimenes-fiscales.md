# Regímenes fiscales — matriz completa y compatibilidad UsoCFDI

Catálogo completo de regímenes fiscales SAT (`c_RegimenFiscal`) con descripción, obligaciones principales, y matriz de compatibilidad con UsoCFDI.

## Tabla maestra

| Clave | Régimen | PF | PM | Descripción breve |
|---|---|---|---|---|
| 601 | General de Ley Personas Morales | No | Sí | El régimen "default" para PM con fines lucrativos |
| 603 | Personas Morales con Fines no Lucrativos | No | Sí | AC, fundaciones, sociedades civiles no lucrativas |
| 605 | Sueldos y Salarios e Ingresos Asimilados | Sí | No | Trabajadores con relación laboral |
| 606 | Arrendamiento | Sí | No | PF que arrienda inmuebles |
| 607 | Régimen de Enajenación o Adquisición de Bienes | Sí | No | Venta/compra de bienes |
| 608 | Demás ingresos | Sí | No | Cajón de ingresos no clasificados |
| 610 | Residentes en el Extranjero sin Establecimiento Permanente | Sí | Sí | Extranjeros sin presencia fiscal en MX |
| 611 | Ingresos por Dividendos (socios y accionistas) | Sí | No | Reparto de utilidades a accionistas |
| 612 | Personas Físicas con Actividades Empresariales y Profesionales (PFAE) | Sí | No | El régimen "default" para freelancers tradicional |
| 614 | Ingresos por intereses | Sí | No | Intereses bancarios y de inversiones |
| 615 | Ingresos por obtención de premios | Sí | No | Premios de lotería, rifas, sorteos |
| 616 | Sin obligaciones fiscales | Sí | No | Personas sin actividad fiscal regular |
| 620 | Sociedades Cooperativas de Producción que optan por diferir | No | Sí | Cooperativas específicas |
| 621 | Incorporación Fiscal (RIF) | Sí | No | Cerrado a nuevas altas desde 2022, migra a RESICO |
| 622 | Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras | No | Sí | Sector primario |
| 623 | Opcional para Grupos de Sociedades | No | Sí | Consolidación de grupos |
| 624 | Coordinados (autotransporte) | No | Sí | Coordinados del autotransporte terrestre |
| 625 | Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas | Sí | No | Uber, Rappi, Airbnb, etc. |
| 626 | Régimen Simplificado de Confianza (RESICO) | Sí | Sí | **El más relevante hoy**. Vigente desde 2022 |

---

## Matriz de compatibilidad: UsoCFDI por régimen del receptor

Esta es una matriz **simplificada**. El SAT mantiene la matriz completa actualizada en su portal y los PACs la validan al timbrar. Si tu receptor está en una combinación no permitida, el PAC rechaza.

### Leyenda
- ✓ Generalmente permitido
- ✗ NO permitido
- ⚠ Permitido pero con restricciones

| UsoCFDI | 601 | 603 | 605 | 606 | 607 | 608 | 612 | 626 PF | 626 PM |
|---|---|---|---|---|---|---|---|---|---|
| G01 Adquisición de mercancías | ✓ | ✓ | ✗ | ✗ | ⚠ | ✓ | ✓ | ✗ | ✓ |
| G02 Devoluciones, descuentos | ✓ | ✓ | ✗ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| G03 Gastos en general | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ⚠ | ✓ |
| I01 Construcciones | ✓ | ✓ | ✗ | ✓ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| I02 Mobiliario y equipo de oficina | ✓ | ✓ | ✗ | ✓ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| I03 Equipo de transporte | ✓ | ✓ | ✗ | ✓ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| I04 Equipo de cómputo y accesorios | ✓ | ✓ | ✗ | ✓ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| I05 Dados, troqueles, moldes, matrices | ✓ | ✓ | ✗ | ⚠ | ✗ | ✓ | ✓ | ✗ | ✓ |
| I06 Comunicaciones telefónicas | ✓ | ✓ | ✗ | ✓ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| I07 Comunicaciones satelitales | ✓ | ✓ | ✗ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| I08 Otra maquinaria y equipo | ✓ | ✓ | ✗ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| D01 Honorarios médicos | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D02 Gastos médicos por incapacidad | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D03 Gastos funerales | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D04 Donativos | ✓ | ✓ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✓ |
| D05 Intereses hipotecarios | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D06 Aportaciones SAR | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D07 Primas seguros gastos médicos | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D08 Transporte escolar | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D09 Depósitos para el ahorro | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| D10 Pagos por servicios educativos (colegiaturas) | ✗ | ✗ | ⚠ | ⚠ | ⚠ | ✓ | ✓ | ⚠ | ✗ |
| S01 Sin efectos fiscales | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CP01 Pagos (REP) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CN01 Nómina | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Reglas clave

1. **D0X solo aplican a PF**: las deducciones personales (D01-D10) son derecho exclusivo de PF que pueden deducir en su declaración anual. PM nunca usa D0X.

2. **Régimen 605 (Sueldos y Salarios) tiene compatibilidad restringida**: los trabajadores no operan negocio, por lo que muchos G/I no aplican. Excepción: si el trabajador tiene gastos personales relacionados con deducciones del Art. 151.

3. **RESICO PF (626) tiene compatibilidad limitada**: el régimen es simplificado, por lo que algunas claves G/I son restringidas. El SAT publica matriz específica.

4. **Régimen 616 (Sin obligaciones fiscales)**: solo recibe CFDIs informativos. UsoCFDI S01 típicamente.

5. **Régimen 610 (Extranjeros)**: típicamente S01 cuando son receptor genérico XEXX. Algunos otros si tienen RFC asignado.

---

## Obligaciones principales por régimen

### 601 - General de Ley PM
- ISR 30% sobre utilidad fiscal
- IVA 16% (cobra y entera)
- Pagos provisionales mensuales
- Declaración anual
- Contabilidad electrónica

### 603 - Personas Morales No Lucrativas
- Sin ISR (régimen no contribuyente)
- IVA solo si causa
- Reportes anuales informativos
- Si tiene autorización para recibir donativos: requisitos adicionales

### 605 - Sueldos y Salarios
- ISR retenido por el patrón (Art. 96 LISR)
- Sin pagos provisionales del trabajador
- Declaración anual obligatoria si:
  - Ingresos > $400k MXN
  - 2+ patrones
  - Ingresos adicionales (intereses, etc.)
- Deducciones personales aplicables

### 612 - PFAE
- ISR tarifa progresiva Art. 96 LISR
- IVA 16% sobre actividad profesional/empresarial
- Pagos provisionales mensuales
- Declaración anual
- Posibilidad de deducir gastos relacionados

### 626 - RESICO
- **RESICO PF**: tarifa muy baja (1-2.5%) sobre ingresos cobrados
- **RESICO PM**: tarifa también reducida sobre flujo
- Sin pagos provisionales (mensual definitivo)
- Declaración anual informativa
- Limitación: ingresos hasta $3.5M MXN anuales (PF)
- **No deduce gastos** (es la simplificación principal)

### 625 - Plataformas Tecnológicas
- ISR e IVA retenidos por la plataforma (Uber, Rappi, etc.)
- Opciones:
  - Considerar retención como pago definitivo (no declaración anual)
  - Acumular y deducir (declara anual)
- Régimen específico del Capítulo II Sección III LISR

---

## Cambio de régimen

### Cómo cambiar
- Trámite en portal SAT con e.firma
- Aviso de actualización de obligaciones
- Efectivo según fecha del aviso (típicamente próximo ejercicio)

### Restricciones
- 626 RESICO requiere ingresos < $3.5M anuales
- No puedes salir y entrar a voluntad año tras año
- Algunos regímenes son one-way (ej. salir de 621 RIF no permite regresar)

### Consideraciones
- ¿Te conviene fiscalmente? Hacer comparativo
- ¿Cambia tu retención al facturar? Sí (PFAE 10% vs RESICO 1.25%)
- ¿Cómo notificar a clientes? Mensaje + nueva Constancia Situación Fiscal

---

## ⚠ Verificación vigente requerida

La matriz UsoCFDI vs Régimen se actualiza con cambios en RMF anual. Validar con:
- Portal SAT (`https://www.sat.gob.mx`)
- Validador del PAC que uses
- Constancia de Situación Fiscal del receptor (lista UsoCFDI que puede recibir)

Esta tabla refleja entendimiento general al momento del training; **NO sustituye validación oficial**.

---

## Recursos

- LISR — Ley del Impuesto Sobre la Renta (DOF actualizado)
- LIVA — Ley del Impuesto al Valor Agregado
- CFF — Código Fiscal de la Federación
- RMF — Resolución Miscelánea Fiscal (publicación anual + modificaciones)

---

## Ver también

- `catalogos-sat.md` — catálogos detallados
- `casos-edge-cfdi.md` — patrones complejos por escenario
- [glosario-fiscal-mx.md](../../../docs/glosario-fiscal-mx.md) — términos
