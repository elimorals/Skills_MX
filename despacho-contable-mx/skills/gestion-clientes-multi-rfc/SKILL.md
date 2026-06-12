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

- Contraseñas CIEC cifradas en reposo
- E.firma path NO en logs
- Notificar cliente cuando se accede a su cuenta SAT
