---
name: verificacion-vehicular
description: Gestiona el calendario obligatorio de verificación vehicular en México (CDMX, EdoMex, Hidalgo, Morelos, Puebla principales) y alerta sobre próximas obligaciones. La verificación es semestral, varía el periodo por terminación de placa, y el costo varía por estado ($550-$700 típico). Verifica el último holograma obtenido (0, 1, 2, exento, doble) para determinar restricciones del programa Hoy No Circula. Usar cuando el usuario diga cuándo verifico mi auto, verificación pendiente, calendario verificación, holograma. NO usar para vehículos comerciales pesados (otra normativa).
allowed-tools: Read, Write
---

# Verificación vehicular — calendario y status

## Reglas generales MX (CDMX/EdoMex)

- **Frecuencia**: cada 6 meses (semestres ene-jun, jul-dic)
- **Calendario por terminación placa**:
  - 1 o 2 → enero/julio
  - 3 o 4 → febrero/agosto
  - 5 o 6 → marzo/septiembre
  - 7 o 8 → abril/octubre
  - 9 o 0 → mayo/noviembre
- **Plazo de gracia**: hasta último día del mes siguiente
- **Costo aproximado**: $550-$700 MXN

## Hologramas

| Holograma | Significado | Hoy No Circula CDMX |
|---|---|---|
| 0 / 00 | Vehículo nuevo (≤2 años) o eléctrico | NO aplica |
| Exento | Eléctrico / híbrido enchufable | NO aplica |
| 1 | Estándar | 1 día/semana + 1 sábado/mes |
| 2 | Mayor contaminación | 1 día/semana + 2 sábados/mes |

## Trigger

- "¿cuándo verifico?"
- "tengo holograma 1 o 2?"
- "qué día no circula mi auto?"

## Lógica

```python
def determinar_periodo(placa: str, ejercicio: int) -> tuple[str, date, date]:
    """Devuelve (semestre, fecha_inicio, fecha_fin)."""
    ultimo_digito = int(placa[-1]) if placa[-1].isdigit() else 0
    mes_map = {0: 5, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5}
    mes = mes_map[ultimo_digito]
    inicio_1 = date(ejercicio, mes, 1)
    fin_1 = ultimo_dia(ejercicio, mes + 1)
    inicio_2 = date(ejercicio, mes + 6, 1)
    fin_2 = ultimo_dia(ejercicio, mes + 7)
    # Determinar cuál aplica (siguiente)
    ...
```

## Output

```json
{
  "placa_hash": "...",
  "entidad": "edomex",
  "ultimo_holograma": "1",
  "ultima_verificacion": "2026-03-15",
  "proxima_verificacion": {
    "periodo": "septiembre-octubre 2026",
    "fecha_inicio": "2026-09-01",
    "fecha_fin": "2026-10-31",
    "dias_restantes": 90
  },
  "no_circula_dias": {
    "lunes": false,
    "martes": false,
    "miercoles": false,
    "jueves": true,
    "viernes": false,
    "sabados_mes": [1]
  },
  "costo_aproximado_mxn": "650.00",
  "verificentros_cercanos_sugeridos": "Buscar en aplicación oficial del estado"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Vehículo eléctrico | Exento, no requiere verificar |
| Placa fronteriza / extranjera | Aplica otras reglas |
| Placa con letras (privada vs publico) | Misma regla, pero verificentros distintos |
| Cambio de estado de registro | Re-aplicar reglas del nuevo estado |

## ⚠ Compliance

- Datos del programa Hoy No Circula CDMX cambiados a marzo 2023 — verificar vigencia
- No suplantar al portal oficial — solo prepara info
