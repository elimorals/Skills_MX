---
name: expediente-cliente-legal
description: Genera y actualiza el expediente del cliente en un despacho legal (PF o PM) con datos de identificación validados, RFC verificado en padrón SAT y contra la lista 69-B (EFOS), poder o autorización para representar, materia del asunto (civil, mercantil, fiscal, laboral, familiar, penal, amparo), conflictos de interés revisados contra la cartera actual, presupuesto y forma de cobro acordada (iguala mensual, honorarios por etapas, cuota litis o mixto). Crea la estructura de carpetas física y digital del expediente con foliado para tribunales y el aviso de privacidad LFPDPPP con sección de datos sensibles del proceso. Usar cuando el usuario diga "nuevo cliente legal", "expediente abogado", "abrir caso", "registrar litigante", "iniciar asunto", "alta de cliente despacho", "client onboarding legal", "conflicto de interés". NO usar para alta de cliente comercial (usar cliente-onboarding de freelancers) ni para expediente médico (usar expediente-clinico-nom004).
allowed-tools: Read, Write, Edit
---

# Expediente de cliente en despacho legal

Crea el expediente con los requisitos legales y de LFPDPPP, con el cuidado propio de datos sujetos a secreto profesional.

## Datos mínimos del expediente

- **Identificación**: nombre completo / razón social, RFC validado, CURP si es PF
- **Contacto**: domicilio para oír y recibir notificaciones, email, WhatsApp
- **Materia del asunto**: civil / mercantil / fiscal / laboral / familiar / penal / amparo
- **Autoridad ante quien se litiga**: tribunal, juzgado, sala, con su nombre vigente. Desde el 1-sep-2025 la SCJN funciona solo en Pleno y el CJF fue sustituido por el Tribunal de Disciplina Judicial y el Órgano de Administración Judicial (reforma DOF 15-09-2024).
- **Código procesal aplicable**: en civil y familiar, el Código Nacional de Procedimientos Civiles y Familiares o el código estatal, según la declaratoria de la entidad (a más tardar 1-abr-2027).
- **Tipo de relación**: cliente directo, contraparte (interés contrario), referido
- **Forma de cobro**: iguala / honorarios por etapas / cuota litis / mixto
- **Conflicto de interés**: revisado contra la cartera vigente — DOCUMENTAR
- **Aviso de privacidad firmado** con sección de datos sensibles del proceso

## Validaciones críticas

1. RFC en padrón SAT y que NO esté en la lista 69-B definitiva (ver `rfc-validacion`).
2. Conflicto de interés: si un cliente actual tiene interés contrario al nuevo → RECHAZAR. El abogado que aceptó el mandato de una parte no puede aceptar el de la contraria en el mismo juicio, aunque renuncie al primero (Art. 2589 CCF).
3. Si la materia es penal: confirmar la designación o autorización por escrito firmada.
4. Si hay cuota litis: documentar el % acordado y el caso de no éxito (gastos).

## Output

```
clientes-legales/<rfc-hash>/
  ├── ficha.json
  ├── poder-o-autorizacion.pdf
  ├── aviso-privacidad-firmado.pdf
  ├── contrato-prestacion-servicios.pdf
  ├── expediente-fisico-folio.md  (correspondencia con foliado tribunal)
  └── bitacora/  (entries de actuaciones — usa bitacora-actuaciones)
```
