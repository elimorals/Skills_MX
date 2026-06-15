# mp_ine_verificacion

KYC sobre Credencial para Votar INE — Servicio de Verificación de Datos + QR alta densidad.

**Universo**: 95M credenciales activas. Uso: onboarding fintechs, notarías, telecom.

**Compliance**: requiere `autorizacion_token` del titular (LFPDPPP + Art. 142 LGIPE).

## Tools

- `ine_verificar_datos(cic, clave_elector, anio_emision, autorizacion_token)` — autentica vs padrón sin exponer datos.
- `ine_verificar_qr(qr_payload)` — verifica QR modelo F (2024+).
- `ine_consultar_vigencia(cic, autorizacion_token)` — vigencia credencial.
- `ine_generar_autorizacion(curp, proposito, vigencia_dias?)` — template firmable LFPDPPP.
- `ine_listar_modelos()` — modelos C/D/D1/E/F.
