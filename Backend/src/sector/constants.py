class ErrorCode:
    SECTOR_NO_ENCONTRADO = "Sector no encontrado"
    SECTOR_YA_INACTIVO = "El sector ya está dado de baja"
    SECTOR_NOMBRE_DUPLICADO = "Ya existe un sector con ese nombre"
    SECTOR_YA_ACTIVO = "El sector ya está activo"
    SECTOR_CON_ATENCIONES_ABIERTAS = "No se puede dar de baja el sector: tiene atenciones sin fecha_hasta"
    SECTOR_CON_MESAS_ACTIVAS = "No se puede dar de baja el sector: tiene mesas activas asociadas"
