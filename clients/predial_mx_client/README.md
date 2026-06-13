# predial_mx_client — Cliente Python standalone

Librería Python pura para consultar predial municipal en México sin necesidad
de Claude Code ni MCP. Usable desde Django, FastAPI, scripts, notebooks, etc.

## Instalación

```bash
# Si está en el repo plugins-mx:
cp -r clients/predial_mx_client /your-app/
# o instalable con pip si lo publicas:
pip install predial-mx-client  # futuro
```

Requisitos:
- Python 3.10+
- Si quieres consultas reales: `pip install playwright && playwright install chromium`

## Uso básico

```python
from predial_mx_client import PredialMxClient

# Modo mock (default — sin red, respuestas simuladas)
client = PredialMxClient(modo="mock")

# Consulta
r = client.consultar(estado="jal", municipio="guadalajara", cuenta="U12345678")
print(f"Adeudo: ${r.adeudo_total_mxn:,.2f} MXN")
print(f"Al corriente: {r.al_corriente}")
print(f"Bimestres pendientes: {r.bimestres_pendientes}")

# Listar municipios validados
for m in client.listar_validados():
    print(f"{m.estado}/{m.clave}: {m.nombre} ({m.poblacion_aprox:,} hab)")

# Búsqueda fuzzy
for m in client.buscar("guadal"):
    print(m.nombre)

# Estadísticas
stats = client.estadisticas()
print(f"Total municipios: {stats['municipios_totales']}")
print(f"Cobertura validada: {stats['cobertura_efectiva']}")
```

## Modo real (consultas reales con Playwright)

```python
import os
os.environ["MP_PLAYWRIGHT_PUBLIC"] = "1"

client = PredialMxClient(modo="real")
r = client.consultar(estado="jal", municipio="guadalajara", cuenta="U_REAL_AQUÍ")
print(r.adeudo_total_mxn)  # consulta real al portal
```

## Casos especiales

### Municipio con CAPTCHA (Puebla)
```python
from predial_mx_client import PredialMxClient, CaptchaRequeridoError

client = PredialMxClient(modo="real")
try:
    r = client.consultar("pue", "puebla", "12345")
except CaptchaRequeridoError as e:
    print(f"Requiere humano. Abre: {e.url_consulta_manual}")
```

### Mérida busca por dirección (no por cuenta)
```python
r = client.consultar(
    estado="yuc", municipio="merida",
    cuenta="",  # no se usa para Mérida
    direccion="Calle 60 # 123",
)
```

### SACPI Michoacán (95 municipios via 1 plataforma)
```python
# Cualquier municipio MICH del catálogo SACPI:
r = client.consultar(estado="mich", municipio="hidalgo_mich", cuenta="034001", tipo="urbano")
```

## Error handling

```python
from predial_mx_client import (
    PredialMxClient,
    NoSoportadoError,    # municipio no en catálogo
    CaptchaRequeridoError,  # requiere CAPTCHA humano
    PortalCaidoError,    # portal no responde
)

client = PredialMxClient(modo="real")
try:
    r = client.consultar("xx", "fake", "123")
except NoSoportadoError as e:
    print(f"No soportado: {e}")
except CaptchaRequeridoError as e:
    print(f"Captcha en: {e.url_consulta_manual}")
except PortalCaidoError as e:
    print(f"Portal caído: {e}")
```

## Integración con Django

```python
# views.py
from django.http import JsonResponse
from predial_mx_client import PredialMxClient

_client = PredialMxClient(modo="mock")  # o "real" si quieres consultar de verdad

def consultar_predial(request):
    estado = request.GET["estado"]
    municipio = request.GET["municipio"]
    cuenta = request.GET["cuenta"]
    try:
        r = _client.consultar(estado, municipio, cuenta)
        return JsonResponse({
            "adeudo": r.adeudo_total_mxn,
            "al_corriente": r.al_corriente,
            "bimestres_pendientes": r.bimestres_pendientes,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
```

## API completa

| Método | Descripción |
|---|---|
| `consultar(estado, municipio, cuenta, [tipo, direccion])` | Consulta predial — devuelve `PredialResponse` |
| `listar_municipios([estado], [solo_validados])` | Lista todos o filtrados — devuelve `list[MunicipioInfo]` |
| `listar_validados([estado])` | Atajo: solo validados |
| `buscar(query)` | Búsqueda fuzzy por nombre |
| `estadisticas()` | Stats del catálogo (dict) |
| `es_soportado(estado, municipio)` | bool — ¿en catálogo? |
| `es_validado(estado, municipio)` | bool — ¿URL real verificada? |

## Cobertura del catálogo (2026-06-13)

- **209 municipios** catalogados
- **33 validados** con URL real verificada
- **95 muns MICH adicionales** via SACPI (plataforma estatal)
- **128 consultables** efectivamente
- **31.4M habitantes** cubierta (24.2% nacional)

## Licencia + advertencias

⚠ Consulta predial es información pública, pero el USO COMERCIAL masivo
(>1000 consultas/día) puede violar términos del portal del municipio.
Para producción a escala, gestionar acuerdo formal con ayuntamientos.

⚠ Datos del propietario (nombre, dirección, RFC) que aparezcan en respuesta
son DATOS PERSONALES bajo LFPDPPP. No almacenar sin consentimiento del titular.
