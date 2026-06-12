---
name: ficha-inmueble
description: Ficha técnica completa del inmueble con datos catastrales (cuenta predial, escritura, RPP), descripción comercial (atributos vendibles), fotos profesionales (mínimo 15), tour virtual, estado de conservación con honestidad, vecindad y entorno (escuelas, transporte, comercios). Usar cuando el usuario diga ficha inmueble, descripción casa para venta, datos catastrales, foto inmueble. NO usar para comparables (otro skill) ni contratos (otro skill).
allowed-tools: Read, Write, Edit
---

# Ficha del inmueble

## Datos catastrales (obligatorios)

```json
{
  "identificacion_legal": {
    "cuenta_predial": "1234567890",
    "valor_catastral_mxn": 4_500_000,
    "ultimo_pago_predial": "2026-01-15",
    "predial_al_corriente": true,
    "escritura_publica": {
      "numero": "12345",
      "notario_publico": 42,
      "fecha_otorgamiento": "2018-05-20",
      "registro_publico_de_la_propiedad": "Folio 654321"
    },
    "regimen_propiedad": "individual | condominio | familiar"
  }
}
```

## Datos físicos del inmueble

```json
{
  "tipo": "departamento",
  "uso": "habitacional",
  "metros": {
    "terreno": 0,  // departamento no aplica
    "construidos": 95,
    "balcones_terraza": 8
  },
  "habitaciones": 3,
  "baños": 2,
  "medios_baños": 1,
  "estacionamientos": 1,
  "bodega": false,
  "piso": 8,
  "edificio_pisos_totales": 15,
  "elevadores": 2,
  "antigüedad_años": 8,
  "estado_conservacion": "muy_bueno",  // excelente, muy_bueno, bueno, regular, requiere_remodelación
  "amenidades_edificio": [
    "alberca",
    "gimnasio",
    "salon_eventos",
    "seguridad_24h",
    "estacionamiento_visitas",
    "area_juegos_infantiles"
  ]
}
```

## Descripción comercial (para difusión)

### Estructura del listing
1. **Headline (60 chars max)**:
   - "Departamento moderno con vista en Polanco — 95m², 3 rec"
2. **Beneficios principales** (3-5 bullets):
   - "Vista panorámica al Parque Lincoln"
   - "Piso alto: aire fresco + privacidad"
   - "A 5 min caminando del Metro Polanco"
3. **Descripción larga** (500-1500 caracteres):
   - Atributos vendibles
   - Llamado a acción al final
4. **Fotos** (15 mínimo):
   - Foto exterior del edificio
   - Sala / comedor (2-3 ángulos)
   - Cocina
   - Cada habitación
   - Baños
   - Balcón / vista
   - Amenidades del edificio
5. **Tour virtual** (recomendado):
   - Matterport, 3D Vista
   - +50% más interesados que listing sin tour

## Honestidad en estado de conservación

### Excelente
- < 2 años desde construcción/remodelación
- Acabados premium intactos
- Ningún imperfecto evidente

### Muy bueno
- 2-10 años, mantenimiento al día
- Detalles pequeños posibles (pintura tocada, alfombra)

### Bueno
- 10-20 años, funcional
- Requiere actualización cosmética (pintura, alfombra, gabinetes)

### Regular
- 20+ años o con problemas significativos
- Requiere remodelación parcial (baños, cocina, pisos)

### Requiere remodelación
- 30+ años sin actualizar
- Plomería/electricidad obsoletas
- Estructura puede requerir refuerzo

⚠ Mentir al respecto = problema en avalúo bancario + cancelación de venta.

## Vecindad y entorno

```json
{
  "ubicacion_detalle": {
    "colonia": "Polanco",
    "ciudad": "CDMX",
    "estado": "CDMX",
    "cp": "11550"
  },
  "transporte_cercano": [
    {
      "tipo": "metro",
      "estacion": "Polanco",
      "distancia_caminando_min": 5
    },
    {
      "tipo": "metrobus",
      "linea": "L7",
      "distancia": 7
    }
  ],
  "comercios_cercanos": [
    {"tipo": "supermercado", "nombre": "Walmart Express", "distancia_min": 8},
    {"tipo": "starbucks", "distancia_min": 3},
    {"tipo": "restaurantes_premium", "count_500m": 25}
  ],
  "servicios": [
    {"tipo": "escuela_publica", "kinder_primaria_secundaria": "todas a 1-3 km"},
    {"tipo": "escuela_privada_premium", "anuhac_isb": "<5 km"},
    {"tipo": "hospital", "abc_y_angeles": "<3 km"},
    {"tipo": "centro_comercial", "antara_polanco": "10 min caminando"}
  ],
  "areas_verdes": [
    {"nombre": "Parque Lincoln", "distancia_min": 8},
    {"nombre": "Bosque de Chapultepec", "distancia_min": 15}
  ],
  "seguridad_zona_rating": 8.5
}
```

## Output estructurado

```json
{
  "ficha_inmueble_creada": {
    "id_inmueble": "INM-2026-0042",
    "tipo": "departamento",
    "ubicacion": "Polanco, CDMX",
    "metros_construidos": 95,
    "habitaciones": 3,
    "baños": 2,
    "datos_catastrales_completos": true,
    "predial_al_corriente": true,
    "estado_conservacion": "muy_bueno",
    "amenidades_count": 6,
    "fotos_capturadas": 22,
    "tour_virtual_disponible": true,
    "puntaje_atractivo_estimado": 8.5,
    "precio_sugerido_basado_en_comparables_mxn": 5_400_000,
    "descripcion_comercial_lista": true,
    "alertas": [
      "Predial 2026 ya pagado — ventaja en negociación",
      "Cuota mantenimiento $3,200/mes — informar a interesado"
    ]
  }
}
```

## Validación pendiente

- Software de tour virtual recomendado MX (Matterport, 3D Vista, etc.)
- Reglas de marketing inmobiliario CDMX (no engañar)
- Plataformas best-in-class para difusión

## Ver también

- `comparables-zona` para precio sugerido
- `mp_inmuebles24` para publicación
