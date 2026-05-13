from typing import Any
from db.dal import DAL

class RetirosModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def registrar_ingreso(self, datos: dict[str, Any]) -> int:
        """Valida y registra un nuevo paquete en bodega."""
        # Regla de negocio: El estado inicial siempre es 'activo' 
        return self.dal.crear_paquete(
            fecha_llegada=datos["fecha_llegada"],
            pyme_remitente_id=datos["pyme_id"],
            nombre_destinatario=datos["destinatario"],
            ubicacion_bodega=datos["ubicacion"],
            estado_pago=datos["estado_pago"],
            recibido_por=datos["recibido_por"],
            descripcion=datos.get("descripcion"),
            estado="activo"
        )

    def listar_pendientes(self) -> list[dict[str, Any]]:
        """Obtiene solo los paquetes que no han sido entregados[cite: 18]."""
        return self.dal.listar_paquetes(estado="activo")