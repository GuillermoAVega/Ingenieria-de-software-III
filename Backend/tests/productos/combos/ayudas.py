def comp(*ids: int, cantidad: int = 1) -> list[dict]:
    """Lista de componentes `{id, cantidad}` para los cuerpos y datos de combos."""
    return [{"id": id_, "cantidad": cantidad} for id_ in ids]
