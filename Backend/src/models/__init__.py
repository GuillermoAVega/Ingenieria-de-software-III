from src.models.base import Base, ModeloBase, keyvalgen

# importar todos los modelos para que create_all los registre
from src.models.medio_pago import MedioPago
from src.models.comanda import Comanda
from src.models.detalle_comanda import DetalleComanda
from src.models.factura import Factura
from src.models.detalle_factura import DetalleFactura
from src.models.comprobante_pago import ComprobantePago
