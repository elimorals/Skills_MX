# Integración con servicios SAT para validación de RFC

Validar estructura del RFC localmente es solo el 60% del trabajo. Para confirmar:
1. RFC existe en padrón
2. RFC está activo (no cancelado)
3. RFC NO está en 69-B EFOS

Necesitas conectar con servicios SAT.

---

## Servicios SAT disponibles

### Validador individual (web público)
- URL: https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf
- Input: RFC + CAPTCHA
- Output: existe / no existe + estatus
- Uso: manual, no automatizable directamente

### Validador masivo (con e.firma)
- URL: https://portalsat.plataforma.sat.gob.mx/ConsultaRFC/
- Input: archivo TXT con lista de RFCs (uno por línea)
- Autenticación: con e.firma (FIEL)
- Output: archivo TXT con resultado por RFC
- Uso: batch, hasta 10,000 RFCs por consulta

### Listado 69-B (descargable)
- URL: https://www.sat.gob.mx/consultas/97323/listado-de-contribuyentes-que-no-han-desvirtuado-la-presuncion
- Formato: XLSX descargable, actualizado periódicamente
- Contenido: contribuyentes EFOS publicados
- Categorías:
  - Definitivos
  - Presuntos
  - Desvirtuados (limpios)
  - Sentencia favorable
  - En sentencia firme

### Listado 69 (descargable)
Similar a 69-B pero para contribuyentes incumplidos en obligaciones (no EFOS específicamente).

---

## Implementación de validador masivo

### Opción 1: Manual con script auxiliar

```python
# scripts/validar-rfc-masivo.py
"""
Genera archivo TXT para validador masivo SAT desde lista de RFCs.
Luego de subir manualmente y descargar resultado, parsea respuesta.
"""

import argparse
from pathlib import Path

def generar_input(rfcs: list, output_path: Path) -> None:
    """Genera archivo TXT con un RFC por línea."""
    with output_path.open("w") as f:
        for rfc in rfcs:
            f.write(rfc.upper().strip() + "\n")

def parsear_output(input_path: Path) -> dict:
    """Parsea respuesta del SAT."""
    resultados = {}
    with input_path.open() as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                rfc = parts[0]
                estado = parts[1]  # ACTIVO, CANCELADO, NO_LOCALIZADO
                resultados[rfc] = {
                    "estado": estado,
                    "tipo_persona": parts[2] if len(parts) > 2 else None,
                }
    return resultados

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rfcs", nargs="+", help="Lista de RFCs")
    parser.add_argument("--input-file", help="Archivo con RFCs")
    parser.add_argument("--output", required=True, help="Path para archivo de salida")
    args = parser.parse_args()
    
    rfcs = args.rfcs or Path(args.input_file).read_text().splitlines()
    generar_input(rfcs, Path(args.output))
    print(f"Archivo generado en {args.output}")
    print(f"Sube manualmente a: https://portalsat.plataforma.sat.gob.mx/ConsultaRFC/")
```

### Opción 2: MCP server con automatización SAT

Si decides automatizar, requiere e.firma del SAT. El procedimiento:

```python
# mcp-servers/sat-rfc-validator.py
"""
MCP server que valida RFCs contra padrón SAT.
Requiere e.firma (.cer + .key + password).
"""

import os
from pathlib import Path
from fastmcp import FastMCP
from cryptography.hazmat.primitives import serialization
# ... otras imports para firma digital

mcp = FastMCP("sat-rfc-validator")

CER_PATH = os.getenv("SAT_CER_PATH")
KEY_PATH = os.getenv("SAT_KEY_PATH")
KEY_PASSWORD = os.getenv("SAT_KEY_PASSWORD")

@mcp.tool()
async def validar_rfcs_lote(rfcs: list[str]) -> dict:
    """Valida lote de RFCs contra padrón SAT.
    
    Args:
        rfcs: lista de RFCs a validar (max 10,000)
    
    Returns:
        dict {rfc: {estado, tipo_persona, nombre_si_disponible}}
    """
    # 1. Generar archivo input
    # 2. Firmar con e.firma
    # 3. POST al endpoint masivo SAT
    # 4. Esperar resultado (puede ser asíncrono)
    # 5. Parsear y retornar
    pass

@mcp.tool()
async def consultar_69b(rfc: str) -> dict:
    """Consulta si un RFC está en lista 69-B EFOS.
    
    Returns:
        dict con estatus en 69-B:
        - en_lista: bool
        - categoria: 'definitivo' | 'presunto' | 'desvirtuado' | etc.
        - fecha_publicacion: ISO date
    """
    # 1. Descargar listado 69-B (cache local diario)
    # 2. Buscar RFC en el listado
    # 3. Retornar status
    pass

if __name__ == "__main__":
    mcp.run()
```

### Opción 3: Servicios de terceros

Algunos PACs (Facturama, SW Sapien) ofrecen endpoints de validación de RFC como servicio agregado:

```python
# Ejemplo con Facturama
import httpx

async def validar_rfc_via_pac(rfc: str, api_key: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.facturama.mx/v1/Validation/RFC/{rfc}",
            headers={"Authorization": f"Basic {api_key}"},
        )
        return resp.json()
```

**Pros**: simple, sin manejo de e.firma.
**Contras**: costo por consulta, dependencia del PAC, posiblemente solo valida estructura no padrón vivo.

---

## Cache de validaciones

Validar al SAT en cada timbrado es ineficiente. Cachear localmente con expiración:

```python
# Pseudo-código de estrategia de cache
def get_rfc_status(rfc: str) -> dict:
    cache_path = Path(f"cache/rfc/{rfc}.json")
    
    if cache_path.exists():
        cached = json.loads(cache_path.read_text())
        age_days = (datetime.now() - parse(cached["fecha"])).days
        
        # Cache válido si < 90 días
        if age_days < 90:
            return cached["data"]
    
    # Refrescar consultando SAT
    fresh = consultar_sat(rfc)
    cache_path.write_text(json.dumps({
        "fecha": datetime.now().isoformat(),
        "data": fresh,
    }))
    return fresh
```

**Cache TTL recomendado por dato**:
- Existencia en padrón: 90 días (cambia raramente)
- Activo/Cancelado: 30 días
- 69-B EFOS: 7 días (publicación quincenal del SAT)

---

## Cómo manejar resultado de validación

### RFC existe + activo + no en 69-B
✅ Proceder normalmente.

### RFC existe + activo + en 69-B presunto
⚠ Alertar al usuario. Puede facturar pero hay riesgo de que el SAT desconozca el CFDI.
Recomendar: pedir al cliente que aclare situación o evite operación.

### RFC existe + activo + en 69-B definitivo
🛑 NO facturar. El SAT considerará operaciones simuladas. Riesgo legal grave.

### RFC existe pero cancelado
⚠ Alertar. El RFC fue dado de baja. No debería emitir/recibir CFDI activamente.

### RFC no existe en padrón
🛑 NO facturar. PAC rechazará.

---

## Frecuencia de actualización del listado 69-B

El SAT publica actualizaciones del 69-B aproximadamente cada 15 días en el portal:
https://www.sat.gob.mx/consultas/97323/

Tu sistema debería:
- Descargar el listado semanalmente
- Comparar contra clientes activos
- Alertar si algún cliente apareció nuevo en lista

---

## ⚠ Verificación vigente

- URLs del SAT pueden cambiar
- Formato de archivos respuesta puede actualizarse
- 69-B se publica periódicamente; el listado vigente es el último publicado

Si vas a automatizar contra SAT en producción, monitorear cambios en el portal y ajustar el integrador.

---

## Ver también

- `palabras-inconvenientes.md` — validación estructural
- Skill `rfc-validacion` — implementación principal
- [integracion-pac.md](../../../docs/integracion-pac.md) — algunos PACs validan RFC como bonus
