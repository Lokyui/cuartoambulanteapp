from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from src.db.dal import DAL

CAMPOS_REPORTE = ["efectivo", "sumup", "total_bruto", "iva", "comision_sumup", "neto", "n_ventas"]


class ReportesModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_pymes(self, solo_activas: bool = True) -> list[dict[str, Any]]:
        return self.dal.listar_pymes(solo_activas=solo_activas)

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

    def exportar_reporte_mensual(self, anio: int, mes: int, destino: str | Path) -> Path:
        data = self.reporte_mensual(anio, mes)
        columnas = ["nombre", *CAMPOS_REPORTE]
        df = pd.DataFrame(data["filas"], columns=columnas)
        if not df.empty:
            fila_total = {"nombre": "TOTAL", **data["totales"]}
            df = pd.concat([df, pd.DataFrame([fila_total])], ignore_index=True)

        destino = Path(destino)
        df.to_excel(destino, index=False, sheet_name=f"{anio}-{mes:02d}")
        return destino

    def exportar_detalle_pyme(
        self,
        pyme_id: int,
        desde: str,
        hasta: str,
        destino: str | Path,
    ) -> Path:
        data = self.detalle_pyme(pyme_id, desde, hasta)
        df_detalle = pd.DataFrame(data["detalle"])
        df_resumen = pd.DataFrame([data["resumen"]])

        destino = Path(destino)
        with pd.ExcelWriter(destino, engine="openpyxl") as writer:
            df_detalle.to_excel(writer, index=False, sheet_name="Detalle")
            df_resumen.to_excel(writer, index=False, sheet_name="Resumen")
        return destino
