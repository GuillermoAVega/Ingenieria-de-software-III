from datetime import date

from sqlalchemy.orm import Session

from src.carta.schemas import CartaRespuesta
from src.productos import services as productos_services
from src.productos.bebidas import services as bebidas_services
from src.productos.combos import services as combos_services
from src.productos.menus_del_dia import services as menus_del_dia_services
from src.productos.platos import services as platos_services
from src.productos.postres import services as postres_services
from src.productos.registro import MenuEjecutivo
from src.productos_menu import services as productos_menu_services
from src.promociones import services as promociones_services
from src.secciones import services as secciones_services


def obtener_carta(sesion: Session, hoy: date) -> CartaRespuesta:
    """Reúne en una transacción los datos necesarios para mostrar la carta."""
    return CartaRespuesta(
        menus_diarios=productos_menu_services.listar_productos_menu(sesion),
        menus_del_dia=menus_del_dia_services.listar_menus_del_dia_con_proxima_fecha(
            sesion, hoy
        ),
        menus_ejecutivos=productos_services.listar(sesion, MenuEjecutivo),
        combos=combos_services.listar_combos(sesion),
        platos=platos_services.listar_platos(sesion),
        postres=postres_services.listar_postres(sesion),
        bebidas=bebidas_services.listar_bebidas(sesion),
        secciones=secciones_services.listar_secciones(sesion),
        promociones=promociones_services.listar_promociones(sesion, hoy),
    )
