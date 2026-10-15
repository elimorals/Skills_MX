---
name: cfdi-carta-porte
description: Emite CFDI 4.0 con complemento Carta Porte 3.1 para traslado de materiales o maquinaria de obra: autotransporte con permiso SICT (p. ej. TPAF01), ubicaciones de origen y destino con código postal, distancia recorrida, mercancías con clave SAT, unidad y peso, operador con licencia federal, placa y configuración vehicular (C2, C3, T3S2… según c_ConfigAutotransporte) y póliza de responsabilidad civil. Cubre traslado de mercancía propia (CFDI tipo T) y flete cobrado a un tercero (CFDI tipo I con el complemento). Usar cuando el usuario diga "carta porte", "complemento autotransporte", "facturar flete", "CFDI traslado materiales", "transporte construcción", "permiso SICT". NO usar para traslados que la RMF exime del complemento ni para CFDI sin complemento de transporte.
allowed-tools: Read, Write, Edit
---

# CFDI con complemento Carta Porte 3.1

Versión vigente del complemento: 3.1 (obligatoria desde julio de 2024). Verifica en el portal del SAT si hay una versión posterior antes de timbrar.

## Cuándo es obligatorio

1. **Autotransporte por tramos de jurisdicción federal** (carreteras federales): siempre con complemento.
2. **Flete cobrado a un tercero**: CFDI tipo I con complemento.
3. **Traslado de mercancía propia** en vehículo propio: CFDI tipo T con complemento.
4. Hay facilidades en la RMF para traslados locales que no transitan tramos federales en vehículos ligeros: **verificar** la regla vigente de la RMF 2026 antes de omitir el complemento.

## Configuración Carta Porte

| Campo | Valor típico construcción |
|---|---|
| TranspInternac | "No" si es nacional |
| TotalDistRec | km totales recorridos |
| Ubicaciones | mínimo 2 (origen y destino) con CP |
| Mercancias | clave SAT del material + peso bruto en kg |
| Autotransporte | PermSCT (catálogo c_TipoPermiso) + NumPermisoSCT + placa + año modelo + ConfigVehicular + seguro de responsabilidad civil |
| FiguraTransporte | operador con RFC y número de licencia federal |

## Validaciones críticas antes de timbrar

1. Permiso SICT vigente y del tipo correcto
2. Licencia federal del operador vigente
3. Póliza de responsabilidad civil vigente
4. Configuración vehicular coherente con el peso transportado
5. Distancia coherente entre origen y destino
6. Mercancías con clave SAT específica (no genérica)

## Output

JSON del CFDI con complemento listo para `facturama_validar_payload_local` y `facturama_timbrar_cfdi` (MCP `mp_facturama_extendido`; el timbrado requiere credenciales del usuario), más advertencias de campos faltantes.

## ⚠ Compliance

El complemento cambia con frecuencia (catálogos y guía de llenado): valida con tu PAC o contador antes de circular.
