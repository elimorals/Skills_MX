# mp_ley_silla_nom037

Compliance Ley Silla (LFT Arts. 132 fr. V y 133 fr. XVII Bis) + NOM-035 + NOM-037 (teletrabajo y desconexión).

**Universo**: 4M empresas formales mexicanas con trabajadores.

## Tools

- `silla_verificar_compliance(rfc, num_empleados, giro, modalidad_remota?, faltas_marcadas?)` —
  checklist con base legal y fundamento de multa por obligación, score y rango de multa potencial.
- `silla_calcular_multa(fundamento, reincidente?)` — `lft_994_v` (250-5000 UMA), `lft_1002`
  (50-5000 UMA), `lft_994_vi` (250-5000 UMA), con UMA 2026.
- `silla_generar_politica(...)` — política Markdown orientativa (Silla + NOM-035 + teletrabajo).
- `silla_listar_obligaciones(marco)` — `ley_silla` / `nom035` / `nom037` / `desconexion_digital`.

## Estado real

Tipo: **cálculo normativo local**. Constantes verificadas el 2026-10-14 (código: `shared/ley_silla_nom_mx.py`):

| Constante | Valor | Fuente |
|---|---|---|
| Ley Silla | DOF **19-12-2024**; vigor 2025-06-17; normativa interna a más tardar 2025-12-14 | LFT vigente (diputados.gob.mx, últ. reforma DOF 14-05-2026), decreto y transitorios |
| Obligación | Art. 132 fr. V: sillas con respaldo suficientes (servicios, comercio y análogos; industria si lo permite) | LFT |
| Prohibición | Art. 133 fr. XVII Bis: no obligar a estar de pie toda la jornada | LFT |
| Desconexión | Solo teletrabajo: Art. 330-E fr. VI (DOF 11-01-2021); NOM-037 5.2 e) | LFT, NOM-037 |
| Multas | 994 fr. V 250-5000 UMA; 1002 50-5000 UMA; reincidencia ×2 (Art. 992) | LFT |
| UMA 2026 | $117.31 diaria, vigente desde 2026-02-01 | INEGI, DOF 09-01-2026 (nota 5778072) |
| NOM-035 por tamaño | ≤15: 5.1, 5.4, 5.5, 5.7; 16-50: + 5.2, 5.6, 5.8; >50: 5.3 en lugar de 5.2 | NOM-035-STPS-2018, numeral 2 (DOF 23-10-2018) |
| NOM-037 | 5.1 listado, 5.2 política, 5.4 lista de verificación, 5.7 silla/equipo, 5.9 capacitación anual, 5.10 reversibilidad, 5.13 violencia familiar | NOM-037-STPS-2023 (DOF 08-06-2023) |

Corregido respecto a la versión anterior: la Ley Silla no es del "DOF 17-jul-2025"; no existe una
"reforma LFT Art. 132 marzo 2026" de desconexión digital; la UMA 2026 no es $113.07; las multas no
van por "severidad" sino por artículo; "descansos cada 4 horas", "capacitación anual de silla" y
"Guía I solo para ≤15" no están en la norma. La "severidad" que queda es solo prioridad interna.
