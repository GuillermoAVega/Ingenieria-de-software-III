# Spec 014 — Correcciones sobre Alta y Listado de Cliente

## Contexto y objetivo
Esta spec agrupa dos correcciones puntuales recibidas sobre features ya
implementadas de Cliente, en la misma línea que [[013-validacion-amigable-formularios]]
(feedback directo de uso, no una nueva historia de negocio):

1. **Alta de Cliente** ([[001-alta-cliente]]): hoy un DNI que ya existe en
   el sistema bloquea el alta sin importar el estado del cliente
   existente (RF-6 de 001). Se pide relajar esta regla: permitir el alta
   de un cliente con un DNI que ya pertenece a un cliente **Inactivo**,
   bloqueando únicamente si pertenece a uno **Activo**. Esto replica,
   del lado del alta, el mismo criterio que [[003-modificacion-cliente]]
   ya aplica del lado de la edición (RF-6/RF-7 de esa spec).
   - Una cuarta corrección relacionada, "reactivar automáticamente al
     cliente Inactivo con los datos nuevos", ya se evaluó y se descartó
     explícitamente en una conversación anterior. Esta spec **no**
     reactiva ni fusiona nada: el alta con un DNI de un Inactivo crea un
     registro de cliente nuevo e independiente, con estado Activo,
     dejando temporalmente el mismo valor de DNI en dos clientes (uno
     Activo, uno Inactivo) — igual que ya ocurre hoy con la edición
     desde [[003-modificacion-cliente]].
2. **Listar Clientes** ([[004-listar-clientes]]): el filtro ya busca por
   Nombre, Apellido y DNI (RF-2 de 004), pero la pantalla no se lo
   comunica al Administrador. Se pide agregar un texto de ayuda debajo
   de la barra de búsqueda indicándolo.

## Usuarios
- **Administrador**: único rol que da de alta y consulta el listado de
  clientes en esta feature.

## Requisitos funcionales

### RF-1: DNI duplicado contra otro cliente Activo (alta)
Se reemplaza el criterio de [[001-alta-cliente]] RF-6: la unicidad de
DNI al dar de alta se compara únicamente contra clientes **Activos**.

- SI el DNI ingresado, comparado por su valor numérico, ya pertenece a
  otro cliente en estado **Activo**, ENTONCES EL SISTEMA deberá
  advertir que el cliente ya se encuentra registrado y no deberá crear
  el registro.

### RF-2: DNI coincidente con un cliente Inactivo permitido (alta)
- EL SISTEMA permitirá registrar un nuevo cliente con un DNI que
  coincide con el de otro cliente en estado **Inactivo**, sin ninguna
  advertencia de duplicado. El cliente nuevo se crea como un registro
  independiente, con su propio estado "Activo" (RF-9 de
  [[001-alta-cliente]]); el cliente Inactivo existente no se modifica,
  no se reactiva ni se fusiona con el nuevo.

### RF-3: Texto de ayuda sobre los criterios de búsqueda (listado)
- EL SISTEMA deberá mostrar, debajo de la barra de búsqueda de la
  pantalla de listado de clientes, un texto indicando que la búsqueda
  puede hacerse por Nombre, Apellido o DNI.

## Requisitos no funcionales
- El mensaje de duplicado (RF-1) y el texto de ayuda (RF-3) deben estar
  en español, mismo criterio que el resto de la aplicación.

## Casos límite
- Alta con un DNI que pertenece a un cliente Activo: se sigue
  bloqueando exactamente igual que hoy (RF-1); no hay cambio de
  comportamiento en este caso.
- Alta con un DNI que pertenece a un cliente Inactivo: se permite
  (RF-2); tras el alta existen dos clientes con el mismo valor de DNI,
  uno Activo (el recién creado) y uno Inactivo (el preexistente).
- Alta con un DNI que pertenece a dos o más clientes Inactivos ya
  existentes (situación ya posible desde que existe RF-7 de
  [[003-modificacion-cliente]]): se permite igual, ya que RF-1 solo
  compara contra clientes Activos, sin importar cuántos Inactivos
  compartan ese DNI.
- El texto de ayuda de RF-3 es puramente informativo: no cambia ni
  restringe el comportamiento de filtrado ya implementado en
  [[004-listar-clientes]] RF-2 a RF-4.

## Fuera de alcance
- Reactivar, fusionar o actualizar los datos de un cliente Inactivo al
  registrar un alta con su mismo DNI: evaluado y descartado
  explícitamente; el alta con un DNI de un Inactivo crea un cliente
  nuevo e independiente (ver RF-2).
- Cualquier otro cambio a las validaciones de formato de
  [[001-alta-cliente]] (nombre, apellido, email, teléfono, campos
  obligatorios): sin cambios, ya cubiertos por
  [[013-validacion-amigable-formularios]].
- Cambios al mecanismo de filtrado de [[004-listar-clientes]] (RF-2 a
  RF-8): el filtro ya busca por Nombre, Apellido y DNI; esta spec solo
  agrega el texto que lo comunica.
- Extender el mismo texto de ayuda a los listados de Producto o Venta.

## Criterios de finalización
- Un alta con un DNI que pertenece a un cliente Activo se sigue
  bloqueando con el mensaje de duplicado (RF-1).
- Un alta con un DNI que pertenece únicamente a clientes Inactivos se
  registra con éxito, creando un cliente nuevo en estado Activo sin
  modificar el/los Inactivo(s) existente(s) (RF-2).
- La pantalla de Listar Clientes muestra, debajo de la barra de
  búsqueda, un texto indicando que se puede buscar por Nombre,
  Apellido o DNI (RF-3).
- Todos los criterios de aceptación listados están cubiertos por
  pruebas automatizadas en verde.

## Dudas abiertas
Sin dudas abiertas pendientes.
