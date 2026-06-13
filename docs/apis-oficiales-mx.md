# APIs oficiales mexicanas (alternativas al scraping con CAPTCHA bypass)

> **Propósito**: documentar las APIs autorizadas y legales que evitan
> tener que pasar CAPTCHAs en portales gubernamentales, bancarios y de
> reporting fiscal. Estas son las rutas que **sí** podemos automatizar
> sin riesgo legal ni técnico de bloqueo.
>
> **Fecha**: 2026-06-13
> **Aplica a**: MCPs `mp_sat_portal`, `mp_bancos_mx`, `mp_imss_patronal`,
> `mp_infonavit_patronal`, `mp_buro_credito_personal`.

---

## TL;DR — cuándo usar API oficial vs scraping vs humano

| Sistema | API oficial existe | Recomendación |
|---|---|---|
| SAT — descarga masiva CFDIs | ✅ Sí (con e.firma) | **Usar API oficial** — REST + SOAP autorizado |
| SAT — Buzón Tributario | ⚠ Solo lectura web | Sesión asistida + humano-en-loop |
| SAT — Verifica CFDI | ✅ Sí (público) | API REST sin auth (ya implementada) |
| SAT — Listas 69 y 69-B | ✅ Sí (público) | TXT descargable directo (ya implementada) |
| IMSS — IDSE | ✅ Sí (SOAP) | **Usar API oficial** — requiere registro patronal |
| IMSS — SUA, EMA, EMCA | ⚠ Web sin API | Humano-en-loop + parser archivos descargados |
| INFONAVIT — Portal Empresarial | ⚠ Web | Igual que IMSS |
| Bancos — Open Banking MX (CNBV) | 🟡 En desarrollo | **Usar cuando esté listo** — sandbox BBVA/Banorte ya |
| Bancos — Estados de cuenta CSV | ✅ Sí (descarga manual) | Parser local del archivo (no scraping) |
| Buró de Crédito — API B2B | ✅ Sí (solo empresas) | Requiere licencia SCIC + contrato comercial |

---

## 1. SAT — Descarga masiva de CFDIs (REST oficial)

### Endpoint
Producción: `https://prodservicios.cfdi.satgob.mx/V2/`
Documentación: `http://omawww.sat.gob.mx/tramitesyservicios/Paginas/descarga_masiva.htm`

### Flujo

```python
# 1. Autenticación con e.firma del cliente
# Requiere: certificado .cer + llave privada .key + contraseña
# El cliente FIRMA un "AuthHeader" con su llave privada — esto es legal
# y autorizado (no es bypass, es uso normal de su propia identidad).

from xml.etree import ElementTree as ET
from datetime import datetime, timedelta

def autenticar_sat(cer_path: str, key_path: str, password: str) -> str:
    """
    Genera token SAT firmando un timestamp con la llave privada del cliente.
    El token vive ~5 minutos — refrescar para llamadas largas.
    """
    # Implementación:
    # 1. Cargar .cer y .key del cliente (PKCS12 si vienen en .pfx)
    # 2. Crear AuthHeader XML con timestamp
    # 3. Firmar con XMLDSig RSA-SHA1
    # 4. POST a https://cfdidescargamasivasolicitud.clouda.sat.gob.mx/Autenticacion/Autenticacion.svc
    # 5. Recibir y cachear el token
    ...

# 2. Solicitud de descarga masiva
def solicitar_descarga_masiva(
    token: str,
    rfc: str,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    tipo: str,  # "emitidos" | "recibidos"
) -> str:
    """
    Devuelve solicitud_id. SAT procesa async (1-4 hrs típico, puede ser días).
    Endpoint: /SolicitaDescarga/SolicitaDescargaService.svc
    """
    ...

# 3. Verificar status
def verificar_solicitud(token: str, solicitud_id: str) -> dict:
    """
    Endpoint: /VerificaSolicitudDescarga/VerificaSolicitudDescargaService.svc
    Devuelve: { estado: "Aceptada"|"En proceso"|"Terminada"|"Error", paquetes: [ids] }
    """
    ...

# 4. Descargar paquetes ZIP cuando estado="Terminada"
def descargar_paquete(token: str, paquete_id: str) -> bytes:
    """
    Endpoint: /Descargas/DescargaService.svc
    Devuelve ZIP con XMLs de los CFDIs solicitados.
    """
    ...
```

### Por qué es la ruta correcta
- ✅ Es la vía OFICIAL que SAT diseñó para automatización
- ✅ Sin CAPTCHA, sin rate limits problemáticos
- ✅ La firma con e.firma del cliente ES legítima (es SU identidad)
- ✅ Auditoría queda en logs SAT — protección para todos
- ⚠ Requiere que el cliente comparta .cer/.key (con su consentimiento explícito y cifrado en reposo)

### Implementar en `mp_sat_portal`
Reemplazar el path Playwright actual por:
```python
# mp_sat_portal/efirma_api.py (NUEVO)
class SatEfirmaApi:
    def __init__(self, cer_path, key_path, password):
        ...
    def descargar_cfdis_masivo(self, rfc, periodo, tipo):
        # 4 pasos arriba
```

**Esfuerzo estimado**: 40-60h (firma XMLDSig es lo más complejo).
**Librerías útiles**: `cryptography`, `lxml`, `xmlsig`, `signxml`.

---

## 2. IMSS — IDSE (Integración Digital de Servicios al Empleador) SOAP

### Endpoint
Producción: `https://idse.imss.gob.mx/idsews/services/`
WSDL: `https://idse.imss.gob.mx/idsews/services/IDSE?wsdl`

### Capacidades
- Altas/bajas de empleados (Aviso de Inscripción de Trabajador AIT)
- Modificaciones de salario (MST)
- Reincorporaciones (ARE)
- Consulta cédula de determinación (CDR/EMA)
- Confirmaciones diferidas

### Requisitos
1. Patrón debe estar registrado en IMSS y dado de alta como usuario IDSE
2. Acceso vía e.firma del representante legal
3. Certificado IDSE separado (NO es la e.firma — IMSS lo emite específico para IDSE)

### Flujo

```python
from zeep import Client
from zeep.wsse.signature import Signature

def cliente_idse(cert_idse_path, key_path):
    """
    SOAP con WS-Security signature usando certificado IDSE del patrón.
    """
    client = Client(
        wsdl="https://idse.imss.gob.mx/idsews/services/IDSE?wsdl",
        wsse=Signature(key_path, cert_idse_path),
    )
    return client

def afiliar_trabajador(client, datos_trabajador: dict) -> dict:
    """
    Equivalente a "Movimiento Afiliatorio AIT".
    SOAP devuelve confirmación con folio_certificacion + estado.
    """
    response = client.service.AltaTrabajador(
        nss=datos_trabajador["nss"],
        curp=datos_trabajador["curp"],
        fecha_alta=datos_trabajador["fecha_alta"],
        sbc=datos_trabajador["salario_base_cotizacion"],
        registro_patronal=datos_trabajador["rp"],
    )
    return {"folio": response.Folio, "estado": response.Estado}
```

### Por qué es la ruta correcta
- ✅ IMSS publica el WSDL — usar es bienvenido
- ✅ Sin CAPTCHA (es B2B SOAP)
- ✅ Es la única vía que IMSS reconoce como "automatizada legítima"

**Esfuerzo estimado**: 60-100h.
**Librerías útiles**: `zeep`, `xmlsec`, `cryptography`.

---

## 3. Bancos MX — Open Banking CNBV (en evolución)

### Marco regulatorio
- **Ley Fintech 2018** Art. 76 — obliga a bancos a compartir datos vía API estandarizada
- **Disposiciones CNBV 2020** — establece estándar técnico (OAuth 2.0 + OpenID Connect)
- **Decreto Open Banking 2023** — fase 1 obligatoria desde julio 2023
- **Roadmap**: fase 2 (transaccional) prevista 2026, fase 3 (escritura) en discusión

### Bancos con sandbox público (2026)

| Banco | Sandbox URL | Endpoints disponibles | Producción |
|---|---|---|---|
| **BBVA** | https://www.bbvaapimarket.com | Cuenta, movimientos, CLABE | Sí (con contrato TPP) |
| **Banorte** | https://developers.banorte.com | Cuenta, movimientos | Sandbox |
| **Santander** | https://developer.santander.com.mx | Open data + cuentas | Sandbox |
| **HSBC** | https://developer.hsbc.com.mx | Limitado | Sandbox |
| **Banamex/Citi** | En desarrollo | — | — |

### Flujo OAuth 2.0 típico

```python
# 1. Registro como TPP (Third Party Provider) ante el banco
#    Requiere: empresa registrada, contrato, certificado QWAC opcional

# 2. Flujo Authorization Code con redirect del cliente
auth_url = (
    "https://api.bbva.com/oauth/authorize"
    "?response_type=code"
    "&client_id=TU_TPP_ID"
    "&redirect_uri=https://tu-app.com/callback"
    "&scope=accounts,transactions"
)
# Cliente autoriza en el banco → recibimos `code`

# 3. Exchange code por access_token
import httpx
response = httpx.post(
    "https://api.bbva.com/oauth/token",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://tu-app.com/callback",
        "client_id": "TU_TPP_ID",
        "client_secret": "TU_TPP_SECRET",
    },
)
access_token = response.json()["access_token"]  # ~30 min TTL

# 4. Consumir API
movs = httpx.get(
    "https://api.bbva.com/v1/accounts/{account_id}/transactions",
    headers={"Authorization": f"Bearer {access_token}"},
)
```

### Por qué es la ruta correcta vs scraping
- ✅ Legalmente obligatorio que los bancos lo expongan (Ley Fintech)
- ✅ Sin CAPTCHA, sin riesgo de bloqueo de cuenta
- ✅ Cliente consciente del consentimiento (autoriza explícitamente)
- ✅ Tokens revocables — cliente mantiene control
- ⚠ Requiere ser TPP autorizado para producción real

### Mientras tanto: parser de estados de cuenta CSV/PDF
Los clientes pueden descargar manualmente su estado de cuenta y nuestro MCP
lo parsea. **NO es scraping** — es procesamiento de un archivo que el cliente
nos dio voluntariamente.

```python
# mp_bancos_mx/csv_parser.py — NUEVO
def parse_estado_cuenta_bbva(csv_path: str) -> list[Movimiento]:
    """Parser del formato CSV oficial BBVA."""
    ...

def parse_estado_cuenta_santander(csv_path: str) -> list[Movimiento]:
    ...
```

**Esfuerzo estimado**: 80-120h para Open Banking real, 20-30h para parsers CSV de top 4 bancos.

---

## 4. Buró de Crédito — API B2B oficial

### Endpoint
Buró de Crédito SCIC: `https://www.burodecredito.com.mx/empresas-api.html`
Círculo de Crédito (alternativo): `https://www.circulodecredito.com.mx/api`

### Requisitos NO negociables
1. Empresa con razón social mexicana
2. Licencia SCIC (Sociedad de Información Crediticia)
3. Contrato comercial con Buró + cuota mensual
4. **Autorización del titular obligatoria** (Art. 28 LRSIC) — sin esto es DELITO
5. Almacenamiento de la autorización por 12 meses

### Estructura
```python
class BuroSCICReporteSimple:
    """Reporte simplificado — el formato completo es propietario."""
    def consultar(
        self,
        rfc_titular: str,
        autorizacion_token: str,  # firmada digitalmente por titular
        proposito: str,  # "credito_inicio", "credito_renovacion", "monitoreo"
    ) -> dict:
        """
        Devuelve: score, deudas activas, historial 24m, alertas.
        Cliente recibe copia gratuita del reporte (Art. 41 LRSIC).
        """
        ...
```

### El MCP actual (mp_buro_credito_personal) YA lo hace bien
El schema Pydantic exige `autorizacion_token` válido — esto cumple con la ley.
NO requiere CAPTCHA bypass — requiere ser TPP autorizado.

**Conclusión**: la implementación actual en mock-mode + el schema obligatorio
es la postura legalmente correcta. Activar producción requiere:
1. Crear empresa con licencia SCIC
2. Contratar con Buró/Círculo
3. Implementar flujo de autorización (envío SMS al titular + firma)

---

## 5. Patrón "humano-en-loop" para flujos NO automatizables

Algunas operaciones simplemente NO se pueden automatizar legalmente (firma e.firma
en SAT para algunos trámites, MFA dinámica del banco, OTP). Para estos casos,
patrón recomendado:

```python
# 1. El agente PREPARA todo (forms llenos, documentos)
estado = agente.preparar_tramite(...)
# → genera URL + screenshots + datos pre-llenados

# 2. El agente envía notificación al cliente (WhatsApp / email):
#    "Listo para finalizar tu refrendo CDMX. Click aquí para confirmar (válido 30 min)"
agente.solicitar_confirmacion_humana(cliente, estado)

# 3. El cliente abre la URL, hace el paso final con sus credenciales
#    El agente NO ve credenciales — el cliente las teclea él mismo

# 4. El cliente vuelve y dice "listo"; agente continúa con el siguiente paso
agente.continuar_tras_confirmacion(estado)
```

Esto es **legal, seguro y escalable** — el cliente mantiene control de sus
credenciales sensibles, el agente automatiza todo lo demás.

---

## 6. Roadmap recomendado de migración (3 meses, ~6,000 USD inversión total)

| Mes | Acción | Resultado |
|---|---|---|
| 1 | Implementar `mp_sat_portal/efirma_api.py` con descarga masiva REST | Reemplazar Playwright SAT actual |
| 1 | Parsers CSV de top 4 bancos | mp_bancos_mx funcional sin scraping |
| 2 | Implementar `mp_imss_patronal/idse_soap.py` | IMSS legalmente automatizado |
| 2 | Patrón humano-en-loop estándar | Para flujos no automatizables |
| 3 | Sandbox Open Banking BBVA + Banorte | Camino futuro |
| 3 | Documentar restricciones Buró | Compliance OK |

---

## 7. Lo que ESTOS docs NO autorizan

Para evitar ambigüedad:

- ❌ Bypassear CAPTCHAs en cualquier portal gubernamental/bancario
- ❌ Almacenar credenciales bancarias del cliente sin Open Banking
- ❌ Consultar Buró sin autorización firmada del titular
- ❌ Suplantar e.firma de cliente (uso normal con su consentimiento sí)
- ❌ Patrones de masking de browser fingerprint (es evidencia de mala fe ante CNBV)

Si necesitas ALGUNO de estos, NO es nuestro proyecto. Hay servicios oscuros
que ofrecen esto y se llaman "bullet-proof scraping" — siempre terminan con
demanda penal contra el operador.

---

## 8. Referencias normativas

- **CFF Art. 30** — conservación de comprobantes 5 años
- **CFF Art. 86** — sanciones por uso indebido de servicios SAT
- **Ley Fintech Art. 17, 76** — Open Banking obligatorio
- **LFPDPPP Art. 8, 32** — consentimiento explícito para datos personales
- **LRSIC Art. 28** — autorización obligatoria para Buró
- **NOM-151-SCFI-2016** — conservación digital con sello tiempo
- **CPF Art. 211 bis** — fraude informático (lo que se evita NO bypassing CAPTCHAs)

— Sesión 2026-06-13
