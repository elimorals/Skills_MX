# Tipos de cambio Banxico — consulta y aplicación

Cómo obtener el tipo de cambio oficial DOF para conversión de monedas en CFDI y contratos.

## Quién publica el tipo de cambio

**Banxico** (Banco de México) publica el tipo de cambio para solventar obligaciones denominadas en moneda extranjera (FIX). Este se publica en el **Diario Oficial de la Federación (DOF)** y es el **único válido** para CFDI según SAT.

## Tipos de tipo de cambio

| Tipo | Uso |
|---|---|
| **FIX** | Para liquidación de obligaciones (CFDI, contratos) |
| **Apertura** | Inicial del día |
| **Promedio** | Promedio del día (referencia estadística) |
| **Mediodía** | A las 12:00 hrs (FIX) |
| **Cierre** | De cierre del día |
| **24 hrs** | Promedio 24 hrs |

Para CFDI: **FIX del día hábil anterior** a la fecha del comprobante.

## API de Banxico

URL pública con datos históricos y actuales:
- Base: https://www.banxico.org.mx/SieAPIRest/service/v1/series/

### Series principales

| Serie | Descripción |
|---|---|
| **SF63528** | Tipo de cambio FIX |
| **SF60653** | Tipo de cambio para obligaciones en moneda extranjera |
| **SP74664** | Tipo de cambio MXN/EUR |
| **SP74665** | Tipo de cambio MXN/GBP |
| **SF46410** | Tipo de cambio MXN/CAD |
| **SF46406** | Tipo de cambio MXN/JPY |

### Endpoint para datos

```
GET https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF63528/datos/oportuno?token=TU_TOKEN

Headers:
  Accept: application/json
  Bmx-Token: tu_token_api
```

### Obtener token

1. https://www.banxico.org.mx/SieAPIRest/service/v1/token
2. Registro gratis con email
3. Token llega por email
4. Sin caducidad por uso normal

## Implementación de cliente

### Python con caché diario

```python
# scripts/banxico_tc.py
"""Cliente para tipo de cambio Banxico con caché diario."""

import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import httpx

CACHE_DIR = Path(".cache/banxico")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

TOKEN = os.getenv("BANXICO_TOKEN", "")

SERIES = {
    "USD/MXN": "SF63528",      # FIX
    "USD/MXN_OBLIG": "SF60653", # Para obligaciones
    "EUR/MXN": "SP74664",
    "GBP/MXN": "SP74665",
    "CAD/MXN": "SF46410",
    "JPY/MXN": "SF46406",
}

def get_tipo_cambio(par: str = "USD/MXN", fecha: date = None) -> float:
    """Obtiene tipo de cambio Banxico.
    
    Args:
        par: 'USD/MXN', 'EUR/MXN', etc.
        fecha: fecha objetivo (default: día hábil anterior a hoy)
    
    Returns:
        Tipo de cambio como float
    """
    if fecha is None:
        fecha = dia_habil_anterior(date.today())
    
    cache_key = f"{par.replace('/', '_')}_{fecha.isoformat()}.json"
    cache_path = CACHE_DIR / cache_key
    
    if cache_path.exists():
        return json.loads(cache_path.read_text())["valor"]
    
    serie = SERIES[par]
    url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/{fecha.isoformat()}/{fecha.isoformat()}"
    
    resp = httpx.get(url, headers={"Bmx-Token": TOKEN, "Accept": "application/json"})
    data = resp.json()
    
    valor = float(data["bmx"]["series"][0]["datos"][0]["dato"])
    
    cache_path.write_text(json.dumps({
        "par": par,
        "fecha": fecha.isoformat(),
        "valor": valor,
        "consultado_en": datetime.now().isoformat(),
    }))
    
    return valor

def dia_habil_anterior(fecha: date) -> date:
    """Retorna el día hábil anterior (excluye sábado, domingo).
    
    Nota: no excluye días festivos oficiales mexicanos. Para precisión SAT,
    considerar implementar calendario de festivos.
    """
    delta = 1
    while True:
        candidato = fecha - timedelta(days=delta)
        if candidato.weekday() < 5:  # 0=Mon, 4=Fri
            return candidato
        delta += 1
```

### MCP server

```python
# mcp-servers/banxico.py
from fastmcp import FastMCP
from datetime import date

mcp = FastMCP("banxico")

@mcp.tool()
async def tipo_cambio_dof(moneda: str = "USD", fecha: str = None) -> dict:
    """Obtiene tipo de cambio Banxico para una moneda y fecha.
    
    Args:
        moneda: 'USD', 'EUR', 'GBP', 'CAD', 'JPY'
        fecha: ISO date YYYY-MM-DD (default: día hábil anterior)
    
    Returns:
        dict con tipo_cambio, fecha_aplicable, fuente
    """
    par = f"{moneda}/MXN"
    if fecha:
        fecha_obj = date.fromisoformat(fecha)
    else:
        fecha_obj = dia_habil_anterior(date.today())
    
    valor = get_tipo_cambio(par, fecha_obj)
    
    return {
        "moneda_origen": moneda,
        "moneda_destino": "MXN",
        "tipo_cambio": valor,
        "fecha_aplicable": fecha_obj.isoformat(),
        "fuente": "Banxico (DOF)",
        "serie": SERIES[par],
    }

if __name__ == "__main__":
    mcp.run()
```

## Reglas de aplicación para CFDI

### CFDI estándar
Usar tipo de cambio del **día hábil anterior** a la fecha del CFDI.

Ejemplo:
- CFDI emitido el viernes 15 marzo 2026
- Tipo de cambio: el del **jueves 14 marzo 2026** (último día hábil anterior)

### CFDI emitido en fin de semana o feriado
El emisor debe esperar al siguiente día hábil para timbrar O usar el TC del último día hábil.

### Operaciones en USD con factura local
```xml
<cfdi:Comprobante 
    ...
    Moneda="USD"
    TipoCambio="18.5432"
    Total="10000.00">
```

El `TipoCambio` es el factor para convertir a MXN: `Total en MXN = Total USD × TipoCambio`.

### CFDI con concepto en una moneda y total en otra
NO permitido. Toda la factura va en una sola moneda.

### CFDI a tasa 0% por exportación
Aún así requiere TipoCambio si moneda ≠ MXN.

## Conversión inversa (MXN → otra moneda)

Si te pagan $10,000 MXN y quieres saber cuántos USD son:

```
USD = MXN / TipoCambio
USD = 10,000 / 18.5432
USD = $539.28
```

## Histórico de tipos de cambio

El DOF tiene archivo histórico en:
https://www.banxico.org.mx/tipcamb/

Útil para:
- Reconstruir contabilidad de meses anteriores
- Validar TC usado en CFDIs viejos
- Análisis de impacto cambiario

## Días en que el dólar puede no publicarse

- Días no hábiles del sistema bancario (festivos + fines de semana)
- Eventos extraordinarios (raros)

En estos casos: usar el último publicado.

## Variación intradía

El FIX se publica una vez al día. Si tu negocio es sensible a variación intradía (trading, alta volatilidad), considerar usar tipos de cambio comerciales (que sí varían continuamente). Pero para CFDI: SOLO el oficial Banxico/DOF.

## Diferencias cambiarias contables

Si emites CFDI hoy a $18.50 y cobras en 30 días a $19.30, la diferencia cambiaria genera:
- Utilidad cambiaria si tipo de cambio subió a tu favor
- Pérdida cambiaria si bajó

Esto se registra en contabilidad, no en CFDI.

## Conversión a letras en otra moneda

Para conversión a letras en USD/EUR:

```
($10,000.00 USD) DIEZ MIL DÓLARES AMERICANOS 00/100 USD
($5,500.50 EUR) CINCO MIL QUINIENTOS EUROS 50/100 EUR
```

Convención similar a MXN pero cambia la moneda en el sufijo.

## ⚠ Verificación vigente

- API de Banxico es estable hace años pero puede cambiar
- Series referenciadas pueden actualizarse
- Tokens pueden requerir renovación

Probar en sandbox antes de producción.

---

## Ver también

- `numeros-a-letra.md` — formato de letras
- Skill `mxn-formato` — implementación principal
- [glosario-fiscal-mx.md](../../../docs/glosario-fiscal-mx.md) — términos TC, DOF
