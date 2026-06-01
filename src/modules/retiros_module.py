from datetime import date
from typing import Any

from src.db.dal import DAL


HISTORIAL_DIAS_DEFAULT = 30


class RetirosModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_todos(self) -> list[dict[str, Any]]:
        return self.dal.listar_paquetes()

    def listar_pendientes(self) -> list[dict[str, Any]]:
        return self.dal.listar_paquetes(estado="activo")

    def listar_por_cobrar(self) -> list[dict[str, Any]]:
        return self.dal.listar_paquetes(estado="activo", estado_pago="por_cobrar")

    def buscar_paquetes(
        self,
        texto: str,
        solo_activos: bool = False,
        solo_por_cobrar: bool = False,
    ) -> list[dict[str, Any]]:
        """Busca en destinatario, nombre de pyme y ubicación. Combinable con filtros."""
        return self.dal.listar_paquetes(
            estado="activo" if solo_activos or solo_por_cobrar else None,
            estado_pago="por_cobrar" if solo_por_cobrar else None,
            busqueda=texto or None,
        )

    def listar_historial(
        self,
        fecha_desde: str | date | None = None,
        fecha_hasta: str | date | None = None,
        pyme_id: int | None = None,
        busqueda: str | None = None,
    ) -> list[dict[str, Any]]:
        """Devuelve paquetes entregados con filtros por rango de fecha de entrega,
        pyme remitente y búsqueda parcial sobre destinatario/pyme/ubicación."""
        return self.dal.listar_paquetes(
            estado="entregado",
            pyme_remitente_id=pyme_id,
            busqueda=busqueda or None,
            fecha_entrega_desde=fecha_desde,
            fecha_entrega_hasta=fecha_hasta,
        )

    def listar_pymes(self, solo_activas: bool = True) -> list[dict[str, Any]]:
        return self.dal.listar_pymes(solo_activas=solo_activas)

    def listar_personal(self) -> list[dict[str, Any]]:
        return self.dal.listar_personal(solo_activos=True)

    def obtener_paquete(self, paquete_id: int) -> dict[str, Any] | None:
        return self.dal.obtener_paquete(paquete_id)

    def registrar_ingreso(self, datos: dict[str, Any]) -> int:
        self._verificar_ubicacion_libre(datos["ubicacion"])
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

    def actualizar_paquete(self, paquete_id: int, datos: dict[str, Any]) -> bool:
        nueva_ubicacion = datos.get("ubicacion")
        if nueva_ubicacion is not None:
            self._verificar_ubicacion_libre(nueva_ubicacion, excluir_id=paquete_id)
        cambios = {
            "fecha_llegada": datos.get("fecha_llegada"),
            "pyme_remitente_id": datos.get("pyme_id"),
            "nombre_destinatario": datos.get("destinatario"),
            "ubicacion_bodega": nueva_ubicacion,
            "estado_pago": datos.get("estado_pago"),
            "recibido_por": datos.get("recibido_por"),
            "descripcion": datos.get("descripcion"),
        }
        cambios = {k: v for k, v in cambios.items() if v is not None}
        return self.dal.actualizar_paquete(paquete_id, cambios)

    def _verificar_ubicacion_libre(self, ubicacion: str, excluir_id: int | None = None) -> None:
        ocupados = self.dal.listar_paquetes(estado="activo")
        for p in ocupados:
            if p["ubicacion_bodega"] == ubicacion and p["id"] != excluir_id:
                raise ValueError(
                    f"La ubicación {ubicacion} ya está ocupada por el paquete de "
                    f"{p['nombre_destinatario']}. Elige otra o entrega el actual primero."
                )

    def marcar_entregado(self, paquete_id: int, fecha_entrega: date | None = None) -> bool:
        return self.dal.actualizar_paquete(
            paquete_id,
            {
                "estado": "entregado",
                "fecha_entrega": fecha_entrega or date.today(),
            },
        )
