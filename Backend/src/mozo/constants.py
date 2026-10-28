class ErrorCode:
    MOZO_NO_ENCONTRADO = "Mozo no encontrado"
    MOZO_LEGAJO_DUPLICADO = "Ya existe un mozo con ese nro_legajo"
    MOZO_YA_INACTIVO = "El mozo ya está dado de baja"
    MOZO_YA_ACTIVO = "El mozo ya está activo"
    MOZO_CON_ATENCIONES_ABIERTAS = "No se puede dar de baja el mozo: tiene atenciones sin fecha_hasta"
