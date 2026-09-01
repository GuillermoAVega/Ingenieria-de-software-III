# Spec 002 — Baja de Cliente

## Contexto y objetivo
El sistema ya permite dar de alta clientes ([[001-alta-cliente]]), pero no
existe forma de retirar de la operatoria a un cliente que deja de comprar o
que debe dejar de operar, sin perder su historial. El objetivo de esta
feature es que el Administrador pueda dar de baja (inactivar) a un cliente
existente localizándolo por su DNI, sin eliminar sus registros, para mantener
actualizada la nómina de clientes activos.

## Usuarios
- **Administrador**: único rol que ejecuta la baja de clientes en esta
  feature.

## Historias de usuario

### HU-CLI-02: Baja de Cliente
Como Administrador
Quiero dar de baja un cliente
Para inactivarlo y mantener actualizada la nómina de clientes.

## Requisitos funcionales

### RF-1: Búsqueda de cliente por DNI
El sistema deberá permitir al Administrador buscar un cliente ingresando su
DNI, como paso previo a la baja.

- CUANDO el Administrador ingresa un DNI y solicita la búsqueda, EL SISTEMA
  deberá localizar un cliente registrado cuyo DNI, comparado por su valor
  numérico (sin considerar ceros a la izquierda), coincida con el ingresado.

### RF-2: Cliente no encontrado
El sistema deberá advertir cuando la búsqueda no encuentre ningún cliente
registrado con el DNI ingresado, sin validar previamente el formato de ese
DNI.

- SI no existe ningún cliente registrado cuyo DNI coincida con el valor
  buscado, ENTONCES EL SISTEMA deberá advertir que el cliente no fue
  encontrado y no deberá habilitar ninguna acción de baja.

### RF-3: Confirmación previa a la baja
El sistema deberá exigir una confirmación explícita del Administrador antes
de modificar el estado del cliente encontrado.

- CUANDO la búsqueda localiza un cliente en estado Activo, EL SISTEMA deberá
  solicitar al Administrador que confirme la baja antes de modificar su
  estado.

### RF-4: Ejecución de la baja
El sistema deberá inactivar al cliente únicamente tras la confirmación del
Administrador.

- CUANDO el Administrador confirma la baja de un cliente en estado Activo,
  EL SISTEMA deberá cambiar su estado a Inactivo, mostrar el mensaje
  "Cliente dado de baja exitosamente" y conservar el resto de sus datos sin
  eliminarlos.

### RF-5: Cancelación de la confirmación
- CUANDO el Administrador cancela la confirmación de baja, EL SISTEMA no
  deberá modificar el estado del cliente ni ningún otro dato del registro.

### RF-6: Baja de cliente ya inactivo
El sistema deberá impedir volver a procesar la baja de un cliente que ya se
encuentra inactivo.

- SI el cliente localizado ya se encuentra en estado Inactivo, ENTONCES EL
  SISTEMA deberá advertir que el cliente ya se encuentra dado de baja, y no
  deberá solicitar confirmación ni modificar su estado.

### RF-7: Persistencia sin eliminación
- EL SISTEMA nunca eliminará el registro de un cliente como parte del
  proceso de baja; el proceso de baja únicamente podrá modificar el campo de
  estado del cliente.

### RF-8: Ausencia de re-verificación de estado al confirmar
El sistema no deberá volver a comprobar el estado del cliente en el momento
de confirmar la baja; deberá aplicar el cambio de estado directamente sobre
el estado obtenido durante la búsqueda (RF-1), asumiendo un único
Administrador operando sobre el sistema.

- CUANDO el Administrador confirma la baja de un cliente que fue localizado
  como Activo en la búsqueda, EL SISTEMA deberá cambiar su estado a Inactivo
  sin volver a consultar su estado actual antes de aplicar el cambio.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- El cambio de estado debe persistirse únicamente en la base de datos
  oficial del proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- DNI con ceros a la izquierda (ej. `0123456`) ingresado en la búsqueda: debe
  localizar al mismo cliente que `123456`, igual que la comparación de
  duplicados del alta (RF-6 de [[001-alta-cliente]]).
- DNI ingresado con formato inválido (letras, puntos, guiones, longitud
  incorrecta): no se valida su formato; si no hay ningún cliente con ese
  valor, se trata como "no encontrado" (RF-2).
- Intento de dar de baja a un cliente ya Inactivo: bloqueado por RF-6, sin
  llegar a pedir confirmación.
- El Administrador cancela la confirmación de baja: el cliente permanece sin
  cambios (RF-5).
- Cliente encontrado y confirmado para baja, pero cuyo estado cambió a
  Inactivo por otra vía entre la búsqueda y la confirmación (condición de
  carrera): el sistema no re-verifica el estado al confirmar; aplica la baja
  directamente sobre el estado obtenido en la búsqueda (RF-8).

## Fuera de alcance
- Reactivación de un cliente Inactivo (volver a estado Activo).
- Edición de los datos del cliente (nombre, email, teléfono, etc.) durante o
  fuera del proceso de baja.
- Listado, búsqueda general o filtrado de clientes más allá de la búsqueda
  puntual por DNI necesaria para iniciar la baja.
- Eliminación física del registro del cliente.
- Registro de motivo o comentario asociado a la baja.
- Historial de auditoría de bajas (quién, cuándo, por qué).
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Notificaciones al cliente dado de baja.

## Criterios de finalización
- Un Administrador puede buscar un cliente Activo por DNI (incluyendo DNIs
  con ceros a la izquierda) y darlo de baja tras confirmar, quedando su
  estado en Inactivo sin perder el resto de sus datos.
- Buscar un DNI sin cliente asociado advierte "no encontrado" y no habilita
  ninguna acción de baja (RF-2).
- Intentar dar de baja a un cliente ya Inactivo advierte que ya se encuentra
  dado de baja, sin modificar su estado (RF-6).
- Cancelar la confirmación de baja no produce ningún cambio en el cliente
  (RF-5).
- Todos los criterios de aceptación de HU-CLI-02 y los casos límite listados
  están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. La condición de carrera entre búsqueda y
confirmación fue resuelta y volcada al requisito RF-8.
