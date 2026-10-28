from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.secciones.constants import NOMBRE_MAX, SUBTITULO_MAX


class SeccionCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=NOMBRE_MAX)
    subtitulo: str | None = Field(default=None, max_length=SUBTITULO_MAX)

    # Se recorta antes de validar la longitud: vacío o solo espacios queda rechazado
    @field_validator("nombre", mode="before")
    @classmethod
    def recortar_nombre(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor

    # Recorta antes de validar el máximo; vacío o solo espacios se almacena como null
    @field_validator("subtitulo", mode="before")
    @classmethod
    def recortar_subtitulo(cls, valor):
        if isinstance(valor, str):
            return valor.strip() or None
        return valor


# El PUT es un reemplazo completo con las mismas reglas del alta
SeccionActualizar = SeccionCrear


class SeccionRespuesta(BaseModel):
    """Respuesta de una sección; se construye desde el modelo ORM."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    subtitulo: str | None
