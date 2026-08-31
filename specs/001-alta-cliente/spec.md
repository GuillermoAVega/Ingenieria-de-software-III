# Spec 001 — Alta de Cliente

## Contexto y objetivo
El sistema necesita permitir que un Administrador registre nuevos clientes para
que puedan operar en la plataforma de venta de productos comerciales. Sin un
alta confiable y validada, no existe una base de clientes consistente sobre la
cual construir el resto de las funcionalidades (ventas, pedidos, atención).
El objetivo de esta feature es que el Administrador pueda dar de alta un
cliente con sus datos de contacto básicos, garantizando que la información
quede correctamente formada y que no se dupliquen clientes por DNI.

## Usuarios
- **Administrador**: único rol que ejecuta el alta de clientes en esta feature.

## Historias de usuario

### HU-CLI-01: Alta de Cliente
Como Administrador
Quiero registrar un nuevo cliente
Para darlo de alta en la base de datos y permitirle operar en el sistema.

**Datos del cliente**: DNI, Nombre, Apellido, Email, Teléfono (ingresados por
el Administrador) y Estado (asignado automáticamente por el sistema; ver
RF-9, no es un dato que el Administrador complete).

## Requisitos funcionales

### RF-1: Registro de cliente con datos válidos
El sistema deberá permitir al Administrador registrar un nuevo cliente
ingresando DNI, nombre, apellido, email y teléfono.

- CUANDO el Administrador envía el formulario de alta con todos los campos
  completos y válidos, y el DNI no está registrado previamente, ENTONCES el
  sistema deberá crear el cliente, mostrar al Administrador el mensaje
  "Cliente registrado exitosamente" y limpiar el formulario para permitir un
  nuevo alta.

### RF-2: Validación de nombre y apellido
El sistema deberá aceptar en los campos nombre y apellido únicamente letras
del alfabeto español (a-z, A-Z, tildes y ñ) y espacios, incluidos espacios
internos múltiples y consecutivos, sin normalizarlos. No se permiten
apóstrofes ni letras de otros alfabetos. No se define una longitud máxima
para estos campos.

- CUANDO el campo nombre o apellido contiene números o caracteres especiales
  no permitidos, ENTONCES el sistema deberá advertir que el campo solo debe
  contener letras y no deberá crear el registro.

### RF-3: Validación de formato de email
El sistema deberá validar que el email tenga la estructura estándar
`usuario@dominio.tld`, es decir, que incluya un punto en la parte del
dominio (ej. `usuario@dominio.com` es válido; `usuario@dominio`, sin punto,
es inválido).

- CUANDO el email ingresado no cumple con la estructura `usuario@dominio.tld`
  (sin `@`, o sin un punto en la parte del dominio), ENTONCES el sistema
  deberá advertir que el email es inválido y no deberá crear el registro.

### RF-4: Validación de formato de teléfono
El sistema deberá aceptar en el campo teléfono únicamente números y guiones,
sin exigir longitud mínima ni máxima, código de área ni estructura de
bloques específica.

- CUANDO el teléfono contiene letras o caracteres distintos de números y
  guiones, ENTONCES el sistema deberá advertir que el formato es incorrecto y
  no deberá crear el registro.

### RF-5: Validación de formato de DNI
El sistema deberá validar que el DNI sea numérico y tenga entre 7 y 8 dígitos.

- CUANDO el DNI ingresado contiene caracteres no numéricos o no tiene entre 7
  y 8 dígitos, ENTONCES el sistema deberá advertir que el formato del DNI es
  inválido y no deberá crear el registro.

### RF-6: Detección de DNI duplicado
El sistema deberá impedir el registro de un cliente cuyo DNI, comparado por su
valor numérico (sin considerar ceros a la izquierda), ya exista en la base de
datos, sin importar el estado (Activo o Inactivo) del cliente existente.

- CUANDO se intenta registrar un cliente con un DNI cuyo valor numérico ya
  existe en el sistema, ENTONCES el sistema deberá advertir que el cliente ya
  se encuentra registrado y no deberá crear el registro, independientemente
  del estado del cliente existente.

### RF-7: Campos obligatorios
El sistema deberá exigir que DNI, nombre, apellido, email y teléfono estén
completos para registrar un cliente.

- CUANDO se envía el formulario con alguno de los campos obligatorios vacío,
  ENTONCES el sistema deberá advertir que el campo es obligatorio y no deberá
  crear el registro.

### RF-8: Reporte completo de errores por intento
El sistema deberá validar todos los campos en cada intento de envío, sin
detenerse en el primer error encontrado.

- CUANDO el formulario se envía con más de un campo inválido y/o vacío a la
  vez, ENTONCES el sistema deberá mostrar todas las advertencias
  correspondientes a los campos afectados en el mismo intento.
- CUANDO el sistema muestra advertencias tras un intento de alta fallido,
  ENTONCES deberá conservar los valores ya ingresados por el Administrador en
  todos los campos, para que no deba reescribir el formulario completo.

### RF-9: Asignación automática del estado inicial
El sistema deberá asignar automáticamente el estado "Activo" a todo cliente
registrado exitosamente. El Administrador no ingresa ni elige el estado
durante el alta.

- CUANDO un cliente se registra exitosamente, ENTONCES el sistema deberá
  persistirlo con estado "Activo".

### RF-10: Normalización de espacios en campos de texto
El sistema deberá recortar (trim) el carácter espacio simple al inicio y al
final de cada campo de texto antes de validarlo y de guardarlo. No se
recortan otros caracteres de espacio en blanco (tabulaciones, saltos de
línea).

- CUANDO un campo de texto contiene el carácter espacio simple al inicio o al
  final, ENTONCES el sistema deberá quitarlo antes de aplicar las
  validaciones correspondientes y antes de persistir el dato.

### RF-11: Advertencia inmediata de errores de Frontend
El sistema deberá advertir de inmediato, sin esperar la respuesta del
servidor, los errores de campos obligatorios (RF-7) y de formato (RF-2 a
RF-5) detectables únicamente con los datos ya ingresados en el formulario.
La detección de DNI duplicado (RF-6) sigue requiriendo la respuesta del
servidor, ya que depende de los datos ya registrados en el sistema.

- CUANDO el Administrador intenta enviar el formulario y algún campo está
  vacío o no cumple su formato, ENTONCES el sistema deberá advertirlo de
  inmediato en el campo correspondiente, sin enviar la solicitud al
  servidor.
- CUANDO todos los campos cumplen su formato y están completos, ENTONCES el
  sistema deberá enviar la solicitud al servidor para completar las
  validaciones restantes (RF-6) y registrar el cliente.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al Administrador
  deben estar en español y deben identificar claramente el campo afectado.
- Los datos del cliente deben persistirse únicamente en la base de datos
  oficial del proyecto; no se admite almacenamiento local ad-hoc.
- El formulario de alta debe ser utilizable en plataformas móviles.

## Casos límite
- DNI con puntos, espacios o guiones (ej. `30.111.222`): debe tratarse como
  formato inválido según RF-5.
- Nombre o apellido compuesto únicamente por espacios en blanco: debe
  tratarse como campo vacío según RF-7, no como valor válido.
- Nombre o apellido de una sola letra: válido según RF-2 (no hay longitud
  mínima definida más allá de "no vacío").
- DNI con ceros a la izquierda (ej. `0123456`): válido si cumple la cantidad
  de dígitos exigida en RF-5; para la detección de duplicados (RF-6) se
  compara por su valor numérico, por lo que `0123456` y `123456` se
  consideran el mismo DNI.
- Alta con un DNI que ya existe pero pertenece a un cliente en estado
  Inactivo: se bloquea igual que si el cliente existente estuviera Activo
  (RF-6 no distingue por estado).
- Reintento de alta luego de que el sistema advierte errores: el
  Administrador corrige los campos señalados y vuelve a enviar; no se crea
  ningún registro parcial mientras existan advertencias pendientes.
- Email sin punto en el dominio (ej. `usuario@dominio`): inválido según
  RF-3, aunque cumpla la estructura `usuario@algo`.
- Todos los campos completos y con formato válido, pero con un DNI ya
  registrado: el Frontend no detecta ningún error (RF-11), por lo que la
  solicitud se envía igual al servidor, que es quien advierte el duplicado
  (RF-6).

## Fuera de alcance
- Edición o baja de clientes ya registrados.
- Listado, búsqueda o filtrado de clientes.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Envío de notificaciones (ej. email de bienvenida) al cliente registrado.
- Importación masiva de clientes.
- Historial de auditoría de altas y modificaciones.
- Cambios de estado posteriores al alta (ej. pasar a Inactivo).

## Criterios de finalización
- Un Administrador puede registrar un cliente con DNI, nombre, apellido,
  email y teléfono válidos, y el cliente queda persistido con estado Activo.
- Las validaciones de RF-2 a RF-7 están implementadas y producen la
  advertencia correspondiente sin crear el registro.
- Un intento de alta con múltiples errores muestra todas las advertencias
  aplicables en un mismo intento y conserva los valores ya ingresados (RF-8).
- Un DNI ya registrado no puede volver a registrarse (RF-6).
- Los campos de texto se recortan (trim) antes de validarse y guardarse
  (RF-10).
- Los errores de campos obligatorios y de formato se advierten de inmediato
  en el Frontend, sin esperar la respuesta del servidor (RF-11).
- Todos los criterios de aceptación de HU-CLI-01 y los casos límite listados
  están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Todas las aclaraciones fueron resueltas y
volcadas a los requisitos correspondientes (RF-1, RF-4, RF-8, RF-10).
