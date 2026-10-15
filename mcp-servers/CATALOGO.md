# Catálogo de MCPs — plugins-mx

**Última actualización**: 2026-10-14 (oleada 1: mock → real)
**Total MCPs**: 83

El estado de cada MCP sale de la sección "Estado real" de su README. La tabla de abajo la genera `scripts/generar-estado-mcps.py`; no se edita a mano.

<!-- estado-mcps:inicio -->
### Estado a 2026-10-14 (oleada 1: mock → real)

Generado por `scripts/generar-estado-mcps.py` desde la sección "Estado real" de cada README. 83 MCPs, 417 tools.

| Categoría | MCPs |
|---|---|
| Real, validado en vivo | 24 |
| Real sin validar (requiere credenciales) | 13 |
| Entrega a humano (CAPTCHA o login) | 17 |
| Sin API pública | 6 |
| Cálculo normativo verificado | 10 |
| Bloqueado | 2 |
| Sin verificar | 11 |

| MCP | Estado | Nota | Tools |
|---|---|---|---|
| `mp_agua_mx` | Real, validado en vivo | Parcial: JMAS Juárez real; SIAPA con reCAPTCHA; CESPT da 404; OOAPAS sin parser validado. | `agua_consultar_adeudo`, `agua_listar_organismos`, `agua_buscar_por_estado`, `agua_estadisticas` |
| `mp_amazon_mx_seller` | Real sin validar (requiere credenciales) | Rutas SP-API verificadas (Orders, Listings, Fees); falta una app SP-API autorizada. | `amazon_mx_list_listings`, `amazon_mx_get_listing`, `amazon_mx_update_inventory`, `amazon_mx_list_orders`, `amazon_mx_get_order`, `amazon_mx_get_fees_estimate`, `amazon_mx_listar_catalogos` |
| `mp_aspel_contpaqi` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `aspel_listar_polizas`, `aspel_get_poliza`, `aspel_obtener_balanza`, `aspel_obtener_catalogo_cuentas`, `aspel_obtener_estado_resultados`, `aspel_obtener_balance_general`, `aspel_parsear_export_csv`, `aspel_obtener_instrucciones_configuracion`, `aspel_listar_catalogos` |
| `mp_bancos_mx` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `bancos_listar_soportados`, `bancos_descargar_estado_cuenta`, `bancos_listar_movimientos`, `bancos_verificar_pago_por_referencia` |
| `mp_banxico` | Real sin validar (requiere credenciales) | SIE API v1 real; requiere BANXICO_TOKEN gratuito. Mock usa UMA 2026 = 117.31. | `banxico_get_tc_dof`, `banxico_get_tc_dia_habil_anterior`, `banxico_convertir_monto`, `banxico_get_uma`, `banxico_get_inpc`, `banxico_get_tiie_28`, `banxico_listar_monedas_soportadas` |
| `mp_banxico_cep` | Real, validado en vivo | Consulta de estado y 'no encontrado' validadas; descarga de un SPEI existente sin validar. Handoff si vuelve el CAPTCHA. | `banxico_cep_validar_clabe`, `banxico_cep_decodificar_clabe`, `banxico_cep_parsear_clave_rastreo`, `banxico_cep_lookup_banco`, `banxico_cep_generar_cep`, `banxico_cep_validar_cep`, `banxico_cep_descargar_pdf`, `banxico_cep_consultar_pago_por_clave`, `banxico_cep_listar_bancos`, `banxico_cep_listar_catalogos` |
| `mp_bitso` | Real, validado en vivo | Ticker, order book y pares públicos validados en vivo sin llaves (2026-10-14); endpoints privados requieren BITSO_API_KEY/SECRET. | `bitso_get_ticker`, `bitso_get_order_book`, `bitso_list_available_books`, `bitso_get_account_status`, `bitso_get_balance`, `bitso_get_fees`, `bitso_get_ledger`, `bitso_list_fundings`, `bitso_list_withdrawals`, `bitso_list_open_orders`, `bitso_calcular_isr_cripto_mx`, `bitso_listar_catalogos` |
| `mp_buro_credito_personal` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `buro_consultar_score`, `buro_descargar_reporte_completo`, `buro_monitorear_alertas`, `buro_listar_catalogos` |
| `mp_cabify_business` | Real sin validar (requiere credenciales) | Reescrito contra la API oficial v4 (estimates, journey, sales); falta sandbox. Sin listado de viajes ni CFDI. | `cabify_estimar`, `cabify_pedir_viaje`, `cabify_consultar_viaje`, `cabify_estado_viaje`, `cabify_cancelar_viaje`, `cabify_ventas_viaje`, `cabify_listar_catalogos` |
| `mp_catastro_estatal_mx` | Entrega a humano (CAPTCHA o login) | IGECEM: handoff; IRCEP sin DNS; IRCNL y OVICA exigen login. | `catastro_consultar_valor`, `catastro_listar_sistemas` |
| `mp_cdmx_municipal` | Entrega a humano (CAPTCHA o login) | Predial (ALTCHA) y tenencia/multas (CAPTCHA de imagen): handoff. Hoy No Circula: cálculo local. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `cdmx_consultar_predial`, `cdmx_consultar_tenencia`, `cdmx_consultar_multas`, `cdmx_consultar_hoy_no_circula`, `cdmx_listar_catalogos` |
| `mp_cfe_facturacion` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `cfe_descargar_factura_mes`, `cfe_consumo_historico`, `cfe_validar_session` |
| `mp_cfe_interconexion_solar` | Cálculo normativo verificado | Umbrales de la LSE (DOF 18-03-2025); sin tarifas ni folios inventados. | `cfe_solar_solicitar`, `cfe_solar_estatus`, `cfe_solar_simular_ahorro`, `cfe_solar_listar_tarifas` |
| `mp_citas_monitor` | Entrega a humano (CAPTCHA o login) | SAT exige sesión, SRE tiene Radware Captcha, IMSS sin DNS, INE informativo. No reserva citas. | `citas_listar_portales`, `citas_generar_consent_token`, `citas_crear_alerta`, `citas_revisar_cupos`, `citas_estadisticas_eticas` |
| `mp_clabe_validador_oficial` | Real, validado en vivo | Catálogo SPEI de Banxico validado en vivo. | `clabe_validador_validar_clabe`, `clabe_validador_info_banco_clabe` |
| `mp_clip_terminal` | Real sin validar (requiere credenciales) | Reescrito contra developer.clip.mx (payments, refunds, devices, settlements); falta credencial de pruebas. | `clip_list_charges`, `clip_get_charge`, `clip_refund_charge`, `clip_terminal_status`, `clip_get_settlement`, `clip_listar_catalogos` |
| `mp_cnbv_fintech` | Real, validado en vivo | Padrón PES de la CNBV validado; no publica RFC; sin fuente para modelos novedosos. | `cnbv_fintech_consultar_itf`, `cnbv_fintech_listar_ifpe`, `cnbv_fintech_listar_ifc`, `cnbv_fintech_listar_modelos_novedosos`, `cnbv_fintech_verificar_contraparte` |
| `mp_cofepris_aviso_funcionamiento` | Cálculo normativo verificado | Constantes de la LGS (reforma DOF 15-01-2026); giros por Acuerdo SSA sin cotejar. | `cofepris_clasificar_giro`, `cofepris_requisitos_aviso`, `cofepris_consultar_aviso`, `cofepris_listar_giros` |
| `mp_conagua_repda` | Real, validado en vivo | Consulta REPDA (ASP.NET, sin CAPTCHA) validada en vivo. | `repda_consultar_titular`, `repda_estado_reporte`, `repda_calcular_lfd`, `repda_vigencia`, `repda_requiere_medidor`, `repda_listar_tipos_uso` |
| `mp_concilianet_profeco` | Real, validado en vivo | PDFs de Concilianet y Buró Comercial validados en vivo. | `concilianet_consultar_proveedor`, `concilianet_buro_quejas`, `concilianet_estatus_caso`, `concilianet_listar_proveedores`, `concilianet_registrar_queja` |
| `mp_condusef_sipres` | Real, validado en vivo | SIPRES validado en vivo (requiere extra truststore por TLS incompleto). | `sipres_buscar_institucion`, `sipres_verificar_autorizada` |
| `mp_conekta` | Real sin validar (requiere credenciales) | Rutas API 2.1.0 coinciden con la doc oficial; falta llave sandbox. | `conekta_create_order`, `conekta_get_order`, `conekta_list_orders`, `conekta_create_charge_on_order`, `conekta_refund_order`, `conekta_create_customer`, `conekta_get_customer`, `conekta_create_payment_link`, `conekta_subscription_create`, `conekta_subscription_update`, `conekta_subscription_cancel`, `conekta_validate_webhook`, `conekta_listar_catalogos` |
| `mp_cre_hidrocarburos` | Real, validado en vivo | XML público de precios/permisos (15,046 estaciones) validado en vivo. | `cre_consultar_permiso`, `cre_calendar_reporte`, `cre_evaluar_anexo30`, `cre_reportar_zeros`, `cre_listar_tipos_permiso` |
| `mp_curp_renapo` | Entrega a humano (CAPTCHA o login) | gob.mx/curp con challenge Akamai y reCAPTCHA Enterprise; validación local de la CURP. Solver opt-in conectado, pero hoy bloquea un anti-bot de red antes del captcha (CURP: Akamai; INE: Cloudflare) y queda en handoff. | `curp_validar_estructura`, `curp_derivar_fecha_nacimiento`, `curp_derivar_sexo`, `curp_derivar_estado`, `curp_validar_lote`, `curp_generar_desde_datos`, `curp_consultar_renapo`, `curp_consultar_renapo_por_datos`, `curp_descargar_constancia_renapo`, `curp_listar_catalogos` |
| `mp_desconexion_digital` | Cálculo normativo verificado | LFT vigente: desconexión solo en teletrabajo (Art. 330-E); no existe la 'reforma Art. 132 marzo 2026'. | `desconexion_checklist`, `desconexion_generar_politica`, `desconexion_template_capacitacion` |
| `mp_didi_food_partners` | Sin API pública | DiDi Food no publica API de comercios; con credenciales devuelve ConfigError. | `didi_food_listar_ordenes`, `didi_food_consultar_orden`, `didi_food_listar_productos_menu`, `didi_food_actualizar_disponibilidad`, `didi_food_consultar_ranking_zona`, `didi_food_estimar_comisiones_mes` |
| `mp_didi_partners` | Sin API pública | DiDi no publica API para conductores; con credenciales devuelve ConfigError. | `didi_partners_listar_viajes`, `didi_partners_consultar_viaje`, `didi_partners_comisiones_mes` |
| `mp_dof_api` | Real, validado en vivo | API JSON de SIDOF validada; búsqueda por título recorriendo sumarios diarios. | `dof_sumario_dia`, `dof_buscar_texto`, `dof_detalle_nota`, `dof_monitorear_por_keyword`, `dof_listar_dependencias_comunes` |
| `mp_donatarias_sat` | Real, validado en vivo | Directorio XLSX del SAT validado (10,017 RFC); no incluye revocaciones posteriores al corte. | `donatarias_consultar`, `donatarias_buscar`, `donatarias_listar_por_entidad`, `donatarias_estadisticas`, `donatarias_listar_rubros` |
| `mp_edomex_municipal` | Real, validado en vivo | Parcial: predial Toluca real; tenencia y multas handoff; Ecatepec, Naucalpan e Izcalli fallan. | `edomex_consultar_predial`, `edomex_consultar_tenencia`, `edomex_consultar_multas`, `edomex_listar_catalogos` |
| `mp_expediente_clinico_nom024` | Cálculo normativo verificado | NOM-024, NOM-004 y LGS verificadas; Reglamento de Insumos sin cotejar. | `ece_generar_receta`, `ece_verificar_medico`, `ece_validar_sistema`, `ece_consentimiento_paciente` |
| `mp_facturama_extendido` | Real sin validar (requiere credenciales) | Rutas verificadas contra el cliente de satcfdi; falta cuenta sandbox. | `facturama_validar_payload_local`, `facturama_timbrar_cfdi`, `facturama_cancelar_cfdi`, `facturama_consultar_estatus`, `facturama_descargar_xml`, `facturama_descargar_pdf`, `facturama_buscar_cfdis`, `facturama_listar_catalogos` |
| `mp_form_filler_public` | Entrega a humano (CAPTCHA o login) | Ya no abre navegador ni envía formularios: devuelve URL, pasos y campos prellenados. | `form_listar_formularios`, `form_validar_inputs`, `form_llenar` |
| `mp_gas_natural_mx` | Real, validado en vivo | Parcial: tarifas Ecogas (PDF) validadas; otros distribuidores sin fuente → upstream_error. | `gas_consultar_recibo`, `gas_tarifas_vigentes`, `gas_listar_distribuidores` |
| `mp_guadalajara_municipal` | Entrega a humano (CAPTCHA o login) | Predial y adeudos vehiculares con reCAPTCHA. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `guadalajara_mun_consultar_predial`, `guadalajara_mun_consultar_multas` |
| `mp_impi_marcanet` | Real, validado en vivo | MARCia (IMPI) validado en vivo, sin CAPTCHA ni login. | `impi_buscar`, `impi_verificar_denominacion` |
| `mp_imss_continuidad` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `imss_continuidad_listar_sistemas`, `imss_continuidad_health_check`, `imss_continuidad_plan`, `imss_continuidad_reporte_ejecutivo` |
| `mp_imss_patronal` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `imss_consultar_avisos_pendientes`, `imss_enviar_movimiento_afiliatorio`, `imss_descargar_cedula_autodeterminacion`, `imss_consultar_emcr`, `imss_consultar_sbc`, `imss_consultar_padron_trabajadores`, `imss_sbc_calcular`, `imss_ema_vs_eba_diferencias`, `imss_calendario_obligaciones`, `imss_simulador_costo_patronal`, `imss_riesgo_trabajo_prima_cambio`, `imss_listar_catalogos` |
| `mp_ine_verificacion` | Entrega a humano (CAPTCHA o login) | Lista nominal con Cloudflare y reCAPTCHA v2; no se evade. Solver opt-in conectado, pero hoy bloquea un anti-bot de red antes del captcha (CURP: Akamai; INE: Cloudflare) y queda en handoff. | `ine_verificar_datos`, `ine_verificar_qr`, `ine_consultar_vigencia`, `ine_generar_autorizacion`, `ine_listar_modelos` |
| `mp_infonavit_patronal` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `infonavit_consultar_creditos_trabajadores`, `infonavit_descargar_emis`, `infonavit_consultar_descuentos_mensuales`, `infonavit_consultar_avisos_pendientes`, `infonavit_descuento_calcular`, `infonavit_creditos_sin_reporte`, `infonavit_emis_historico`, `infonavit_conciliacion_nomina`, `infonavit_listar_catalogos` |
| `mp_inmuebles24` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `inm24_buscar_inmuebles`, `inm24_obtener_detalle`, `inm24_buscar_comparables_zona`, `inm24_publicar_listing`, `inm24_listar_catalogos` |
| `mp_ish_mx` | Cálculo normativo verificado | Cálculo local; tasas 2026 contra fuentes secundarias (confianza media, varias en conflicto). | `ish_calcular`, `ish_info_estado`, `ish_listar_estados`, `ish_comparar_estados` |
| `mp_isn_mx` | Cálculo normativo verificado | Cálculo local; tasas 2026 contra fuente secundaria. | `isn_calcular`, `isn_listar_estados`, `isn_info_estado`, `isn_generar_linea_captura`, `isn_descargar_declaracion` |
| `mp_klap` | Sin API pública | Sin documentación pública de API; con credenciales devuelve ConfigError. | `klap_listar_pagos`, `klap_consultar_pago` |
| `mp_kueski` | Sin API pública | API solo para comercios afiliados; con credenciales devuelve ConfigError. | `kueski_listar_pagos`, `kueski_consultar_pago`, `kueski_cancelar_pago` |
| `mp_ley_silla_nom037` | Cálculo normativo verificado | LFT (Ley Silla DOF 19-12-2024), NOM-035, NOM-037 y UMA 2026 verificadas. | `silla_verificar_compliance`, `silla_calcular_multa`, `silla_generar_politica`, `silla_listar_obligaciones` |
| `mp_llave_mx` | Real sin validar (requiere credenciales) | Login con CAPTCHA; el canje de token requiere convenio con la ATDT. Estadísticas de adopción leídas de datos.gob.mx. | `llave_iniciar_oauth`, `llave_estado_endpoints`, `llave_estadisticas_adopcion`, `llave_validar_token`, `llave_listar_tramites`, `llave_detalle_tramite`, `llave_vincular_e_firma` |
| `mp_llave_mx_tracker` | Real, validado en vivo | Revisión de portadas de 20 portales validada en vivo; solo mira la portada. | `llave_mx_listar_dependencias`, `llave_mx_estatus_dependencia`, `llave_mx_estadisticas_nacionales`, `llave_mx_verificar_en_vivo` |
| `mp_lnetb_auditor` | Cálculo normativo verificado | Plazos de los transitorios de la LNETB (DOF 16-07-2025); se retiraron scores por estado sin fuente. | `lnetb_listar_indicadores`, `lnetb_plazos_legales`, `lnetb_evaluar_estado`, `lnetb_ranking_nacional`, `lnetb_comparar_estados` |
| `mp_mercado_libre` | Real sin validar (requiere credenciales) | Rutas cotejadas; reputación corregida a GET /users/{id} → seller_reputation. Falta app OAuth. | `mercadolibre_get_me`, `mercadolibre_list_items`, `mercadolibre_get_item`, `mercadolibre_update_stock`, `mercadolibre_update_price`, `mercadolibre_pause_item`, `mercadolibre_activate_item`, `mercadolibre_list_orders`, `mercadolibre_get_order`, `mercadolibre_list_messages`, `mercadolibre_send_message`, `mercadolibre_list_questions`, `mercadolibre_answer_question`, `mercadolibre_get_seller_reputation`, `mercadolibre_listar_catalogos` |
| `mp_mercado_pago` | Real sin validar (requiere credenciales) | Rutas coinciden con la doc oficial (preferences, payments/search, refunds); falta access token de prueba. | `mercadopago_create_preference`, `mercadopago_get_preference`, `mercadopago_get_payment`, `mercadopago_list_payments`, `mercadopago_refund_payment`, `mercadopago_cancel_payment`, `mercadopago_validate_webhook_signature`, `mercadopago_listar_catalogos` |
| `mp_merida_municipal` | Entrega a humano (CAPTCHA o login) | Predial detrás de Radware Bot Manager con hCaptcha. | `merida_mun_consultar_predial` |
| `mp_monterrey_municipal` | Real, validado en vivo | Predial (ASP.NET, sin CAPTCHA) validado con expediente inexistente; tabla de adeudo sin ver con caso real. | `nl_consultar_predial`, `nl_listar_catalogos` |
| `mp_multas_mx` | Entrega a humano (CAPTCHA o login) | CDMX, EdoMex, Jalisco y San Pedro con CAPTCHA; NL solo refrendo. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `multas_consultar`, `multas_estados_disponibles` |
| `mp_multas_vehiculares_mx` | Entrega a humano (CAPTCHA o login) | CDMX, EdoMex, Jalisco y San Pedro con CAPTCHA; NL consulta manual. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `multas_consultar_por_placa`, `multas_calcular_total`, `multas_listar_sistemas` |
| `mp_no_antecedentes_penales_mx` | Entrega a humano (CAPTCHA o login) | Sin verificador público consultable (CDMX); EdoMex sin DNS. | `noantecedentes_verificar_constancia`, `noantecedentes_verificar_apto` |
| `mp_paypal_mx` | Real sin validar (requiere credenciales) | Cliente contra el OpenAPI oficial (transactions, balances); falta app REST con credenciales. | `paypal_mx_listar_transacciones`, `paypal_mx_consultar_transaccion`, `paypal_mx_balance` |
| `mp_portales_monitor` | Real, validado en vivo | Chequeo HTTP de 25 portales validado en vivo; los detrás de Akamai necesitan navegador con ventana. | `portales_listar`, `portales_check_http`, `portales_check_form_render`, `portales_health_dashboard`, `portales_configurar_alerta` |
| `mp_predial_mx` | Real, validado en vivo | Parcial: Toluca real; CDMX handoff (ALTCHA); resto del catálogo no revalidado en esta oleada. | `predial_consultar`, `predial_listar_municipios`, `predial_buscar_municipio`, `predial_estadisticas_catalogo` |
| `mp_puebla_municipal` | Entrega a humano (CAPTCHA o login) | Predial con CAPTCHA. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `puebla_mun_consultar_predial` |
| `mp_queretaro_municipal` | Real, validado en vivo | Endpoints JSON del portal validados con clave ficticia, sin CAPTCHA. | `queretaro_mun_consultar_predial` |
| `mp_rappi_partners` | Real sin validar (requiere credenciales) | Cliente contra el dev-portal; credenciales solo para aliados aprobados. Ranking y comisiones: sin endpoint. | `rappi_listar_ordenes`, `rappi_consultar_orden`, `rappi_listar_productos_menu`, `rappi_actualizar_disponibilidad`, `rappi_consultar_ranking_zona`, `rappi_estimar_comisiones_mes` |
| `mp_repep_profeco` | Entrega a humano (CAPTCHA o login) | El portal tiene controles anti-automatización deliberados; no se emulan. | `repep_consultar`, `repep_filtrar_lote`, `repep_inscribir`, `repep_estadisticas` |
| `mp_repse_stps` | Real, validado en vivo | Búsqueda y padrón REPSE validados en vivo. | `repse_consultar_por_razon_social`, `repse_consultar_por_numero_registro`, `repse_verificar_proveedor` |
| `mp_repuve` | Entrega a humano (CAPTCHA o login) | reCAPTCHA v3 y body cifrado en el navegador; robo devuelve null (desconocido), nunca false. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `repuve_consultar_niv`, `repuve_consultar_placa`, `repuve_verificar_robado` |
| `mp_resico_sat` | Cálculo normativo verificado | Cálculo local sobre tablas LISR; la tasa de retención de plataformas y el criterio 'SCJN 2026' están sin verificar. | `resico_calcular_isr`, `resico_evaluar_estatus`, `resico_calendario`, `resico_retencion_plataforma`, `resico_solicitar_devolucion`, `resico_listar_tasas`, `resico_listar_plataformas` |
| `mp_retys_catalogo` | Real, validado en vivo | Validado solo con Chromium con ventana (Akamai bloquea headless y httpx). | `retys_listar_sectores`, `retys_buscar_tramite`, `retys_detalle_tramite`, `retys_exportar_dcat`, `retys_buscar_en_vivo` |
| `mp_sacpi_michoacan` | Bloqueado | Host sacpi.michoacan.gob.mx sin DNS (NXDOMAIN); selectores de 2026-06 sin revalidar. | `sacpi_consultar`, `sacpi_listar_municipios`, `sacpi_codigo_municipio` |
| `mp_sat_opinion_32d` | Real, validado en vivo | Consulta pública 32-D validada; descarga propia con e.firma sin validar. | `sat_opinion_32d_consultar`, `sat_opinion_32d_verificar_proveedor`, `sat_opinion_32d_descargar_propia` |
| `mp_sat_portal` | Real, validado en vivo | Parcial: listas 69 y 69-B validadas; login e.firma (CSF, padrón, vigencia) sin validar con e.firma real; buzón y acuses no implementados. | `sat_consultar_padron`, `sat_consultar_69b_efos`, `sat_consultar_69_incumplidos`, `sat_verificar_cfdi_uuid`, `sat_validar_uuid_estructura`, `sat_descargar_csf`, `sat_descargar_buzon_tributario`, `sat_descargar_cfdi_masivo`, `sat_agendar_cita`, `sat_verificar_efirma_vigente`, `sat_descargar_acuse`, `sat_actualizar_obligaciones`, `sat_listar_catalogos`, `sat_calendario_fiscal_por_regimen`, `sat_cfdi_prevalidar`, `sat_declaraciones_historico`, `sat_devolucion_estatus`, `sat_buzon_tributario_resumen` |
| `mp_sat_ws` | Real sin validar (requiere credenciales) | Firma y autenticación validadas con e.firma de prueba; solicitud/descarga con e.firma real sin validar. | `sat_ws_solicitar_descarga`, `sat_ws_verificar_solicitud`, `sat_ws_descargar_paquete` |
| `mp_sedatu_uso_suelo` | Entrega a humano (CAPTCHA o login) | Sin consulta pública nacional de uso de suelo; devuelve pasos con permitido: null. | `sedatu_buscar_tramite`, `sedatu_consultar_uso_suelo`, `sedatu_estimar_construccion`, `sedatu_listar_tramites` |
| `mp_sep_profesional` | Entrega a humano (CAPTCHA o login) | Cédula profesional exige token reCAPTCHA; resultado null (desconocido) con handoff. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `sep_consultar_cedula`, `sep_consultar_por_datos`, `sep_validar_medico_para_consulta`, `sep_listar_profesiones_reguladas` |
| `mp_shopify_mx` | Real sin validar (requiere credenciales) | REST Admin API; versión por defecto subida a 2026-07 (2024-10 sin soporte). Falta tienda de desarrollo. | `shopify_list_products`, `shopify_get_product`, `shopify_get_inventory_level`, `shopify_update_inventory_level`, `shopify_list_orders`, `shopify_get_order`, `shopify_create_fulfillment`, `shopify_get_customer`, `shopify_list_webhooks`, `shopify_calculate_tax_mx`, `shopify_listar_catalogos` |
| `mp_simplifica_ciudadano` | Bloqueado | No hay fuente pública del avance por estado; fuera de mock devuelve ConfigError. | `simplifica_estado`, `simplifica_tracker_nacional`, `simplifica_comparar_estados` |
| `mp_softrestaurant` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `softrest_corte_z`, `softrest_ventas_periodo`, `softrest_inventario_actual`, `softrest_platillos_vendidos`, `softrest_meseros_ventas`, `softrest_mesas_estatus`, `softrest_parsear_export`, `softrest_listar_catalogos` |
| `mp_telmex_facturacion` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `telmex_descargar_factura`, `telmex_consumo_historico`, `telmex_listar_facturas` |
| `mp_tenencia_mx` | Cálculo normativo verificado | Cálculo local; montos 2026 de notas de prensa (confianza media o baja); se retiraron estados sin fuente. | `tenencia_calcular`, `tenencia_info_estado`, `tenencia_listar_estados`, `tenencia_comparar_estados` |
| `mp_tijuana_municipal` | Real, validado en vivo | Consulta de vivienda asegurada validada en vivo, sin CAPTCHA. | `tijuana_mun_consultar_predial`, `tijuana_mun_consultar_vivienda_asegurada` |
| `mp_trustly_mx` | Sin API pública | Trustly no opera en México; con credenciales devuelve ConfigError. | `trustly_create_payment`, `trustly_get_payment`, `trustly_list_payments`, `trustly_refund_payment`, `trustly_listar_catalogos` |
| `mp_uber_eats_partners` | Sin API pública | La doc de la Marketplace API no es pública; con credenciales devuelve ConfigError. | `uber_eats_listar_ordenes`, `uber_eats_consultar_orden`, `uber_eats_listar_productos_menu`, `uber_eats_actualizar_disponibilidad`, `uber_eats_consultar_ranking_zona`, `uber_eats_estimar_comisiones_mes` |
| `mp_verificacion_vehicular_mx` | Entrega a humano (CAPTCHA o login) | Estatus CDMX con CAPTCHA; calendario y costos 2026 de notas de prensa. Con solver opt-in (2captcha): consulta real, sin validar en vivo (falta llave). | `verificacion_consultar_estatus`, `verificacion_proximo_periodo`, `verificacion_listar_programas` |
| `mp_vivanuncios` | Sin verificar | El README no tiene sección 'Estado real' de la oleada 1. | `viv_buscar_anuncios`, `viv_obtener_detalle`, `viv_publicar_anuncio`, `viv_listar_catalogos` |
<!-- estado-mcps:fin -->

---

# Histórico (2026-06-15, previo a la oleada 1)

> Todo lo que sigue describe el catálogo antes de la oleada 1: tiers, "mock-first", conteos de tests y validaciones de junio 2026. No se revalidó y en varios casos ya no es cierto (tools borradas, MCPs reclasificados). Se conserva como referencia.

## Convención de Tier

| Tier | Definición | Criterios |
|---|---|---|
| **S** | Producción crítica | Path real implementado · 100% tests pasando · cobertura nacional alta · validación experta o portal estable >12 meses |
| **A** | Producción con human-in-loop | Path real con CAPTCHA/cookies/MFA · tests pasando · operativo bajo supervisión |
| **B** | Catálogo + mock-first | Discovery validado en vivo · selectores documentados · path real opt-in pero parser puede requerir calibración |
| **C** | Mock-only definitivo | Portal no expone consulta pública · solo app móvil o login-only · mantenido como referencia |

## Tabla maestra (76 MCPs)

### Tier S — Producción crítica (7)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_banxico` | Federal financiero | Universal | ✅ | ✅ REST | TCs DOF + UMA + INPC + TIIE diario |
| `mp_facturama_extendido` | CFDI 4.0 | 5.5M PyMEs | ✅ | ✅ REST | Sandbox + producción |
| `mp_mercado_pago` | Pagos | Universal | ✅ | ✅ REST + HMAC | Webhooks idempotentes |
| `mp_mercado_libre` | Marketplace | 50k+ vendedores activos MX | ✅ | ✅ REST | Listings + órdenes + mensajes |
| `mp_curp_renapo` | Identidad | 130M habitantes | ✅ | ✅ Estructural + Playwright | CURP estructural real + RENAPO stub |
| `mp_banxico_cep` | SPEI | Universal | ✅ | ✅ REST/form-POST | CLABE + CEP |
| `mp_sat_opinion_32d` | Compliance fiscal | 5.5M PyMEs | ✅ | ✅ HTTP público | Opinión 32-D sin captcha |

### Tier A — Producción con human-in-loop (10)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_cfe_facturacion` | Servicios públicos | 42M usuarios CFE | ✅ | ✅ Playwright + CAPTCHA + cookies | Human-in-loop CAPTCHA · sesión 30 min |
| `mp_telmex_facturacion` | Servicios públicos | 15M líneas Telmex | ✅ | ✅ Playwright + reCAPTCHA v3 invisible | `pago_sin_login` sin credenciales del usuario |
| `mp_verificacion_vehicular_mx` | Fiscal vehicular | 8M veh zonas verificación | ✅ | ✅ SAF CDMX calibrado | 7 estados · parser calibrado en vivo 2026-06-15 |
| `mp_agua_mx` | Servicios públicos | ~50% pob urbana | ✅ | ✅ SIAPA Playwright | 17 organismos · 2 públicos (JMAS Juárez + OOAPAS Morelia) |
| `mp_conekta` | Pagos | Universal | ✅ | ✅ REST | Charges + refunds + suscripciones |
| `mp_shopify_mx` | Marketplace | 30k tiendas | ✅ | ✅ REST | Wrapper específico MX |
| `mp_bitso` | Cripto | 4M cuentas | ✅ | ✅ REST | Calculadora ISR cripto |
| `mp_sep_profesional` | Validación profesional | Médicos/abogados/etc | ✅ | ✅ HTTP público | Sin captcha — desbloquea telemedicina-mx |
| `mp_repse_stps` | Compliance laboral | 4M empresas formales | ✅ | ✅ HTTP público | Art. 15 LFT subcontratación |
| `mp_dof_api` | Compliance horizontal | Despachos legales/contables | ✅ | ✅ HTTP público | Sumario diario + búsqueda full-text |

### Tier B — Catálogo + mock-first con discovery validado (33)

#### B.1 Fiscal estatal y vehicular (7)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_tenencia_mx` | Fiscal vehicular | 40M vehículos | ✅ | Cálculo + tablas | 20 estados con tasa + factor depreciación |
| `mp_ish_mx` | Fiscal estatal | 100k anfitriones Airbnb | ✅ | Cálculo | ISH 32 estados (27 cobran, 5 sin) |
| `mp_isn_mx` | Fiscal estatal | 4M empresas formales | ✅ | 8 estados Playwright | 32 estados catalogados |
| `mp_multas_vehiculares_mx` | Fiscal vehicular | ~22M vehículos | ✅ | CDMX (SAF reusado) | 5 sistemas: CDMX + EdoMex + NL ICVNL + NL San Pedro + JAL |
| `mp_catastro_estatal_mx` | Inmobiliario | Notarías + peritos | ✅ | Mock | 10 sistemas — patrón nacional confirmado no-público |
| `mp_predial_mx` | Municipal | 35.2M hab (26.7% nacional) | ✅ | 71 muns Playwright validados | 243 muns catalogados |
| `mp_multas_mx` | Fiscal vehicular | 8 estados | ✅ | Mock + reCAPTCHA opt-in | Catálogo legacy |

#### B.2 Compliance y registros (7)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_donatarias_sat` | Compliance fiscal | ~10k donatarias + donantes | ✅ | Mock + Akamai diferido | Anexo 14 RMF — CFDI uso D04 |
| `mp_cnbv_fintech` | Compliance regulatorio | Ecosistema fintech/cripto | ✅ | Mock + catálogo curado | ITF Ley Fintech (IFPE/IFC) |
| `mp_no_antecedentes_penales_mx` | Compliance identidad | Reclutamiento corporativo | ✅ | Playwright stub | Carta no antecedentes federal |
| `mp_repuve` | Compliance vehicular | 40M veh | ✅ | Playwright stub | Registro público vehicular |
| `mp_condusef_sipres` | Compliance financiero | Ecosistema financiero | ✅ | Playwright stub | SIPRES entidades financieras |
| `mp_impi_marcanet` | Propiedad intelectual | Marcas registradas | ✅ | Playwright stub | Marcanet IMPI |
| `mp_sat_ws` | Web Services SAT | CFDI emisores | ✅ | Stub + e.firma | Web Services oficiales |

#### B.3 Municipales individuales (8)

Refactorizados al catálogo central `shared/catalogo_municipios_mx.py`. Se mantienen por backward compat.

| MCP | Cobertura | Tests | Path real |
|---|---|---|---|
| `mp_cdmx_municipal` | CDMX 16 alcaldías | ✅ | Mock + validado |
| `mp_edomex_municipal` | EdoMex | ✅ | Mock |
| `mp_monterrey_municipal` | Monterrey | ✅ | Mock |
| `mp_guadalajara_municipal` | Guadalajara | ✅ | Mock |
| `mp_merida_municipal` | Mérida | ✅ | Playwright validado |
| `mp_puebla_municipal` | Puebla | ✅ | Mock |
| `mp_queretaro_municipal` | Querétaro | ✅ | Playwright validado |
| `mp_tijuana_municipal` | Tijuana | ✅ | Login-only (Sprint D) |

#### B.4 Marketplaces e inmobiliario (4)

| MCP | Categoría | Universo MX | Tests | Path real |
|---|---|---|---|---|
| `mp_amazon_mx_seller` | Marketplace | Sellers MX | ✅ | LWA + 6 endpoints |
| `mp_inmuebles24` | Inmobiliario | ~30k inmobiliarias | ✅ | Playwright real |
| `mp_vivanuncios` | Inmobiliario + autos | Multi-categoría | ✅ | Mock |
| `mp_buro_credito_personal` | Crédito personal | Reclutamiento + arrendamiento | ✅ | Mock + autorización Pydantic |

#### B.5 Pagos extendidos (4)

| MCP | Categoría | Tests | Path real |
|---|---|---|---|
| `mp_paypal_mx` | Pagos | ✅ | Mock + REST stub |
| `mp_klap` | POS alterno | ✅ | Mock |
| `mp_kueski` | Crédito BNPL | ✅ | Mock |
| `mp_trustly_mx` | Open banking | ✅ | Mock + REST stub |

#### B.6 SACPI y agregadores estatales (1)

| MCP | Cobertura | Tests | Path real |
|---|---|---|---|
| `mp_sacpi_michoacan` | 95 muns Michoacán | ✅ | Playwright real (95:1 ratio) |

#### B.7 Identidad bancaria (1)

| MCP | Categoría | Tests | Path real |
|---|---|---|---|
| `mp_clabe_validador_oficial` | CNBV reverso CLABE | ✅ | ✅ REST |

### Tier C — Mock-only definitivo (12)

Portales no exponen consulta pública. Mantenidos como referencia + scaffolding para clientes que tengan credenciales propias.

| MCP | Razón mock-only | Tests | Notas |
|---|---|---|---|
| `mp_imss_patronal` | IDSE requiere e.firma + MFA empresarial | ✅ | Cliente provee credenciales |
| `mp_infonavit_patronal` | Igual IMSS | ✅ | Cliente provee credenciales |
| `mp_bancos_mx` | BBVA/Banamex/Santander cierran scraping | ✅ | Esqueleto Playwright |
| `mp_gas_natural_mx` | Naturgy/ENGIE solo app móvil + WhatsApp | ✅ | Sprint C hallazgo negativo |
| `mp_sat_portal` | SAT bloquea bots agresivamente | ✅ | 4/11 HTTP públicos reales |
| `mp_aspel_contpaqi` | Solo CSV exports | ✅ | Parser sin API directa |
| `mp_softrestaurant` | Solo CSV exports | ✅ | Parser sin API directa |
| `mp_cabify_business` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_didi_partners` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_didi_food_partners` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_rappi_partners` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_uber_eats_partners` | API restringida a partners | ✅ | Cliente provee credenciales |

---

## Sprint E — 14 MCPs nuevos (Tier P0–P3 normativa 2026)

Lote agregado 2026-06-15 cubriendo bloqueadores normativos críticos para 2026 (Ley Silla NOM-037, RESICO, ECE NOM-024, desconexión digital), identidad ciudadana (Llave MX, INE), energía renovable (CFE solar, CRE), recursos naturales (CONAGUA), consumidor (PROFECO REPEP/Concilianet), urbano (SEDATU) y tracker de simplificación estatal.

### Tier A · Validado vivo Playwright (1)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_llave_mx` | Identidad ciudadana | 130M habitantes | ✅ | ✅ OAuth2 form real | Validado `llave.gob.mx/oauthV2.xhtml` — selectores `frmLogin:txtCorreo`, `frmLogin:txtPassword`, sin captcha. JSF + PrimeFaces. 20 trámites catalogados (identidad/fiscal/salud/vivienda/etc.) |

### Tier B · Discovery validado parcialmente (4)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_conagua_repda` | Recursos naturales | ~500k titulares | ✅ | Mock + REPDA público | Tarifa LFD 2026 por zona 1-9 ($27.50-$0.62/m³). Umbral medidor 150k m³/año |
| `mp_repep_profeco` | Consumidor | 130M habitantes | ✅ | Mock + portal público | Normalización teléfonos +52; filtro lote ≤5000 |
| `mp_concilianet_profeco` | Consumidor | 130M habitantes | ✅ | Mock + 32 proveedores convenio | Aeroméxico, Volaris, Telcel, Liverpool, Rappi, BBVA, etc. |
| `mp_cre_hidrocarburos` | Energía | ~12k permisionarios | ✅ | Mock + RUPETH público | Umbral Anexo 30 = 75,714 L/mes; calendario 10 primeros días hábiles |

### Tier C · Mock + calculadora/validador (8)

Sin portal público a scrapear — son calculadoras normativas, validadores de cumplimiento, generadores de plantilla legal o trackers estadísticos.

| MCP | Categoría | Razón Tier C | Tests |
|---|---|---|---|
| `mp_ley_silla_nom037` | Compliance laboral | Calculadora multas LFT (UMA 2026 117.31) + checklist Ley Silla/NOM-035/037 + generador política SST | ✅ |
| `mp_expediente_clinico_nom024` | Salud digital | Validador 10 requisitos NOM-024 + clasificador medicamentos COFEPRIS (fracciones I-V) | ✅ |
| `mp_resico_sat` | Fiscal | Calculadora ISR mensual 5 tramos (1.00-2.50%) + alerta tope $3.5M + 12 plataformas digitales retención 2.5% | ✅ |
| `mp_ine_verificacion` | Identidad | Portal INE solo informativo (B2G/B2B vía convenio) — validado vivo 2026-06-15 | ✅ |
| `mp_cfe_interconexion_solar` | Energía renovable | Simulador ahorro + tarifas DAC/PDBT/GDMTH (factor exportación 0.70 vigente 2026) | ✅ |
| `mp_desconexion_digital` | Compliance laboral | Checklist desconexión en teletrabajo (LFT 330-E fr. VI + NOM-037 5.2) + política + plantilla capacitación | ✅ |
| `mp_cofepris_aviso_funcionamiento` | Salud | Clasificador 19 giros A/B/C (NOM-167-SSA1) — portal Digipro requiere login | ✅ |
| `mp_sedatu_uso_suelo` | Inmobiliario/Urbano | Catálogo 6 trámites + 13 usos suelo + estimador MIA/EIU/MIV (>10k m²) — competencia municipal varía | ✅ |
| `mp_simplifica_ciudadano` | Tracker estatal | Avance Ley Nacional Trámites Burocráticos (DOF 16-jul-2025) en 32 estados — sin fuente pública: solo mock | ⚠️ |

### Tier S · Cobertura federal anclada en SAT (1)

| MCP | Categoría | Tests | Path real | Notas |
|---|---|---|---|---|
| `mp_resico_sat` (calculadora) | Promovido a S para empresas <$3.5M MXN | ✅ | Cálculo + calendario | Cubre el 78% del padrón RFC PyMEs MX |

> **Nota de honestidad**: `mp_resico_sat` aparece dos veces — como **calculadora/validador Tier C** (sin scraping al portal SAT) y como **Tier S funcional** porque su lógica de tasas RESICO está validada contra LISR 2026 Art. 113-E. La duplicidad refleja que un mismo paquete puede tener valor operativo S aunque su path técnico sea C.

---

## Métricas globales

- **Path real validado en vivo Playwright**: 20 MCPs (incluye `mp_llave_mx` validado 2026-06-15)
- **Catálogo + mock con discovery documentado**: 39 MCPs (incluye 4 Sprint E Tier B)
- **Mock-only definitivo + calculadoras/validadores normativos**: 21 MCPs (incluye 9 Sprint E Tier C)
- **Tests totales**: 1,514 pasando (1,380 anteriores + 134 Sprint E)
- **Cobertura normativa 2026**: Ley Silla NOM-037 + ECE NOM-024 + RESICO + Desconexión Digital + Simplifica + Anexo 30 CRE

---

## Sprint F — Profundización SAT/IMSS/INFONAVIT (14 tools nuevos)

Lote agregado 2026-06-15 cubriendo los gaps de profundización del plan original (sección 3): operación mensual del agente `auditor-fiscal-mx` (SAT) + compliance laboral profundo (IMSS + INFONAVIT).

### `mp_sat_portal` — +5 tools

| Tool | Implementación | Tests |
|---|---|---|
| `sat_calendario_fiscal_por_regimen` | Local · 4 regímenes (601/605/612/626) · fechas día 17 + anual | ✅ 5 |
| `sat_cfdi_prevalidar` | Local · valida 10 elementos requeridos CFDI 4.0 + complementos PAGO/NOMINA/CARTAPORTE | ✅ 5 |
| `sat_declaraciones_historico` | Mock + e.firma · alerta RESICO 3 omisiones (SCJN 2026) | ✅ 3 |
| `sat_devolucion_estatus` | Mock + e.firma · 6 fases + plazo legal 40 días hábiles | ✅ 3 |
| `sat_buzon_tributario_resumen` | Mock + e.firma · conteo urgentes 5d + vencidas + Art. 17-K CFF | ✅ 2 |

### `mp_imss_patronal` — +5 tools

| Tool | Implementación | Tests |
|---|---|---|
| `imss_sbc_calcular` | Local · factor integración + tope 25 UMAs ($2,826.75/d 2026) | ✅ 5 |
| `imss_ema_vs_eba_diferencias` | Mock + e.firma · DIFERENCIA_CUOTAS/MOV_NO_APLICADO/INTERESES_MORA | ✅ 2 |
| `imss_calendario_obligaciones` | Local · 12 mensuales + 6 bimestrales + anual RT | ✅ 3 |
| `imss_simulador_costo_patronal` | Local · 9 cuotas LSS + INFONAVIT + provisiones LFT · factor real | ✅ 3 |
| `imss_riesgo_trabajo_prima_cambio` | Local · fórmula Art. 72 LSS + tope ±1% Art. 74 | ✅ 4 |

### `mp_infonavit_patronal` — +4 tools

| Tool | Implementación | Tests |
|---|---|---|
| `infonavit_descuento_calcular` | Local · 5 tipos crédito + cap LFT Art. 110 (30% SBC) | ✅ 6 |
| `infonavit_creditos_sin_reporte` | Mock · intereses moratorios 1.8%/mes estimados | ✅ 3 |
| `infonavit_emis_historico` | Mock · hasta 10 años bimestral · PAGADO/OMISO | ✅ 3 |
| `infonavit_conciliacion_nomina` | Local + mock · hasta 5000 registros · diff por trabajador | ✅ 4 |

**Total Sprint F**: 14 tools nuevos · 51 tests · 174/174 pasando en los 3 MCPs.

### Lo que sigue NO implementado del plan original

Ningún gap del Top 15 ni de la sección 3 queda pendiente. Próxima frontera (no estaba en el plan):
- Path real Playwright para SAT/IMSS/INFONAVIT (requiere e.firma del cliente — opt-in B2B)
- Empaquetamiento comercial + landing pricing + primer piloto pagante (recomendación honesta sección 7 del plan)

---

## Sprint G — 5 productos gobierno B2G (2026-06-15)

Productos diseñados a partir de research profundo (civica.digital + ATDT + dolor ciudadano). Aprovechan que **ningún civic-tech MX tiene browser automation gob.mx en producción** — diferenciador clave.

| MCP | Comprador objetivo | Vehículo | Tests |
|---|---|---|---|
| `mp_llave_mx_tracker` | ATDT (José Merino), IMCO, México Evalúa | Open source + servicios | ✅ 11 |
| `mp_retys_catalogo` | CONAMER + datos.gob.mx (Sistema Ajolote) | Donación cívica + mantenimiento | ✅ 11 |
| `mp_lnetb_auditor` | ATDT + IMCO + México Evalúa | Piloto think tank → escalar | ✅ 12 |
| `mp_portales_monitor` | Estados rezagados (Oax/Chis/Gro/Tab) | Licitación menor MIPYME via ComprasMX | ✅ 13 |
| `mp_imss_continuidad` | IMSS directo o integradora primaria | Subcontrato MIPYME (licitación mayo 2026) | ✅ 11 |

**Total Sprint G**: 5 MCPs · 58 tests · 1,634 totales · path real opt-in vía `MP_PLAYWRIGHT_PUBLIC=1`.

### Diferenciador frente a Cívica Digital y peers

- Cívica Digital usa Ruby/Elixir/Python pero **NO tiene browser automation gob.mx**
- Codeando México, SocialTIC, OPI Analytics: data/análisis, NO operación de portales
- Estos 5 MCPs son **infraestructura de operación** que complementa (no compite) civic-tech UI/SaaS

---

## Sprint H — Nivel 2: preparación documental + workflow RESICO HITL (2026-06-15)

Implementa el Nivel 2 del análisis "automatización de trámites MX" (legal + factible).

### MCPs nuevos

| MCP | Universo | Tests |
|---|---|---|
| `mp_form_filler_public` | 8 formularios públicos sin login (SAT, REPUVE, REPSE, REPEP, CURP, etc.) | ✅ 17 |
| `mp_citas_monitor` | Monitor **ético** cupos SAT/IMSS/SRE/INE con `consent_token` LFPDPPP | ✅ 16 |

### Workflow demo vendible

**`core-mexico/workflows/declaracion-resico-mensual.workflow.js`** — orquesta 6 MCPs:

1. `mp_sat_portal` → verifica régimen RESICO + omisiones SCJN 2026
2. `mp_resico_sat` → calcula ISR (Sprint E) + retenciones plataformas
3. `mp_sat_portal` → calendario fiscal (Sprint F) + pre-validar
4. `mp_clabe_validador_oficial` → verifica CLABE Banxico
5. HITL WhatsApp → autorización del titular (24h timeout)
6. Preparación paquete documental + reporte ejecutivo

**Métricas comerciales**:
- Universo: ~2.5M PF RESICO
- Tiempo: 4 min vs 2h manual
- Precio sugerido: $99-149 MXN B2C / $18k/mes B2B contadores
- Cobertura legal: CFF Art. 17-D + LFPDPPP Art. 13

### Diferenciador ético sobre mercado negro

`mp_citas_monitor` se distingue del mercado negro de citas SAT ($1k/cita) por:
- 1 alerta vinculada a 1 CURP (consent_token)
- Throttling mínimo 60s
- NO auto-reserva — solo alerta al titular
- Bitácora LFPDPPP-compliant
- Reportable a PFDC en caso de uso indebido

## Convención para agregar un MCP nuevo

1. **Discovery primero** con Playwright MCP en vivo — NO escribir parsers sin ver HTML real.
2. **Documentar hallazgos** en `docs/discoveries/discovery-portales-YYYY-MM-DD.md`.
3. **Asignar Tier** desde el primer commit: S, A, B o C.
4. **Tests mínimos**: catálogo + 1 parser + 1 routing live-flag = 3 tests.
5. **Mock-first obligatorio**: cliente corre sin credenciales con `simulated: true`.
6. **Bitácora con hash**: identificadores sensibles (RFC, CURP, placa) hasheados.
7. **Actualizar este CATALOGO.md** + `mcp-servers/README.md` + `website/mcp-manifest.json`.

## Comandos útiles

```bash
# Listar todos los MCPs
ls mcp-servers/ | grep '^mp_'

# Correr suite completa
PYTHONPATH=mcp-servers python3 -m pytest mcp-servers/ -q

# Validar un MCP específico
PYTHONPATH=mcp-servers python3 -m pytest mcp-servers/mp_predial_mx/tests/ -v
```
