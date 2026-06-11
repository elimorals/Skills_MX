#!/usr/bin/env python3
"""
Mock PAC — simula timbrado de CFDI sin conectar a Facturama/SW Sapien.

Útil para:
- Iteración rápida sin credenciales
- Tests de regresión con fixtures
- Demos sin riesgo de timbrar real

Uso como CLI:
    python mock_pac.py --action timbrar --payload payload.json
    python mock_pac.py --action cancelar --uuid abc-... --motivo 01 --folio-sustituto def-...

Uso como módulo:
    from mock_pac import MockPAC
    pac = MockPAC()
    response = pac.timbrar(payload)
"""

import argparse
import hashlib
import json
import secrets
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


class MockPAC:
    """Simula un PAC con respuestas plausibles."""

    def __init__(self, bitacora_path: Path = Path(".cache/mock-pac/bitacora.jsonl")):
        self.bitacora_path = bitacora_path
        self.bitacora_path.parent.mkdir(parents=True, exist_ok=True)

    def _generar_uuid(self) -> str:
        """Genera UUID con formato 8-4-4-4-12 hex válido."""
        hex_chars = secrets.token_hex(16)
        return f"{hex_chars[0:8]}-{hex_chars[8:12]}-{hex_chars[12:16]}-{hex_chars[16:20]}-{hex_chars[20:32]}"

    def _generar_sello(self, payload: dict) -> str:
        """Genera sello simulado basado en hash del payload."""
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
        return hashlib.sha256(data).hexdigest()[:128]

    def _validar_payload(self, payload: dict) -> list:
        """Validaciones críticas del payload antes de "timbrar"."""
        errores = []

        # Emisor
        emisor = payload.get("emisor", {})
        if not emisor.get("rfc"):
            errores.append("Falta RFC del emisor")
        if not emisor.get("regimen_fiscal"):
            errores.append("Falta régimen fiscal del emisor")

        # Receptor
        receptor = payload.get("receptor", {})
        if not receptor.get("rfc"):
            errores.append("Falta RFC del receptor")
        if not receptor.get("cp_domicilio"):
            errores.append("Falta CP del domicilio del receptor (obligatorio en CFDI 4.0)")
        if not receptor.get("uso_cfdi"):
            errores.append("Falta UsoCFDI")

        # Comprobante
        comp = payload.get("comprobante", {})
        metodo = comp.get("metodo_pago", "")
        forma = comp.get("forma_pago", "")

        if metodo == "PUE" and forma == "99":
            errores.append(
                "Inconsistencia: MétodoPago = PUE requiere FormaPago específico (01-31), "
                "no 99. 99 'Por definir' es solo válido cuando MétodoPago = PPD."
            )
        if metodo == "PPD" and forma != "99":
            errores.append(
                "Inconsistencia: MétodoPago = PPD requiere FormaPago = 99 (Por definir). "
                f"Recibido: {forma}."
            )

        # Conceptos
        conceptos = payload.get("conceptos", [])
        if not conceptos:
            errores.append("Sin conceptos en el CFDI")

        # Exportación obligatoria en 4.0
        if not comp.get("exportacion"):
            errores.append("Falta campo Exportacion (obligatorio en CFDI 4.0)")

        return errores

    def timbrar(self, payload: dict) -> dict:
        """Simula timbrado del CFDI."""
        errores = self._validar_payload(payload)
        if errores:
            response = {
                "simulated": True,
                "exito": False,
                "errores": errores,
            }
            self._log("timbrar_fallido", payload, response)
            return response

        uuid = self._generar_uuid()
        sello = self._generar_sello(payload)
        ahora = datetime.now(timezone.utc).replace(microsecond=0)

        response = {
            "simulated": True,
            "exito": True,
            "uuid": uuid,
            "fecha_timbrado": ahora.isoformat(),
            "sello_sat": sello,
            "sello_emisor": sello[:128],  # En real serían distintos
            "cadena_original_complemento": (
                f"||1.1|{uuid}|{ahora.isoformat()}|"
                f"AAA010101AAA|{sello[:8]}|0001|"  # PAC RFC simulado
            ),
            "xml_timbrado": f"<cfdi:Comprobante UUID='{uuid}'>...</cfdi:Comprobante>",
            "advertencias": [
                "Este timbrado es SIMULADO. UUID no es válido ante SAT.",
                "Para producción, conectar PAC real (Facturama, SW Sapien, etc.).",
            ],
        }
        self._log("timbrar_exitoso", payload, response)
        return response

    def cancelar(self, uuid: str, motivo: str, folio_sustituto: str = None,
                dias_desde_emision: int = 0, monto: float = 0) -> dict:
        """Simula cancelación."""
        errores = []

        if motivo not in {"01", "02", "03", "04"}:
            errores.append(f"Motivo de cancelación inválido: {motivo}. Debe ser 01-04.")

        if motivo == "01" and not folio_sustituto:
            errores.append("Motivo 01 requiere folio_sustituto.")

        if errores:
            response = {"simulated": True, "exito": False, "errores": errores}
            self._log("cancelar_fallido", {"uuid": uuid, "motivo": motivo}, response)
            return response

        requiere_aceptacion = dias_desde_emision > 3 or monto > 1000

        response = {
            "simulated": True,
            "exito": True,
            "uuid": uuid,
            "motivo": motivo,
            "folio_sustituto": folio_sustituto,
            "requiere_aceptacion_receptor": requiere_aceptacion,
            "plazo_respuesta_receptor": "3 días hábiles" if requiere_aceptacion else None,
            "default_si_no_responde": "se considera aceptada",
            "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
            "advertencias": [
                "Cancelación SIMULADA. En producción, verificar estatus posterior.",
            ],
        }
        self._log("cancelar_solicitada", {"uuid": uuid, "motivo": motivo, "monto": monto}, response)
        return response

    def consultar_estatus(self, uuid: str) -> dict:
        """Simula consulta de estatus."""
        return {
            "simulated": True,
            "uuid": uuid,
            "estatus": "Vigente",
            "consultado_en": datetime.now(timezone.utc).isoformat(),
            "advertencias": [
                "Estatus simulado. En producción consultar contra SAT.",
            ],
        }

    def _log(self, accion: str, request: dict, response: dict) -> None:
        """Registra operación en bitácora."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accion": accion,
            "request_summary": {
                "emisor_rfc": request.get("emisor", {}).get("rfc"),
                "receptor_rfc": request.get("receptor", {}).get("rfc"),
                "monto": sum(c.get("importe", 0) for c in request.get("conceptos", [])),
            } if "emisor" in request else request,
            "response_summary": {
                "exito": response.get("exito"),
                "uuid": response.get("uuid"),
                "errores": response.get("errores", []),
            },
        }
        with self.bitacora_path.open("a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Mock PAC para CFDI 4.0")
    parser.add_argument("--action", required=True, choices=["timbrar", "cancelar", "estatus"])
    parser.add_argument("--payload", help="Path a JSON con payload del CFDI")
    parser.add_argument("--uuid", help="UUID del CFDI para cancelar/consultar")
    parser.add_argument("--motivo", help="Motivo de cancelación (01-04)")
    parser.add_argument("--folio-sustituto", help="UUID del CFDI sustituto si motivo=01")
    parser.add_argument("--dias-desde-emision", type=int, default=0)
    parser.add_argument("--monto", type=float, default=0)
    args = parser.parse_args()

    pac = MockPAC()

    if args.action == "timbrar":
        if not args.payload:
            print("--payload requerido para timbrar")
            sys.exit(1)
        payload = json.loads(Path(args.payload).read_text())
        response = pac.timbrar(payload)
    elif args.action == "cancelar":
        if not args.uuid or not args.motivo:
            print("--uuid y --motivo requeridos para cancelar")
            sys.exit(1)
        response = pac.cancelar(
            args.uuid, args.motivo, args.folio_sustituto,
            args.dias_desde_emision, args.monto,
        )
    elif args.action == "estatus":
        if not args.uuid:
            print("--uuid requerido para consultar estatus")
            sys.exit(1)
        response = pac.consultar_estatus(args.uuid)

    print(json.dumps(response, indent=2, ensure_ascii=False))

    sys.exit(0 if response.get("exito", True) else 1)


if __name__ == "__main__":
    main()
