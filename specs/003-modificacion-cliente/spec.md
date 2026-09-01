# Spec 003 — Modificación de Cliente

## Contexto y objetivo
El sistema ya permite dar de alta ([[001-alta-cliente]]) y dar de baja
([[002-baja-cliente]]) clientes, pero no hay forma de corregir sus datos de
contacto cuando cambian o fueron mal cargados. El objetivo de esta feature es
que el Administrador pueda editar los datos de un cliente existente
(localizándolo por su DNI), para mantenerlos actualizados sin necesidad de
volver a darlo de alta ni de perder su historial.

## Usuarios
- **Administrador**: único rol que ejecuta la modificación de clientes en
  esta feature.

## Historias de usuario

### HU-CLI-03: Modificación de Cliente
Como Administrador
Quiero editar la información de un cliente
Para mantener actualizados sus datos de contacto e identificación.

## Requisitos funcionales

### RF-1: Búsqueda de cliente por DNI para editar
El sistema deberá permitir al Administrador buscar un cliente ingresando su
DNI, como paso previo a la edición.

- CUANDO el Administrador ingresa un DNI y solicita la búsqueda, EL SISTEMA
  deberá localizar al cliente registrado cuyo DNI, comparado por su valor
  numérico (sin considerar ceros a la izquierda), coincida con el ingresado,
  sin importar si su estado es Activo o Inactivo.

### RF-2: Cliente no encontrado
- SI no existe ningún cliente registrado con el DNI buscado, ENTONCES EL
  SISTEMA deberá advertir que el cliente no fue encontrado y no deberá
  mostrar ningún formulario de edición.

### RF-3: Formulario de edición con los datos actuales
- CUANDO el sistema localiza un cliente, EL SISTEMA deberá mostrar un
  formulario con sus datos actuales (DNI, nombre, apellido, email, teléfono)
  para que el Administrador los modifique.

### RF-4: Validación de campos con las reglas del alta
El sistema deberá validar los campos editados con las mismas reglas de
formato, obligatoriedad y recorte de espacios que rigen el alta de cliente
(RF-2 a RF-5, RF-7 y RF-10 de [[001-alta-cliente]]).

- CUANDO el Administrador envía el formulario de edición con algún campo
  vacío o con formato inválido, ENTONCES EL SISTEMA deberá advertir el campo
  afectado y no deberá guardar ningún cambio del intento.

### RF-5: Reporte completo de errores por intento
- CUANDO el formulario de edición se envía con más de un campo inválido y/o
  vacío a la vez, ENTONCES EL SISTEMA deberá mostrar todas las advertencias
  correspondientes en el mismo intento, sin guardar ningún cambio.

### RF-6: DNI duplicado contra otro cliente Activo
- SI el DNI editado pertenece a otro cliente (distinto del que se está
  editando) que se encuentra en estado Activo, ENTONCES EL SISTEMA deberá
  advertir que el DNI ya está en uso y no deberá guardar ningún cambio del
  intento, aunque el resto de los campos sea válido.

### RF-7: DNI coincidente con un cliente Inactivo permitido
- EL SISTEMA permitirá que el DNI editado coincida con el de otro cliente
  cuyo estado es Inactivo, sin advertir ningún conflicto por ese motivo.

### RF-8: Confirmación previa a guardar
- CUANDO todos los campos editados son válidos y el DNI (si cambió) no
  pertenece a otro cliente Activo, EL SISTEMA deberá solicitar al
  Administrador que confirme el guardado antes de aplicar los cambios.

### RF-9: Guardado tras confirmación
- CUANDO el Administrador confirma el guardado, EL SISTEMA deberá persistir
  los cambios y mostrar el mensaje "Cliente modificado exitosamente".

### RF-10: Cancelación de la confirmación
- CUANDO el Administrador cancela la confirmación de guardado, EL SISTEMA no
  deberá modificar ningún dato del cliente.

### RF-11: La edición no altera el estado del cliente
- EL SISTEMA no modificará el estado (Activo/Inactivo) del cliente como
  parte de la edición de sus datos de contacto.

## Requisitos no funcionales
- Todos los mensajes de advertencia y confirmación dirigidos al
  Administrador deben estar en español.
- Los cambios deben persistirse únicamente en la base de datos oficial del
  proyecto; no se admite almacenamiento local ad-hoc.

## Casos límite
- El Administrador edita otros campos sin cambiar el DNI: no se dispara
  ninguna advertencia de duplicado, porque la comparación de RF-6 es contra
  "otro" cliente, nunca contra el propio registro que se está editando.
- El DNI editado, con ceros a la izquierda distintos, sigue siendo el mismo
  valor numérico que el DNI actual del propio cliente: no se considera un
  cambio de DNI ni dispara duplicado.
- El DNI editado coincide con el de otro cliente Activo, y el resto de los
  campos son válidos: se bloquea el intento completo (no se guarda nada),
  no solo el campo DNI (RF-6).
- El DNI editado coincide con el de otro cliente Inactivo: se permite y se
  guarda sin advertencia (RF-7). Esto puede dejar temporalmente el mismo
  valor de DNI en más de un cliente (uno Activo, uno o más Inactivos); el
  sistema no lo considera un conflicto mientras no haya más de un cliente
  Activo con ese DNI.
- Se edita un cliente Inactivo: sus datos de contacto cambian, pero
  permanece Inactivo (RF-11).
- El Administrador cancela la confirmación de guardado: ningún dato del
  cliente cambia (RF-10).
- El formulario se envía con varios campos inválidos y/o vacíos a la vez: se
  muestran todas las advertencias correspondientes en el mismo intento y no
  se guarda ningún cambio (RF-5).

## Fuera de alcance
- Cambiar el estado del cliente (dar de alta, de baja o reactivar) desde
  esta funcionalidad — eso corresponde a [[001-alta-cliente]] y
  [[002-baja-cliente]].
- Historial de auditoría de cambios (qué campo cambió, cuándo, quién lo
  modificó).
- Edición masiva o por lote de varios clientes a la vez.
- Deshacer una edición ya guardada.
- Autenticación y gestión de roles de usuario (se asume que el sistema ya
  identifica quién opera como Administrador).
- Listado, búsqueda general o filtrado de clientes más allá de la búsqueda
  puntual por DNI necesaria para iniciar la edición.
- Notificación al cliente sobre los cambios en sus datos.

## Criterios de finalización
- Un Administrador puede buscar un cliente (Activo o Inactivo) por DNI,
  editar sus datos con valores válidos, confirmar el guardado y ver los
  cambios persistidos junto con el mensaje "Cliente modificado
  exitosamente".
- Un intento de edición con campos inválidos y/o vacíos muestra todas las
  advertencias correspondientes en el mismo intento y no guarda ningún
  cambio (RF-4, RF-5).
- Un intento de editar el DNI a uno de otro cliente Activo advierte que el
  DNI ya está en uso y no guarda ningún cambio del intento (RF-6).
- Editar el DNI a uno de otro cliente Inactivo se guarda sin advertencia
  (RF-7).
- Cancelar la confirmación de guardado no modifica ningún dato del cliente
  (RF-10).
- El estado del cliente no cambia como resultado de la edición (RF-11).
- Todos los criterios de aceptación de HU-CLI-03 y los casos límite listados
  están cubiertos por pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes. Se identificó y resolvió durante la
entrevista una tensión entre RF-7 (permitir DNI coincidente con un cliente
Inactivo) y la unicidad de DNI construida en [[001-alta-cliente]]: se
decidió mantener la regla literal del criterio de aceptación (RF-7), lo que
implica que la unicidad de DNI ya no se exige entre todos los clientes por
igual, sino solo respecto de otros clientes Activos. Esta relajación deberá
tenerse en cuenta al planificar la persistencia en `plan.md`.
