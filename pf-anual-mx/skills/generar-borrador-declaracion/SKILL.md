---
name: generar-borrador-declaracion
description: Genera un borrador en PDF de la declaración anual ISR de una persona física en México listo para revisar antes de presentar en DeclaraSAT. Estructura el documento con secciones por capítulo (I Salarios, II Actividad empresarial/profesional, V Premios, etc.) según los ingresos del año. Incluye memoria de cálculo paso a paso, deducciones personales aplicadas con sus topes, comparativa contra pagos provisionales, y resultado final (saldo a pagar / a favor). Footer obligatorio con disclaimer "borrador no validado por contador certificado". Usar cuando el usuario diga generar borrador, dame PDF declaración, exporta cálculo, imprime declaración. NO usar para presentar al SAT (eso es manual vía DeclaraSAT del usuario).
allowed-tools: Read, Write
---

# Generar borrador declaración anual — PDF

## Objetivo

Salida visualmente clara que permita al usuario o contador revisar todos los números antes de cargarlos manualmente en DeclaraSAT.

## NO presenta al SAT

Este skill **genera un PDF presentable**. El usuario debe:
1. Revisar con contador
2. Cargar manualmente en DeclaraSAT (https://www.sat.gob.mx)
3. Obtener línea de captura
4. Pagar (si saldo a pagar)

## Estructura del PDF

```
1. Portada
   - Logo / nombre del freelancer
   - RFC
   - Ejercicio
   - Fecha de generación

2. Identificación
   - RFC, nombre, régimen
   - Período del cálculo (1 enero - 31 diciembre)

3. Resumen ejecutivo
   - Ingresos acumulables: $X
   - Deducciones: $Y
   - ISR causado: $Z
   - Saldo (a pagar / favor): $W

4. Capítulo II - Actividad empresarial y profesional (PFAE/RESICO PF)
   4.1 Ingresos cobrados del año (tabla por mes)
   4.2 Deducciones acumulables (tabla por categoría)
       - Honorarios pagados
       - Gastos operativos
       - Depreciaciones
   4.3 Utilidad fiscal del capítulo

5. Capítulo I - Salarios (solo si aplica)
   - Sueldos brutos
   - Prestaciones exentas
   - Subsidio al empleo
   - Total ingresos por salarios

6. Deducciones personales (Art. 151)
   - Tabla con 8 categorías
   - Topes aplicados (5 UMAs anuales)
   - Deducción personal total aplicable

7. Memoria de cálculo ISR
   - Ingresos acumulables totales
   - Menos deducciones (acumulables + personales)
   - Igual base gravable
   - Aplicar tarifa Art. 96 LISR del año (anualizada)
   - ISR causado anual

8. Pagos a cuenta
   - Pagos provisionales acumulados
   - Retenciones de ISR (banco, clientes)
   - Subsidio acreditable (asalariados)
   - Total a cuenta

9. Saldo
   - Si saldo a pagar: línea de captura sugerida (manual desde DeclaraSAT)
   - Si saldo a favor: instrucciones para solicitar devolución

10. Advertencias (caja amarilla)
    - "Borrador NO validado por contador certificado"
    - "Tarifa Art. 96 puede haber cambiado — verificar"
    - "5 UMAs anuales usadas para tope — confirmar UMA vigente"

11. Anexos
    - Lista de CFDIs aplicados como deducción personal (UUIDs)
    - Lista de CFDIs emitidos del año (resumen)
    - Lista de retenciones acreditadas

12. Footer
    - "Generado por plugins-mx pf-anual-mx v0.1.0"
    - "Este documento es un borrador. NO sustituye la opinión de un contador certificado."
    - Fecha de generación
```

## Generación técnica

Usar `reportlab` o `weasyprint`. Plantilla base en `references/template.html` (cuando exista).

```python
# Pseudo-código
def generar_pdf(calculo: dict, output_path: Path) -> Path:
    from weasyprint import HTML

    template = Path(__file__).parent / "references" / "template.html"
    rendered = jinja_env.from_string(template.read_text()).render(**calculo)
    HTML(string=rendered).write_pdf(output_path)
    return output_path
```

## Output

```json
{
  "operation": "generar_borrador_declaracion",
  "pdf_path": "~/.local/share/plugins-mx/declaraciones/2025/<rfc_hash>-borrador-2025.pdf",
  "ejercicio": 2025,
  "rfc_hash": "...",
  "paginas": 11,
  "tamanio_kb": 250,
  "advertencias_criticas": [
    "Tarifa Art. 96 LISR ejercicio 2025 debe validarse contra RMF",
    "Tope UMA anual usado: placeholder"
  ],
  "siguiente_paso": "Llevar PDF a contador certificado para revisión antes de presentar",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Comportamiento |
|---|---|
| Saldo a favor > $100k | Sección extra con instrucciones para solicitud + advertencia de auditoría |
| Múltiples capítulos (I + II) | Generar ambas secciones, total acumulado |
| Régimen cambió mid-año | Dos columnas por periodo + total |
| Persona fallecida (sucesión) | Advertencia: "caso especial, no usar este borrador" |
| Ingresos = 0 (año sin actividad) | Generar pero advertir que puede no requerir declaración |

## ⚠ Compliance

- PDF debe llevar disclaimer en footer de TODAS las páginas
- No firmar electrónicamente
- No usar logo del SAT (sería suplantación)
- `vigencia_validada: false`

## Dependencias

- Outputs de: `recopilar-cfdis-anuales`, `identificar-deducciones-personales`, `calculadora-isr-anual`, `cruzar-bancos-vs-cfdis` (opcional)
- Librerías PDF: `reportlab` o `weasyprint` (humano debe instalar)
