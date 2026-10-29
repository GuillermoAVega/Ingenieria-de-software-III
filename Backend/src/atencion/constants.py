class ErrorCode:
    ATENCION_NO_ENCONTRADA = "Atención no encontrada"
    ATENCION_YA_INACTIVA = "La atención ya está dada de baja"
    ATENCION_FECHA_INVALIDA = (
        "Las fechas de atención no pueden ser futuras y fecha_hasta debe ser "
        "mayor o igual a fecha_desde"
    )
    ATENCION_SECTOR_YA_ASIGNADO = "El mozo ya tiene una atención activa en ese sector"
    MOZO_INACTIVO_O_INEXISTENTE = "El mozo indicado no existe o está inactivo"
    SECTOR_INACTIVO_O_INEXISTENTE = "El sector indicado no existe o está inactivo"
