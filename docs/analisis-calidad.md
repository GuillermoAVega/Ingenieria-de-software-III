# Análisis de calidad de código (análisis estático)

## 1. Qué es el análisis estático

Es la revisión automática del código fuente **sin ejecutarlo**. Detecta errores probables, código sin uso, problemas de estilo y complejidad excesiva antes de que lleguen a producción. No modifica el código: solo reporta.

## 2. Herramientas investigadas

| Herramienta | Lenguaje | Qué detecta | Uso en este proyecto |
|---|---|---|---|
| **ESLint** (+ typescript-eslint, react-hooks) | TypeScript / React | Errores, variables sin uso, reglas de hooks, tipado | Frontend (ya configurado en `Frontend/eslint.config.js`) |
| **Flake8** (pycodestyle + pyflakes + mccabe) | Python | Estilo PEP 8, imports/variables sin uso, nombres indefinidos, complejidad ciclomática | Backend (nuevo, `Backend/.flake8`) |
| Ruff | Python | Lo mismo que Flake8, mucho más rápido | Alternativa considerada |
| SonarQube / SonarCloud | Multilenguaje | Deuda técnica, duplicación, cobertura, seguridad | Alternativa considerada; requiere servidor/cuenta |

Se eligieron **ESLint** (frontend) y **Flake8** (backend) porque son el estándar de cada ecosistema, no requieren infraestructura y se integran fácilmente al CI existente.

## 3. Configuración

- **ESLint**: `js.configs.recommended`, `typescript-eslint recommended`, `react-hooks recommended`, `react-refresh`. Comando: `npm run lint` (en `Frontend/`).
- **Flake8** (`Backend/.flake8`): `max-line-length = 100`, `max-complexity = 10`, excluye `venv`, `.pytest_cache`, `__pycache__`. Comando: `flake8 src tests` (en `Backend/`).

## 4. Resultados

### 4.1 Frontend — ESLint

- Archivos analizados: **186**
- Errores: **0** — Advertencias: **0**

El frontend ya cumple todas las reglas configuradas.

### 4.2 Backend — Flake8

Total: **167 hallazgos** en `src` y `tests`.

| Código | Cant. | Significado | Severidad |
|---|---:|---|---|
| E501 | 81 | Línea de más de 100 caracteres | Estilo |
| E402 | 20 | Import que no está al inicio del módulo | Estilo |
| F401 | 20 | Import sin usar | Código muerto |
| W292 | 14 | Falta salto de línea al final del archivo | Estilo |
| E302 | 8 | Faltan 2 líneas en blanco | Estilo |
| E741 | 8 | Variable de nombre ambiguo (`l`) | Legibilidad |
| E712 | 4 | Comparación `== True` | Estilo |
| E303 | 3 | Demasiadas líneas en blanco | Estilo |
| C901 | 2 | Función demasiado compleja | Mantenibilidad |
| F811 | 2 | Redefinición de import sin usar (`date`) | Posible error |
| W293 | 2 | Línea en blanco con espacios | Estilo |
| F821 | 1 | Nombre indefinido (`DetalleReserva`) | Posible error |
| F841 | 1 | Variable local sin usar | Código muerto |
| W391 | 1 | Línea en blanco al final | Estilo |

Archivos con más hallazgos: `tests/conftest.py` (20), `tests/test_flujo_facturacion.py` (12), `src/promociones/services.py` (12), `src/models/__init__.py` (9), `src/cliente/services.py` (9).

## 5. Análisis de los hallazgos

**Relevantes (revisar y corregir):**
- **C901**: `modificar_comanda` (`src/comanda/services.py:304`, complejidad 15) y un test (complejidad 25). La primera es candidata a refactor.
- **F401 / F841 / F811** en código real y tests (`datetime.date` sin usar, redefinido en `tests/test_comanda_reserva.py`, variable `b` sin usar).
- **E741**: variable `l` en `src/promociones/services.py`.
- **E501 / W292 / E302 / E303 / W293 / W391**: estilo, correcciones mecánicas.

**Probables falsos positivos (se justifican, no se "arreglan"):**
- **F401 en `src/models/__init__.py` y `src/main.py:27-29`**: son imports intencionales para registrar modelos/tablas (re-export y efectos secundarios). Se resuelven con `# noqa: F401` o `__all__`.
- **E402 en `tests/conftest.py`**: imports tras configurar el entorno de pruebas; es intencional.
- **E712 en `src/atencion/services.py`**: `== True` en consultas SQLAlchemy es necesario para generar el SQL; se cambia a `.is_(True)` o se usa `# noqa`.
- **F821 `DetalleReserva` en `src/reserva/models.py:39`**: referencia adelantada que SQLAlchemy resuelve por nombre; falso positivo salvo que falte el import bajo `TYPE_CHECKING`.

## 6. Plan de corrección propuesto (Fase 2)

1. Correcciones mecánicas de estilo (E3xx, W2xx, W391) — riesgo nulo.
2. Eliminar imports/variables sin uso reales (F401, F841, F811).
3. Renombrar `l` (E741) y partir líneas largas (E501).
4. Marcar con `# noqa` los falsos positivos justificados.
5. Refactorizar `modificar_comanda` para bajar su complejidad.
6. Agregar `flake8` a `requirements.txt` y como paso del job `backend` en `.github/workflows/ci.yml`.

Cada paso en commits chicos, verificando con `pytest` y `npm run build`.
