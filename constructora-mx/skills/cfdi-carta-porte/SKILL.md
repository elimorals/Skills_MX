---
name: cfdi-carta-porte
description: Emite CFDI 4.0 con complemento Carta Porte 3.x (obligatorio para autotransporte federal de carga + transporte de materiales en obra civil dentro de zonas federales) incluyendo datos de transporte (autotransporte tipo 01 con permiso SCT TPAF, marítimo 02, aéreo 03, ferroviario 04), ubicación origen y destino con coordenadas y código postal, mercancías transportadas con clave SAT + unidad de medida + peso/volumen, datos del operador (RFC, licencia federal de conductor LFC, número de operador), placa del vehículo, póliza de seguro de carga vigente con CFDI o póliza, y configuración vehicular del autotransporte (C2, C3, T3S2, T3S3 según SAT C_ConfigAutotransporte). Cubre traslado propio (CFDI tipo T) y traslado por flete cobrado a tercero (CFDI tipo I con complemento Carta Porte). Usar cuando el usuario diga "carta porte", "complemento autotransporte", "facturar flete", "CFDI traslado materiales", "transporte construcción", "obligación SCT". NO usar para traslado urbano de mercancía sin permiso federal ni para CFDI sin complemento de transporte.
allowed-tools: Read, Write, Edit
---

# CFDI con complemento Carta Porte 3.x

## Cuándo es obligatorio

1. **Autotransporte federal**: traslado entre estados o por carreteras federales
2. **Transporte por flete cobrado**: aún urbano si el emisor cobra por el flete
3. **Comercio exterior**: traslado de mercancía importada/exportada

## Configuración Carta Porte

| Campo | Valor típico construcción |
|---|---|
| TranspInternac | "No" si nacional |
| RegimenAduanero | N/A para nacional |
| TotalDistRec | KM totales recorridos |
| Ubicaciones | mínimo 2 (origen + destino) |
| Mercancias | clave SAT material + peso bruto |
| Autotransporte | permiso SCT + póliza + config |
| TiposFigura | operador con LFC |

## Validaciones críticas pre-timbrado

1. Permiso SCT TPAF vigente (validar contra padrón SCT)
2. LFC operador no vencida
3. Póliza de seguro de carga vigente
4. Configuración vehicular coherente con peso transportado
5. Distancia coherente entre origen y destino (validar con maps)
6. Mercancías con clave SAT correcta (no genérica)

## Output

JSON listo para `mp_facturama_extendido.timbrar_con_cartaporte` + advertencias de campos faltantes.
