# Utilidades de texto compartidas por varios módulos (productos, secciones)


def normalizar_nombre(nombre: str) -> str:
    """Clave de unicidad: sin espacios sobrantes y sin distinguir mayúsculas (sí tildes)."""
    return nombre.strip().casefold()
