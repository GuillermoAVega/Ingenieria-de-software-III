from sqlalchemy.orm import Session

from src.auth import services
from src.auth.dependencies import obtener_usuario_actual
from src.auth.models import RolUsuario, Usuario
from src.auth.schemas import UsuarioCrear
from src.main import app


def _crear_usuario(motor, usuario="admin", clave="clave-segura", rol=RolUsuario.ADMINISTRADOR):
    with Session(motor) as db:
        return services.crear_usuario(
            db,
            UsuarioCrear(
                nombre="Usuario de prueba",
                nombre_usuario=usuario,
                clave=clave,
                rol=rol,
            ),
        )


def test_login_y_usuario_actual(cliente, motor):
    _crear_usuario(motor)
    app.dependency_overrides.pop(obtener_usuario_actual)

    respuesta = cliente.post(
        "/auth/login",
        json={"nombre_usuario": "ADMIN", "clave": "clave-segura"},
    )

    assert respuesta.status_code == 200
    token = respuesta.json()["token"]
    actual = cliente.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert actual.status_code == 200
    assert actual.json()["nombre_usuario"] == "admin"


def test_login_rechaza_clave_incorrecta(cliente, motor):
    _crear_usuario(motor)

    respuesta = cliente.post(
        "/auth/login", json={"nombre_usuario": "admin", "clave": "incorrecta"}
    )

    assert respuesta.status_code == 401


def test_endpoint_protegido_rechaza_sin_token(cliente):
    app.dependency_overrides.pop(obtener_usuario_actual)

    respuesta = cliente.get("/clientes")

    assert respuesta.status_code == 401


def test_operario_puede_leer_configuracion_pero_no_modificarla(cliente):
    app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
        id=2,
        nombre="Operario",
        nombre_usuario="operario",
        clave_hash="no-utilizada",
        rol=RolUsuario.OPERARIO,
        activo=True,
    )

    assert cliente.get("/sectores/").status_code == 200
    respuesta = cliente.post("/sectores/", json={"nombre": "Terraza"})
    assert respuesta.status_code == 403


def test_operario_no_puede_consultar_reportes(cliente):
    app.dependency_overrides[obtener_usuario_actual] = lambda: Usuario(
        id=2,
        nombre="Operario",
        nombre_usuario="operario",
        clave_hash="no-utilizada",
        rol=RolUsuario.OPERARIO,
        activo=True,
    )

    respuesta = cliente.get(
        "/reportes/medios-pago?desde=2026-01-01&hasta=2026-01-31"
    )

    assert respuesta.status_code == 403
