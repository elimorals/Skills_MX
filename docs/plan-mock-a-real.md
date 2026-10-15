# Plan: MCPs de mock a real + calidad de skills (2026-10-14)

Decisión de arquitectura: [ADR 008](adrs/008-estado-real-sin-fallback-silencioso.md). Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

Meta: que cada MCP responda con datos reales del upstream, y que las skills se
evalúen por la **corrección** de su respuesta, no solo por si se activan.

## Reglas para todo el trabajo

1. **Sin fallback silencioso a mock.** Si el upstream falla, se levanta
   `UpstreamError` (o se devuelve un error explícito). Datos simulados solo con
   `PLUGINS_MX_MOCK=1` y siempre marcados `simulated: true`.
2. **Validación en vivo obligatoria** para declarar un MCP "real": al menos una
   llamada real exitosa, registrada en el README del MCP (fecha, URL, status), y
   un test `@pytest.mark.live` (se salta salvo `PLUGINS_MX_LIVE=1`).
3. **CAPTCHA: entrega a humano por defecto.** Si el portal lo exige, el tool devuelve
   un handoff (URL + pasos). Con el solver opt-in (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha`)
   se resuelve el CAPTCHA del formulario; nunca se evaden anti-bots de red (Akamai,
   Cloudflare, Radware) ni se usa en citas o REPEP.
4. **Solo lectura en vivo.** Nada que presente declaraciones, agende citas,
   modifique obligaciones o mueva dinero contra un upstream real durante pruebas.
5. **Secretos fuera del repo.** Los tests generan una e.firma autofirmada al vuelo;
   la e.firma de prueba del SAT (comparaciones contra phpcfdi) se lee de
   `SAT_EFIRMA_PRUEBA_DIR`, fuera del repo. Nunca se imprime ni se commitea.

## Grupos (inventario de los 83 MCPs)

| Grupo | MCPs | Cómo se vuelve real | Validable hoy |
|---|---|---|---|
| A. SAT web services (e.firma) | sat_ws, sat_portal (descarga masiva, verificación CFDI) | SOAP firmado con XMLDSig | Sí, FIEL de prueba |
| B. SAT portal con e.firma | sat_portal (CSF, buzón, e.firma vigente), sat_opinion_32d, resico_sat, donatarias_sat | Login FIEL al portal + httpx | Sí, FIEL de prueba |
| C. Federales públicos (1) | curp_renapo, repuve, repse_stps, clabe_validador_oficial, banxico_cep, dof_api, cnbv_fintech, condusef_sipres, sep_profesional, impi_marcanet, no_antecedentes_penales_mx, form_filler_public | Endpoint público (HAR/REA) → httpx | Sí, sin login |
| D. Federales públicos (2) | cofepris, conagua_repda, cre_hidrocarburos, repep_profeco, concilianet_profeco, retys_catalogo, ine_verificacion, citas_monitor, portales_monitor, llave_mx, llave_mx_tracker, lnetb_auditor, simplifica_ciudadano, sedatu_uso_suelo, ley_silla_nom037, desconexion_digital, expediente_clinico_nom024, cfe_interconexion_solar | Igual que C; varios son cálculo normativo local | Sí, sin login |
| E1. Estatal/municipal (centro) | cdmx_municipal, edomex_municipal, predial_mx, tenencia_mx, verificacion_vehicular_mx, multas_mx, multas_vehiculares_mx, catastro_estatal_mx, isn_mx, ish_mx | Endpoints de consulta pública por placa/cuenta | Parcial (placa/cuenta de prueba) |
| E2. Estatal/municipal (resto) | guadalajara, monterrey, merida, puebla, queretaro, tijuana, sacpi_michoacan, agua_mx, gas_natural_mx | Igual que E1 | Parcial |
| F. APIs privadas documentadas | banxico (SIE), bitso, conekta, mercado_pago, mercado_libre, shopify_mx, amazon_mx_seller, paypal_mx, clip_terminal, cabify_business, trustly_mx, uber_eats_partners, facturama_extendido, kueski, klap, didi_partners, didi_food_partners, rappi_partners | Cliente contra la doc oficial + respx | Solo con API key de cada servicio |
| G. Login de usuario final | bancos_mx, buro_credito_personal, cfe_facturacion, telmex_facturacion, imss_patronal, imss_continuidad, infonavit_patronal, inmuebles24, vivanuncios | HAR capturado por el usuario + REA | **Bloqueado**: requiere credenciales y captura del usuario |
| H. Software local | aspel_contpaqi, softrestaurant | Lectura de archivos/BD locales | Con export de muestra |

## Oleadas

- **Oleada 1 (en paralelo):** A, B, C, D, E1, E2, F, y calidad de skills (evals de salida).
- **Oleada 2:** G. Necesita del usuario: credenciales de prueba por portal y un
  HAR de cada flujo (o sesión guiada), que se analiza con REA (`rea-agents`).
  Bancos: evaluar agregador (Belvo/Finerio) en vez de scraping.
- **Oleada 3:** extracción de PDFs (CSF, 32-D, recibos CFE/Telmex) con docling
  donde las skills reciben documentos.
