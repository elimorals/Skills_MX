# psicoterapia-mx

Plugin para psicólogos en práctica privada con compliance LGPDPPSO estricto.

> Score: **7.8/10**. Patrón de `consultorio-especialista-mx` + sensibilidad extra confidencial.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install psicoterapia-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Diferencia clave

Datos psicológicos = categoría más sensible LGPDPPSO. Acceso restringido estrictamente al terapeuta. Audit log obligatorio. Cifrado en reposo siempre. Sanciones mayores si fuga.

## Skills

1. `sesiones-tracking-psicoterapia` — notas por sesión sin diagnóstico literal salvo necesario
2. `consentimiento-terapia-digital` — informado firmado pre-1ra sesión
3. `cobranza-recurrente-terapia` — empático (relación clínica)
4. `gestion-pacientes-confidencial` — control acceso
5. `dashboard-terapeuta-mes`
