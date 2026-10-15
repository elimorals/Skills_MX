---
name: expediente-salud-personal
description: Expediente de salud que el PACIENTE mantiene (no el médico) — su copia personal con diagnósticos activos, alergias, medicamentos crónicos, estudios pasados, antecedentes familiares. Útil para llevar a primera consulta con nuevo médico o emergencia. Recomienda guardarlo cifrado (son datos sensibles). Usar cuando el usuario diga mi expediente, historia clinica personal, mis antecedentes.
allowed-tools: Read, Write
---

# Expediente salud personal

## Estructura

```python
class ExpedienteSaludPersonal(BaseModel):
    nombre: str
    fecha_nacimiento: date
    grupo_sanguineo: str
    alergias: list[str]
    diagnosticos_cronicos_cie10: list[str]
    medicamentos_cronicos: list[Medicamento]
    cirugias_previas: list[Cirugia]
    hospitalizaciones_previas: list[Hospitalizacion]
    antecedentes_familiares: list[str]
    vacunas: list[Vacuna]
    estudios_recientes: list[Estudio]
    contacto_emergencia: ContactoEmergencia
```

## Output

```
🏥 MI EXPEDIENTE DE SALUD

Datos:
  Nombre: [Hash]
  Fecha nac: 1985-03-15
  Grupo sang: O+
  Alergias: Penicilina, mariscos

Diagnósticos activos:
  • I10 - Hipertensión esencial (2019)
  • E11.9 - Diabetes mellitus T2 (2021)

Medicamentos crónicos:
  • Losartán 50mg c/24h (cardiología)
  • Metformina 850mg c/12h (endo)

Cirugías previas:
  • Apendicectomía 2010

Antecedentes familiares:
  • Padre: diabetes, hipertensión
  • Madre: cáncer mama (60a)

Última actualización: 2026-06-12
```

## Privacidad

Son datos personales sensibles (LFPDPPP 2025). La skill solo escribe archivos locales: guárdalos en carpeta cifrada (FileVault/BitLocker o un gestor con cifrado) y comparte solo el resumen necesario.
Puedes pedir por escrito a tu médico u hospital un resumen clínico de tu expediente (NOM-004-SSA3-2012; el expediente original es del prestador).
