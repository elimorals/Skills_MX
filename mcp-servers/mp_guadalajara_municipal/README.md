# mp_guadalajara_municipal

## Tools

| Tool | Estado |
|---|---|
| `guadalajara_mun_consultar_predial(cuenta_predial, recaudadora?, tipo?)` | Con solver opt-in: real sin validar en vivo (falta llave). Sin solver: handoff humano (`motivo: captcha`) |
| `guadalajara_mun_consultar_multas(placa, numero_serie?, nombre_propietario?, numero_motor?)` | Igual — adeudos vehiculares estatales de Jalisco |

Los dos portales exigen reCAPTCHA. Sin solver, el tool devuelve `requiere_humano: true`,
la URL y los pasos. Con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`
(ver `shared/captcha_solver.py`) se pide el token a 2captcha y se consulta; si el portal
rechaza el token se reintenta 2 veces y luego `UpstreamError`. Si faltan los datos que el
portal exige (predial: recaudadora 1-4 y tipo U/R; Jalisco: ≥5 caracteres de serie) se
devuelve el handoff.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://pagoenlinea.guadalajara.gob.mx/impuestopredial/main.js` | 200; `grecaptcha.render(...)` + verificación `rest/index.php/captcha/captcha` antes de `consulta_adeudo` |
| 2026-10-14 | `GET https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos` | 200; formulario `frmAdeudos` con reCAPTCHA |
| 2026-10-14 | mismos GET (descubrimiento para el solver) | ver abajo |

**Predial — con solver opt-in: real sin validar en vivo (falta llave).**
- reCAPTCHA **v2** checkbox, sitekey `6LfPYOQrAAAAAG4wXEmhHL070x0BHcOHQU0GIKUc` (de `main.js`; se re-extrae en vivo).
- El token va en el form `response` a `POST https://aytoapi.guadalajara.gob.mx/rest/index.php/captcha/captcha`
  → `{"success": bool}` (`false` = token rechazado).
- Después `POST https://apipagoenlinea.guadalajara.gob.mx/predialApi/consulta_adeudo`
  (form `recaudadora`, `tipo`, `cuenta`, `correo`, `version`) → `{status, tipo, message, data}`;
  `data` trae `importe`, `fecha_limite`, `linea_captura`, `adeudos`, `ClaveCatastral`, domicilio y valores.
  Según el bundle, `consulta_adeudo` no recibe el token: la verificación es la llamada previa.

**Adeudos vehiculares Jalisco — con solver opt-in: real sin validar en vivo (falta llave).**
- Sitekey `6LehxCgfAAAAAE_6lvOTiXBtQNZCyc37CLZssnzC`, action `submit`. El botón usa el patrón
  de reCAPTCHA v3 (`class="g-recaptcha"` + `data-action`), no checkbox: se pide token v3
  (`JAL_RECAPTCHA_VERSION`); si 2captcha no lo resuelve, cambiar a `v2`.
- `POST /serviciosVehiculares/adeudos` (form `origen=normal`, `accion=getAdeudos`, `placa`,
  `numeroSerie`, `nombrePropietario`, `numeroMotor`, `g-recaptcha-response`). Los errores del
  servidor llegan en `<div id="error">`; si mencionan captcha se trata como token rechazado.
- La página de resultado no se ha visto (no se enviaron datos de terceros): el tool devuelve
  las filas de las tablas tal cual con `formato_resultado_validado: false`.

Los tests `@pytest.mark.live` fallan si un portal quita el CAPTCHA (señal para implementar
la consulta directa). Los live con solver requieren `TWOCAPTCHA_API_KEY` y datos propios en
`GDL_PREDIAL="recaudadora,tipo,cuenta"` / `JAL_VEHICULO="placa,serie,nombre,motor"`.
Mock solo con `PLUGINS_MX_MOCK=1`.
