"""mp_sep_profesional — MCP standalone para validación de cédulas profesionales SEP.

Wrapper sobre shared.sep_cedula expuesto como tools MCP con auto-routing por
modo de consulta (cédula | datos | CURP).

Crítico para verticales que requieren validar cédula profesional por ley:
- telemedicina-mx (NOM-004: validar médico antes de consulta)
- consultorio-especialista-mx
- clinica-salud-mx
- psicoterapia-mx
- despacho-legal-mx (validar abogado)
- despacho-contable-mx (validar contador)
"""
