import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone

ITERACIONES = 310_000
DURACION_TOKEN_HORAS = 12


def crear_hash_clave(clave: str) -> str:
    sal = secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, ITERACIONES)
    return "pbkdf2_sha256${}${}${}".format(
        ITERACIONES,
        base64.urlsafe_b64encode(sal).decode(),
        base64.urlsafe_b64encode(derivada).decode(),
    )


def verificar_clave(clave: str, clave_hash: str) -> bool:
    try:
        algoritmo, iteraciones, sal_b64, derivada_b64 = clave_hash.split("$", 3)
        if algoritmo != "pbkdf2_sha256":
            return False
        sal = base64.urlsafe_b64decode(sal_b64.encode())
        esperada = base64.urlsafe_b64decode(derivada_b64.encode())
        obtenida = hashlib.pbkdf2_hmac(
            "sha256", clave.encode(), sal, int(iteraciones)
        )
        return hmac.compare_digest(obtenida, esperada)
    except (ValueError, TypeError):
        return False


def _codificar(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).decode().rstrip("=")


def _decodificar(valor: str) -> bytes:
    return base64.urlsafe_b64decode(valor + "=" * (-len(valor) % 4))


def _secreto() -> bytes:
    return os.getenv(
        "AUTH_SECRET_KEY", "gestion-restaurante-clave-solo-desarrollo"
    ).encode()


def crear_token(usuario_id: int) -> str:
    vencimiento = datetime.now(timezone.utc) + timedelta(hours=DURACION_TOKEN_HORAS)
    cuerpo = _codificar(
        json.dumps(
            {"sub": usuario_id, "exp": int(vencimiento.timestamp())},
            separators=(",", ":"),
        ).encode()
    )
    firma = _codificar(hmac.new(_secreto(), cuerpo.encode(), hashlib.sha256).digest())
    return f"{cuerpo}.{firma}"


def obtener_usuario_id(token: str) -> int | None:
    try:
        cuerpo, firma = token.split(".", 1)
        firma_esperada = _codificar(
            hmac.new(_secreto(), cuerpo.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(firma, firma_esperada):
            return None
        datos = json.loads(_decodificar(cuerpo))
        if int(datos["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            return None
        return int(datos["sub"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
