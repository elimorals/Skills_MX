"""Loader de e.firma SAT (certificado .cer + llave privada .key + password).

La e.firma se compone de:
- `.cer`: certificado X.509 con la clave pública
- `.key`: clave privada en formato PKCS#8 cifrada
- password: contraseña que abre el .key

Este módulo:
1. Carga ambos archivos sin firmar nada (solo valida estructura)
2. Extrae metadatos: RFC, nombre, fecha de vencimiento, número de serie
3. Valida vigencia (devuelve días para vencer)
4. Detecta si .cer + .key están emparejados

NO firma datos por sí mismo. Esa lógica vive en el Playwright client cuando
sea necesario interactuar con el portal SAT.

⚠ La e.firma es CRÍTICA. NUNCA loguees el contenido del .key ni la password
en claro. Esta clase solo expone metadatos del .cer.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.errors import ConfigError, ValidationError


@dataclass(frozen=True)
class EfirmaMetadata:
    """Metadatos extraídos del certificado .cer (no expone llave privada)."""

    rfc: str
    nombre: str | None
    numero_serie: str
    not_before: datetime
    not_after: datetime
    issuer: str
    is_valid_now: bool
    days_until_expiry: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "rfc": self.rfc,
            "nombre": self.nombre,
            "numero_serie": self.numero_serie,
            "vigencia_desde": self.not_before.isoformat(),
            "vigencia_hasta": self.not_after.isoformat(),
            "issuer": self.issuer,
            "vigente": self.is_valid_now,
            "dias_para_vencer": self.days_until_expiry,
        }


class EfirmaLoader:
    """Carga y valida una e.firma SAT sin exponer secretos.

    Uso:
        loader = EfirmaLoader.from_env()  # lee SAT_EFIRMA_*
        meta = loader.metadata()          # solo del .cer (público)
        # loader.sign(data) → cuando exista path real
    """

    def __init__(
        self,
        *,
        cert_path: Path,
        key_path: Path,
        password: str,
    ) -> None:
        self.cert_path = cert_path
        self.key_path = key_path
        self._password = password  # no se expone via getter
        self._cached_metadata: EfirmaMetadata | None = None
        self._cached_key_valid: bool | None = None
        self._validate_paths()

    @classmethod
    def from_env(cls) -> "EfirmaLoader":
        """Construye loader desde SAT_EFIRMA_CERT / SAT_EFIRMA_KEY / SAT_EFIRMA_PASSWORD.

        Lanza ConfigError si faltan envs.
        """
        cert = os.environ.get("SAT_EFIRMA_CERT", "").strip()
        key = os.environ.get("SAT_EFIRMA_KEY", "").strip()
        password = os.environ.get("SAT_EFIRMA_PASSWORD", "")

        missing = []
        if not cert:
            missing.append("SAT_EFIRMA_CERT")
        if not key:
            missing.append("SAT_EFIRMA_KEY")
        if not password:
            missing.append("SAT_EFIRMA_PASSWORD")

        if missing:
            raise ConfigError(
                f"Faltan variables de entorno para cargar e.firma: {', '.join(missing)}",
                {"missing": missing},
            )

        return cls(
            cert_path=Path(cert).expanduser(),
            key_path=Path(key).expanduser(),
            password=password,
        )

    def _validate_paths(self) -> None:
        if not self.cert_path.exists():
            raise ConfigError(
                f"Certificado .cer no encontrado: {self.cert_path}",
                {"path": str(self.cert_path)},
            )
        if not self.key_path.exists():
            raise ConfigError(
                f"Llave .key no encontrada: {self.key_path}",
                {"path": str(self.key_path)},
            )

    def metadata(self) -> EfirmaMetadata:
        """Extrae metadatos del .cer. Cacheado tras primer call.

        Lanza ValidationError si .cer no parsea (corrupto / no es certificado X.509).
        Requiere `cryptography` package — error claro si no está instalado.
        """
        if self._cached_metadata is not None:
            return self._cached_metadata

        cert = _parse_cert(self.cert_path)

        # SAT incluye RFC y nombre en el subject del cert (campos específicos)
        rfc = _extract_rfc(cert)
        nombre = _extract_subject_attr(cert, "x500UniqueIdentifier") or _extract_subject_attr(
            cert, "commonName"
        )
        serial = format(cert.serial_number, "x").upper()
        not_before = cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before.replace(tzinfo=timezone.utc)
        not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days = (not_after - now).days

        meta = EfirmaMetadata(
            rfc=rfc,
            nombre=nombre,
            numero_serie=serial,
            not_before=not_before,
            not_after=not_after,
            issuer=cert.issuer.rfc4514_string(),
            is_valid_now=not_before <= now <= not_after,
            days_until_expiry=days,
        )
        self._cached_metadata = meta
        return meta

    def validate_key_pair(self) -> bool:
        """Verifica que .cer + .key están emparejados (misma keypair).

        Hace un sign+verify de un nonce con la llave privada y verifica con la
        pública del cert. Si pasa, los archivos están emparejados.

        Cacheado tras primer call.
        """
        if self._cached_key_valid is not None:
            return self._cached_key_valid

        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
        except ImportError:
            raise ConfigError(
                "Package `cryptography` no instalado. Ejecuta: pip install cryptography",
                {"hint": "instalar cryptography"},
            )

        cert = _parse_cert(self.cert_path)
        key_bytes = self.key_path.read_bytes()
        try:
            private_key = serialization.load_der_private_key(
                key_bytes, password=self._password.encode("utf-8")
            )
        except Exception:
            try:
                private_key = serialization.load_pem_private_key(
                    key_bytes, password=self._password.encode("utf-8")
                )
            except Exception as exc:
                raise ValidationError(
                    "No se pudo abrir la llave .key — password incorrecto o formato inesperado",
                    {"raw_error": type(exc).__name__},
                )

        nonce = b"plugins-mx-efirma-validation-nonce"
        sig = private_key.sign(
            nonce,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        try:
            cert.public_key().verify(
                sig,
                nonce,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            self._cached_key_valid = True
        except Exception:
            self._cached_key_valid = False

        return self._cached_key_valid


# ---------- helpers ----------

def _parse_cert(path: Path):
    """Lee un .cer y retorna objeto cert de cryptography. SAT entrega DER por default."""
    try:
        from cryptography import x509
    except ImportError:
        raise ConfigError(
            "Package `cryptography` no instalado. Ejecuta: pip install cryptography",
            {"hint": "instalar cryptography"},
        )

    raw = path.read_bytes()
    # Intenta DER primero (formato nativo SAT), luego PEM
    try:
        return x509.load_der_x509_certificate(raw)
    except Exception:
        try:
            return x509.load_pem_x509_certificate(raw)
        except Exception as exc:
            raise ValidationError(
                f"Certificado en {path.name} no parsea como DER ni PEM",
                {"raw_error": type(exc).__name__},
            )


def _extract_rfc(cert) -> str:
    """SAT codifica el RFC en uniqueIdentifier OID 2.5.4.45 del subject.

    Fallback: busca un campo que parezca RFC en el commonName.
    """
    try:
        from cryptography.x509.oid import NameOID

        for attr in cert.subject:
            # OID 2.5.4.45 = uniqueIdentifier (SAT lo usa para RFC)
            if attr.oid.dotted_string == "2.5.4.45":
                rfc_text = attr.value.strip()
                # SAT a veces concatena RFC + CURP. RFC son los primeros 12-13 chars.
                rfc = rfc_text.split(" ")[0].strip().upper()
                if 12 <= len(rfc) <= 13:
                    return rfc
                return rfc[:13]

        # Fallback: commonName puede contener "Juan Pérez ABCD010101000"
        for attr in cert.subject:
            if attr.oid == NameOID.COMMON_NAME:
                tokens = attr.value.strip().split()
                for token in tokens:
                    token = token.upper()
                    if 12 <= len(token) <= 13 and token[0].isalpha():
                        return token
    except Exception:
        pass
    return "UNKNOWN"


def _extract_subject_attr(cert, attr_name: str) -> str | None:
    try:
        from cryptography.x509.oid import NameOID

        oid_map = {
            "commonName": NameOID.COMMON_NAME,
            "x500UniqueIdentifier": None,  # no estándar
        }
        target_oid = oid_map.get(attr_name)
        for attr in cert.subject:
            if target_oid and attr.oid == target_oid:
                return attr.value
            if attr_name == "commonName" and attr.oid == NameOID.COMMON_NAME:
                return attr.value
    except Exception:
        pass
    return None
