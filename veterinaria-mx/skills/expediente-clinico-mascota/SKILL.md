---
name: expediente-clinico-mascota
description: Expediente clínico veterinario completo de mascota (perro, gato, exótico) con datos generales (raza, peso, edad, esterilizado), historial de consultas con diagnóstico y tratamiento, vacunas aplicadas con marca/lote/vencimiento, alergias documentadas, cirugías previas, medicación crónica, exámenes laboratorio y radiografías. Útil para clínicas veterinarias y hospitales. Usar cuando el usuario diga expediente mascota, historial paciente, consulta veterinaria, ficha pet, mascota nueva, alergia mascota. NO usar para vacunación standalone (vacunacion-calendario) ni urgencias (urgencias-protocolo).
allowed-tools: Read, Write, Edit
---

# Expediente clínico veterinario

Documento médico-legal de la mascota. Debe mantenerse actualizado para continuidad de tratamiento.

## Estructura del expediente

```json
{
  "id_paciente": "PET-2026-001234",
  "nombre_mascota": "Luna",
  "datos_generales": {
    "especie": "canino | felino | ave | reptil | exotico",
    "raza": "Labrador",
    "sexo": "hembra",
    "esterilizado": true,
    "fecha_nacimiento_aprox": "2020-05-15",
    "edad_calculada": "5 años 7 meses",
    "color_pelaje": "dorado",
    "peso_kg_actual": 28.5,
    "microchip": "9854321076543210",
    "tatuaje": null,
    "id_rabia_placa": "RAB-CDMX-2026-12345"
  },
  "tutor_legal": {
    "nombre": "Ana Martínez",
    "tel_wa": "+5215512345678",
    "email": "ana@example.mx",
    "rfc_opcional": "MAJG800101XYZ",
    "direccion_general": "CDMX",
    "contacto_emergencia": {
      "nombre": "Carlos Hermano",
      "tel": "+5215587654321"
    }
  },
  "alergias_conocidas": [
    "Penicilina (anafilaxia documentada 2023)",
    "Pollo (dermatitis)"
  ],
  "medicacion_cronica": [
    {
      "medicamento": "Carprofen 75mg",
      "dosis": "1 tableta cada 24h",
      "indicacion": "Displasia cadera",
      "inicio": "2024-08-15",
      "prescriptor": "MVZ Dr. Demo Cert. 12345"
    }
  ],
  "cirugias_previas": [
    {
      "fecha": "2021-03-10",
      "procedimiento": "Esterilización (ovariohisterectomía)",
      "mvz_responsable": "MVZ Demo",
      "complicaciones": "Ninguna",
      "post_op_notas": "Recuperación normal en 10 días"
    }
  ],
  "vacunas_aplicadas": [
    {
      "vacuna": "Multivalente (DAPP-L)",
      "marca": "Nobivac DHPPi-L4",
      "lote": "ABC-2025-1234",
      "fecha_aplicacion": "2025-06-15",
      "vencimiento_proteccion": "2026-06-15",
      "via_aplicacion": "subcutánea",
      "mvz_aplicante": "MVZ Cert. 12345"
    },
    {
      "vacuna": "Antirrábica",
      "marca": "Defensor 3",
      "lote": "RAB-2025-5678",
      "fecha_aplicacion": "2025-06-15",
      "vencimiento_proteccion": "2028-06-15",
      "obligatoria_cdmx": true
    }
  ],
  "consultas_historicas": [
    {
      "fecha": "2026-02-10",
      "motivo": "Vómito intermitente 3 días",
      "examen_fisico": "Decaída, deshidratación leve, abdomen sensible cuadrante anterior",
      "diagnostico_presuntivo": "Gastritis aguda",
      "tratamiento_indicado": [
        "Suero ringer SC 200ml",
        "Metoclopramida 0.5mg/kg PO cada 8h x 3 días",
        "Dieta blanda 5 días"
      ],
      "examenes_solicitados": [
        "Hemograma completo",
        "Química sanguínea (perfil basico)"
      ],
      "resultados_examenes_referencia": "ver examen-EX-2026-0345",
      "control_recomendado": "5 días",
      "mvz_atendio": "MVZ Demo Cert. 12345"
    }
  ],
  "examenes_laboratorio": [
    {
      "id": "EX-2026-0345",
      "tipo": "Hemograma + Química sanguínea",
      "fecha": "2026-02-10",
      "laboratorio_externo": "LabPet CDMX",
      "resultados_relevantes": "Leucocitosis leve (15,500), urea ligeramente elevada (45 mg/dL)",
      "interpretacion": "Compatible con inflamación gastrointestinal",
      "archivo_pdf_url": null
    }
  ],
  "radiografias_rx": [],
  "ecografias": [],
  "vacunas_pendientes": [
    {
      "vacuna": "Multivalente refuerzo anual",
      "fecha_sugerida": "2026-06-15",
      "alerta_30d": true
    }
  ]
}
```

## Vacunas obligatorias por especie

### Perro
- DAPP (multivalente: Distemper, Adenovirus, Parvovirus, Parainfluenza)
- Leptospirosis (en zonas húmedas)
- Antirrábica (obligatoria por ley CDMX, EdoMex, etc.)
- Bordetella (kennel cough — opcional según riesgo)
- Influenza canina (zonas alto contacto)
- Lyme (opcional según geografía)

### Gato
- FVRCP (Calicivirus, Rinotraqueitis, Panleucopenia)
- Leucemia felina (FeLV)
- Antirrábica
- PIF — actualmente no hay vacuna efectiva

### Exóticos
- Hurón: Distemper canino + rabia
- Conejo: Mixomatosis + RHD
- Reptiles, aves: vacunación específica por especie y región

## Reglas de seguridad

- ⚠ **Alergias previas**: SIEMPRE verificar antes de cualquier tratamiento. Si paciente tiene alergia documentada, NO usar fármaco aunque sea fórmula distinta de la misma familia.
- ⚠ **Contraindicaciones cruzadas**: NSAIDs con renal crónico, esteroides con diabetes, ciertos antibióticos en gestación.
- ⚠ **Edad y peso**: dosis siempre por kg de peso real. Cachorros < 6 meses y geriátricos > 8 años requieren ajuste.
- ⚠ **Razas con sensibilidades específicas**:
  - Collies, Border Collies, Australian Shepherd: gen MDR1 (sensibilidad a ivermectina, loperamida)
  - Bulldogs, Boxers, Doberman: sensibilidad a anestesia (premedicación distinta)
  - Greyhounds: respuesta atípica a barbitúricos

## Output estructurado

```json
{
  "expediente_resumen": {
    "id_paciente": "PET-2026-001234",
    "nombre": "Luna",
    "edad": "5 años 7 meses",
    "alertas_criticas": [
      "Alergia documentada: Penicilina (anafilaxia 2023)",
      "Medicación crónica: Carprofen 75mg"
    ],
    "vacunas_vigentes": 2,
    "vacunas_pendientes_30d": 1,
    "ultima_consulta": "2026-02-10 (Gastritis aguda)",
    "ultimo_peso_kg": 28.5,
    "tendencia_peso_6m": "estable (+0.5 kg)",
    "examenes_lab_total": 4,
    "compliance_dueño_tratamientos": "alta"
  }
}
```

## Validación pendiente

- Calendario vacunación específico por geografía (CDMX, Mérida, Tijuana)
- Catálogo medicamentos veterinarios MX vigente
- Razas sensibles (genética actualizada 2026)
- Marco legal expediente clínico veterinario (NOM-051-ZOO-1995 y posteriores)
