---
name: gestion-clientes-multi-rfc
description: Directorio de clientes del despacho con datos fiscales completos por cada uno (RFC, régimen, e.firma, contraseñas SAT cifradas, e.firma vencimiento, contacto, mensualidad servicio). Permite agregar, modificar, dar de baja clientes y consultar status. Usar cuando el usuario diga clientes despacho, agregar cliente, directorio.
allowed-tools: Read, Write
---

# Gestión clientes multi-RFC

## Schema cliente

```python
class ClienteDespacho(BaseModel):
    cliente_id: str
    rfc: str
    razon_social: str
    tipo: Literal["PF", "PM"]
    regimen_fiscal: str
    e_firma_cer_path: Path
    e_firma_vencimiento: date
    ciec_password_cifrada: bytes | None
    contacto_principal: str
    tel_wa: str
    email: str
    fecha_alta_despacho: date
    mensualidad_servicio_mxn: Decimal
    estado: Literal["activo", "atrasado_pago", "baja"]
    notas: str
```

## Vista

```
👥 CLIENTES DEL DESPACHO (47 activos, 3 atrasados)

🟢 Activos al corriente (42):
  • ACME S.A. de C.V.   PM 601  $3,500/mes
  • Juan Pérez          PF 612  $1,200/mes
  ...

🟡 Atrasados pago servicio (3):
  • Cliente A — $1,200 — 25 días atrasado
  ...

⚠ E.firma vence < 90 días (5):
  • Cliente B — vence 2026-09-01 — renovar
  ...
```

## ⚠ Compliance

- Contraseñas (antes CIEC) cifradas en reposo; nunca guardes la contraseña de la llave privada (.key) de la e.firma en el mismo lugar que el archivo
- Rutas de e.firma y contraseñas NO en logs
- Guardar e.firma y contraseña de un cliente requiere su autorización expresa y por escrito; la e.firma equivale a su firma autógrafa (Art. 17-D CFF)
- Datos personales de clientes PF: aviso de privacidad conforme a la LFPDPPP vigente (DOF 20-03-2025; autoridad: Secretaría Anticorrupción y Buen Gobierno). Ver skill `compliance-lfpdppp`
- Notificar al cliente cuando se accede a su cuenta SAT
- Vencimientos de e.firma: usa el skill `gestor-efirma-vencimientos` de `core-mexico`
