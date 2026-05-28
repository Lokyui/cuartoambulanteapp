from datetime import date
from typing import Any

from src.db.dal import DAL

CAMPOS_REPORTE = ["efectivo", "sumup", "total_bruto", "iva", "comision_sumup", "neto", "n_ventas"]


class ReportesModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_pymes(self) -> list[dict[str, Any]]:
        return self.dal.listar_pymes(solo_activas=True)

    def detalle_pyme(self, pyme_id: int, desde: str, hasta: str) -> dict[str, Any]:
        return self.dal.obtener_detalle_reporte_pyme(pyme_id, desde, hasta)

    def reporte_mensual(self, anio: int, mes: int) -> dict[str, Any]:
        filas = self.dal.reporte_mensual(anio, mes)
        totales = {c: sum(f[c] for f in filas) for c in CAMPOS_REPORTE}
        return {"filas": filas, "totales": totales}

    def detalle_dia(self, fecha: date, pyme_id: int | None = None) -> list[dict[str, Any]]:
        """Lista de ventas del día con el nombre de la tienda resuelto."""
        ventas = self.dal.listar_ventas(fecha=fecha, pyme_id=pyme_id)
        pymes = {p["id"]: p["nombre"] for p in self.dal.listar_pymes(solo_activas=False)}
        for v in ventas:
            v["pyme_nombre"] = pymes.get(v["pyme_id"], "—")
        return ventas
