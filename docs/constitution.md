# Constitución del Proyecto

1. **Stack fijo**: backend en Python 3.12+ con FastAPI y Pydantic para
   validación; frontend en React + JavaScript (sin TypeScript), con tipos
   documentados vía JSDoc y verificados con `tsc --checkJs`. No se agregan
   frameworks adicionales sin justificación en el PR.
2. **Spec antes que código**: ninguna feature se implementa sin una spec en
   `specs/` que la preceda y describa su comportamiento esperado.
3. **Lógica separada de la interfaz**: la lógica de negocio no vive en
   componentes de UI; toda regla de negocio debe ser testeable sin renderizar UI.
4. **Tests obligatorios**: todo PR que agregue lógica de negocio incluye tests;
   sin tests en verde, no hay merge.
5. **Persistencia única**: todos los datos de productos/clientes se guardan
   solo en la base de datos oficial del proyecto, nunca en estado local
   ad-hoc ni archivos sueltos.
6. **Idioma consistente**: código, nombres e identificadores en inglés;
   mensajes de commit y comentarios en español; mensajes al usuario en la
   UI también en español.
