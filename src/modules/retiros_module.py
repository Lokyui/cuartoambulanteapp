from datetime import date
from typing import Any

from src.db.dal import DAL


class RetirosModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_todos(self) -> list[dict[str, Any]]:
        return self.dal.listar_paquetes()

    def listar_pendientes(self) -> list[dict[str, Any]]:
        return self.dal.listar_paquetes(estado="activo")

    def listar_pymes(self) -> list[dict[str, Any]]:
        return self.dal.listar_pymes(solo_activas=True)

    def listar_personal(self) -> list[dict[str, Any]]:
        return self.dal.listar_personal(solo_activos=True)

    def registrar_ingreso(self, datos: dict[str, Any]) -> int:
        return self.dal.crear_paquete(
            fecha_llegada=datos["fecha_llegada"],
            pyme_remitente_id=datos["pyme_id"],
            nombre_destinatario=datos["destinatario"],
            ubicacion_bodega=datos["ubicacion"],
            estado_pago=datos["estado_pago"],
            recibido_por=datos["recibido_por"],
            descripcion=datos.get("descripcion"),
            estado="activo",
        )

    def marcar_entregado(self, paquete_id: int, fecha_entrega: date | None = None) -> bool:
        return self.dal.actualizar_paquete(
            paquete_id,
            {
                "estado": "entregado",
                "fecha_entrega": fecha_entrega or date.today(),
            },
        )
