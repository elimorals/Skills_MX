# veterinaria-mx

Plugin para clínicas veterinarias y pet care en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install veterinaria-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Casos de uso

- **Clínica solo-vet** (1-2 médicos): expediente + agenda + vacunas
- **Clínica multi-especialidad**: cirugía, dermatología, oncología
- **Hospital veterinario 24h**: protocolo urgencias + hospitalización
- **Pet shop con vet**: integración pet shop + servicios médicos
- **Estética canina**: baños, cortes, manicure pet

## Skills propios (5)

| Skill | Cuándo activa |
|---|---|
| `expediente-clinico-mascota` | Historial, vacunas, alergias, cirugías previas |
| `vacunacion-calendario` | Calendario vigente con recordatorios automáticos |
| `recordatorios-pet-wa` | WhatsApp al dueño: vacunas, citas, urgencias |
| `tarifario-servicios-vet` | Consulta, cirugía, hospitalización, estética |
| `urgencias-protocolo` | Triaje 24h + decisión hospitalización vs casa |

## Comandos

```
/vet:registrar-mascota
/vet:agendar-vacuna
/vet:cotizar-servicio-vet
/vet:urgencia
```

## Estado

⚠ Scaffolding (v0.1.0). Validar con veterinario certificado antes de producción.
