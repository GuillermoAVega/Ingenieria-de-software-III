# Spec 005 — Alta de Producto

## Contexto y objetivo
El sistema hasta ahora solo gestiona clientes. Para operar la venta de
productos comerciales necesita un catálogo de productos con su stock
disponible. El objetivo de esta feature es que el Administrador pueda
registrar un nuevo producto con sus datos básicos e incorporarlo al
catálogo, garantizando que el código de producto (SKU) no se duplique y
que el precio y el stock inicial sean valores numéricos positivos válidos.

## Usuarios
- **Administrador**: único rol que ejecuta el alta de productos en esta
  feature.

## Historias de usuario

### HU-PROD-01: Alta de Producto
Como Administrador
Quiero registrar un nuevo producto
Para incorporarlo al catálogo e inventario disponible.

**Datos del producto**: Código/SKU, Nombre, Marca, Descripción (opcional),
Precio unitario y Stock inicial (ingresados por el Administrador).

## Requisitos funcionales

### RF-1: Registro de producto con datos válidos
El sistema deberá permitir al Administrador registrar un nuevo producto
ingresando Código/SKU, Nombre, Marca, Precio unitario, Stock inicial y,
opcionalmente, Descripción.

- CUANDO el Administrador envía el formulario de alta con todos los campos
  obligatorios completos y válidos, y el SKU no está registrado
  previamente, ENTONCES el sistema deberá crear el producto, mostrar el
  mensaje "Producto registrado exitosamente" y limpiar el formulario para
  permitir un nuevo alta.

### RF-2: Campos obligatorios
El sistema deberá exigir que Código/SKU, Nombre, Marca, Precio unitario y
Stock inicial estén completos para registrar un producto. La Descripción
es el único campo opcional.

- CUANDO se envía el formulario con alguno de los campos obligatorios
  vacío, ENTONCES EL SISTEMA deberá advertir que el campo es obligatorio y
  no deberá crear el registro.

### RF-3: Validación de precio unitario positivo
- SI el precio unitario ingresado no es un número válido, o es menor o
  igual a cero, ENTONCES EL SISTEMA deberá advertir que el valor debe ser
  un número positivo y no deberá crear el registro.

### RF-4: Validación de stock inicial entero y positivo
- SI el stock inicial ingresado no es un número entero válido (incluye
  valores con decimales), o es menor o igual a cero, ENTONCES EL SISTEMA
  deberá advertir que el valor debe ser un número positivo y no deberá
  crear el registro.

### RF-5: Detección de SKU duplicado
- SI el código/SKU ingresado, comparado sin distinguir mayúsculas de
  minúsculas, ya existe entre los productos registrados, ENTONCES EL
  SISTEMA deberá advertir que el código de producto está duplicado y no
  deberá crear el registro.

### RF-6: Reporte completo de errores por intento
El sistema deberá validar todos los campos en cada intento de envío, sin
detenerse en el primer error encontrado.

- CUANDO el formulario se envía con más de un campo inválido y/o vacío a
  la vez, ENTONCES EL SISTEMA deberá mostrar todas las advertencias
  correspondientes a los campos afectados en el mismo intento.
- CUANDO el sistema muestra advertencias tras un intento de alta fallido,
  ENTONCES deberá conservar los valores ya ingresados por el Administrador
  en todos los campos, para que no deba reescribir el formulario completo.

### RF-7: Normalización de espacios en campos de texto
El sistema deberá recortar (trim) el espacio simple al inicio y al final
de los campos de texto (Código/SKU, Nombre, Marca, Descripción) antes de
validarlos y de guardarlos.

- CUANDO un campo de texto contiene el carácter espacio simple al inicio o
  al final, ENTONCES EL SISTEMA deberá quitarlo antes de aplicar las
  validaciones correspondientes y antes de persistir el dato.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español y deben identificar claramente el
  campo afectado.
- Los datos del producto deben persistirse únicamente en la base de datos
  oficial del proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- Precio unitario igual a cero: inválido, mismo tratamiento que un valor
  negativo (RF-3).
- Stock inicial igual a cero: inválido, mismo tratamiento que un valor
  negativo (RF-4).
- Stock inicial con decimales (ej. `5.5`): inválido, mismo mensaje que un
  valor no positivo (RF-4).
- Precio unitario con decimales (ej. `19.99`): válido, sin restricción de
  cantidad de decimales.
- SKU con distinta capitalización de uno ya existente (ej. `ABC123` frente
  a `abc123`): se considera el mismo código y se bloquea como duplicado
  (RF-5).
- SKU con espacios al inicio o al final: se recorta antes de comparar y de
  guardar (RF-7), por lo que `" ABC123"` y `"ABC123"` se consideran el
  mismo código a efectos de RF-5.
- Descripción vacía: válida, no dispara advertencia de campo obligatorio
  (RF-2, es el único campo opcional).
- Intento con múltiples errores a la vez (ej. precio negativo y SKU
  duplicado): se muestran todas las advertencias correspondientes en el
  mismo intento, sin crear el producto (RF-6).

## Fuera de alcance
- Edición, baja o listado de productos (posibles features futuras,
  análogas a las ya construidas para clientes).
- Categorías o clasificación de productos.
- Gestión de proveedores.
- Movimientos de stock posteriores al alta (entradas o salidas de
  inventario).
- Imágenes o archivos adjuntos del producto.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Importación masiva de productos.
- Historial de auditoría de altas y modificaciones.

## Criterios de finalización
- Un Administrador puede registrar un producto con SKU, nombre, marca,
  precio y stock válidos (con o sin descripción), y el producto queda
  persistido.
- Las validaciones de RF-2 a RF-5 producen la advertencia correspondiente
  sin crear el producto.
- Un intento con múltiples errores muestra todas las advertencias
  aplicables en un mismo intento y conserva los valores ya ingresados
  (RF-6).
- Un SKU ya registrado (sin importar mayúsculas) no puede volver a
  registrarse (RF-5).
- Los campos de texto se recortan (trim) antes de validarse y guardarse
  (RF-7).
- Todos los criterios de aceptación de HU-PROD-01 y los casos límite
  listados están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Todas las aclaraciones fueron resueltas y
volcadas a los requisitos correspondientes (RF-2 a RF-5).
