# mp_guadalajara_municipal

## Tools

| Tool | Estado |
|---|---|
| `guadalajara_mun_consultar_predial(cuenta_predial)` | Handoff humano (`motivo: captcha`) |
| `guadalajara_mun_consultar_multas(placa)` | Handoff humano (`motivo: captcha`) — adeudos vehiculares estatales de Jalisco |

Los dos portales exigen reCAPTCHA. Por regla del proyecto no se intenta saltarlo: el
tool devuelve `requiere_humano: true`, la URL y los pasos.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://pagoenlinea.guadalajara.gob.mx/impuestopredial/main.js` | 200; `grecaptcha.render(...)` + verificación `rest/index.php/captcha/captcha` antes de `consulta_adeudo` |
| 2026-10-14 | `GET https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos` | 200; formulario `frmAdeudos` con reCAPTCHA |

Los tests `@pytest.mark.live` fallan si un portal quita el CAPTCHA (señal para implementar
la consulta directa). Mock solo con `PLUGINS_MX_MOCK=1`.
