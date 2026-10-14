# mp_ine_verificacion

Credencial para Votar (INE): formatos por modelo, regla de vigencia y handoff a la consulta oficial.

**Compliance**: `ine_verificar_datos` exige `autorizacion_token` del titular (datos personales).

## Tools

- `ine_verificar_datos(modelo, autorizacion_token, cic?, id_ciudadano?, ocr?, clave_elector?, numero_emision?)`
  — valida los campos que pide el INE para ese modelo y devuelve **handoff humano** (reCAPTCHA).
- `ine_consultar_vigencia(modelo, anio_emision)` — regla publicada: modelo vigente y 10 años
  desde la emisión. No ve bajas por robo/extravío.
- `ine_verificar_qr(qr_payload)` — no verificable localmente (`autentica: null`).
- `ine_generar_autorizacion(curp, proposito, vigencia_dias?)` — plantilla de texto.
- `ine_listar_modelos()` — modelos A-J con campos y vigencia según el INE.

## Estado real

**Handoff humano.** Revisado 2026-10-14 en `https://listanominal.ine.mx/scpln/`:

- httpx → 403 Cloudflare ("Just a moment"). Navegador real → 200 con **reCAPTCHA** v2
  (sitekey `6LdAe1sUAAAAACrdhVFHK5KmZ5TA8ZJ0iWQ6i64b`). No se evade.
- Campos (maxlength del formulario): CIC 9, Identificador del ciudadano 9, OCR 13,
  clave de elector 18, número de emisión 2.
- Vigentes según el INE: E (jul-2014), F (extranjero, feb-2016), G y H (dic-2019), I y J (jun-2026).
  D y A-C: "No vigente". "La vigencia de cada credencial es de diez años a partir de su emisión."

Corregido respecto al mock: autenticidad y "similitud de huellas" se decidían por el último
dígito; el CIC tenía 13 dígitos (son 9); los modelos C/D/D1/E/F y sus años eran incorrectos.
