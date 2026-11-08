# AGENTS.md — Backend

Guía para agentes que modifiquen `Backend/`.

- Stack: FastAPI + SQLAlchemy + Pydantic + SQLite.
- Código en `Backend/src/`; pruebas en `Backend/tests/`.
- Mensajes y textos de error visibles en español; el dominio del proyecto usa nombres en español (`crear_seccion`, `nombre_normalizado`, etc.). Mantener la convención existente del módulo que se modifique.

## Estructura de una feature

Cada módulo de dominio vive en `Backend/src/<feature>/` con esta separación:

- `constants.py`: constantes del módulo (por ejemplo, `PREFIJO` de rutas).
- `models.py`: modelos SQLAlchemy.
- `schemas.py` / `schema.py`: modelos Pydantic de entrada y salida.
- `services.py`: lógica de negocio y transacciones.
- `router.py` / `routers.py`: rutas HTTP y traducción de errores de dominio a HTTP.
- `exceptions.py`: excepciones del dominio.
- `__init__.py`: paquete.

Algunos submódulos de productos están anidados, por ejemplo `src/productos/platos/`, `src/productos/bebidas/`, `src/productos/combos/`, `src/productos/menus_ejecutivos/`.

## Capas y responsabilidades

- El `router` solo recibe la petición, delega en `services` y declara `response_model`/códigos HTTP. No contiene lógica de negocio.
- `services` no importa FastAPI. Recibe `Session` y los schemas/datos, y devuelve modelos o lanza excepciones de dominio.
- Los `models` no contienen reglas de negocio.
- Los `schemas` validan y serializan; no acceden a la base.

## Base de datos y transacciones

- La sesión llega por inyección de dependencias con `Depends(get_db)`.
- Toda operación que falle debe hacer `rollback` antes de lanzar la excepción, para no dejar la transacción abierta.
- Las escrituras hacen `commit` en `services`.
- Traducir `IntegrityError` a errores de dominio (conflictos de unicidad) en `services`; no exponer errores crudos de SQLAlchemy.
- Para claves de unicidad por nombre usar `src.texto.normalizar_nombre`.
- Si se agrega un modelo nuevo, importarlo antes del `create_all` (ver `src/main.py` y `src/productos/registro.py`).
- Las migraciones legacy se resuelven con las funciones `migrar_*` de `src/database.py`, invocadas desde el `lifespan`.

## Errores

- Las excepciones de dominio heredan de `src/exceptions.py` o del `exceptions.py` de la feature.
- Registrar los manejadores en `MANEJADORES_EXCEPCIONES` del router y sumarlos en `src/main.py` cuando corresponda.
- Mantener los códigos HTTP coherentes: 400 solicitud inválida, 404 no encontrado, 409 conflicto, 422 validación.

## Pruebas

Ejecutar desde `Backend/`:

```bash
pytest
```

- `pytest.ini` fija `pythonpath = .` y `testpaths = tests`.
- `tests/conftest.py` usa una base SQLite en memoria (`DB_URL=sqlite://`); las pruebas nunca deben tocar `Backend/app.db`.
- Usar los fixtures existentes (`cliente`, `sesion`, `motor`, `persistir`, `crear_*`) antes de crear infraestructura nueva.
- Cubrir el camino feliz y los errores de dominio relevantes (no encontrado, duplicados, validación).

## Configuración y archivos generados

- La configuración se toma de `Backend/.env` (`ENV`, `ROOT_PATH_DEV`, `DB_URL`). No commitear `.env`.
- No commitear `Backend/venv/`, `__pycache__`, `.pytest_cache` ni bases SQLite locales (`app.db`, `restaurante.db`).
