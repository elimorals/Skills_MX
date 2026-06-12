---
name: expediente-cliente-legal
description: Genera y actualiza expediente del cliente en despacho legal (PF o PM) incluyendo datos de identificación validados, RFC verificado contra padrón SAT y lista 69-B EFOS, poder o autorización para representar, materia del asunto (civil, mercantil, fiscal, laboral, familiar, penal, amparo), conflictos de interés revisados contra cartera actual, presupuesto y forma de cobro acordada (igualas mensuales, honorarios por etapas, cuota litis al éxito, o mixto). Crea estructura de carpetas físicas y digitales del expediente con foliado para tribunales, aviso de privacidad LFPDPPP específico para sector legal con sensibilidad por datos confidenciales del proceso. Usar cuando el usuario diga "nuevo cliente legal", "expediente abogado", "abrir caso", "registrar litigante", "iniciar asunto", "alta de cliente despacho", "client onboarding legal". NO usar para alta de cliente comercial (usar cliente-onboarding de freelancers) ni para expediente médico (usar expediente-clinico-nom004).
allowed-tools: Read, Write, Edit
---

# Expediente de cliente en despacho legal

Crea expediente completo cumpliendo requisitos legales y LFPDPPP, con la sensibilidad propia de datos sujetos a secreto profesional.

## Datos mínimos del expediente

- **Identificación**: nombre completo / razón social, RFC validado, CURP si PF
- **Contacto**: domicilio para oír y recibir notificaciones, email, WhatsApp
- **Materia del asunto**: civil / mercantil / fiscal / laboral / familiar / penal / amparo
- **Autoridad ante quien se litiga**: tribunal, juzgado, sala
- **Tipo de relación**: cliente directo, contraparte (interés contrario), referido
- **Forma de cobro**: iguala / honorarios por etapas / cuota litis / mixto
- **Conflicto de interés**: revisado contra cartera vigente — DOCUMENTAR
- **Aviso de privacidad firmado** con sección específica de datos sensibles del proceso

## Validaciones críticas

1. Verificar RFC en padrón SAT y NO esté en lista 69-B definitivo
2. Conflicto de interés: si cliente actual tiene relación adversa con el nuevo → RECHAZAR
3. Si materia es penal: confirmar autorización por escrito firmada
4. Si cuota litis: documentar % acordado + caso de no éxito (gastos)

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
