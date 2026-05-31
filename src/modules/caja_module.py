from datetime import date
from pathlib import Path

import pandas as pd

from src.db.dal import DAL


class CajaModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_pymes(self) -> list[dict]:
        return self.dal.listar_pymes(solo_activas=True)

    def calcular_cierre_dia(self, fecha: date, efectivo_real: int) -> dict:
        ventas = self.dal.listar_ventas(fecha=fecha)
        total_efectivo = sum(v["total"] for v in ventas if v["metodo"] == "efectivo")

        caja_diaria = self.dal.obtener_caja_diaria(fecha)
        inicial = caja_diaria["caja_inicial"] if caja_diaria else 0
        esperado = inicial + total_efectivo

        return {
            "esperado": esperado,
            "diferencia": efectivo_real - esperado,
            "total_efectivo": total_efectivo,
        }

    def resumen_dia(self, fecha: date, pyme_id: int | None = None) -> dict:
        """Desglose del día separando ventas en efectivo y SumUp.

        Devuelve totales + listados detallados de cada método para mostrar en pestañas.
        Incluye el estado de cierre persistido (caja_inicial, real, diferencia, cerrada).
        `pyme_id` filtra solo el desglose visual; los datos de cierre persistido
        (caja_inicial, cerrada) siguen siendo del día completo.
        """
        ventas = self.dal.listar_ventas(fecha=fecha, pyme_id=pyme_id)
        pymes = {p["id"]: p["nombre"] for p in self.dal.listar_pymes(solo_activas=False)}

        for v in ventas:
            v["pyme_nombre"] = pymes.get(v["pyme_id"], "—")

        efectivo = [v for v in ventas if v["metodo"] == "efectivo"]
        sumup = [v for v in ventas if v["metodo"] == "sumup"]

        total_efectivo = sum(v["total"] for v in efectivo)
        total_sumup = sum(v["total"] for v in sumup)
        total_iva = sum(v["iva"] for v in ventas)
        total_comision = sum(v["comision_sumup"] or 0 for v in sumup)
        total_bruto = total_efectivo + total_sumup
        neto = total_bruto - total_iva - total_comision

        caja_diaria = self.dal.obtener_caja_diaria(fecha) or {}
        caja_inicial = caja_diaria.get("caja_inicial", 0)

        return {
            "fecha": fecha,
            "ventas_efectivo": efectivo,
            "ventas_sumup": sumup,
            "totales": {
                "efectivo": total_efectivo,
                "sumup": total_sumup,
                "bruto": total_bruto,
                "iva": total_iva,
                "comision_sumup": total_comision,
                "neto": neto,
                "n_ventas": len(ventas),
                "n_efectivo": len(efectivo),
                "n_sumup": len(sumup),
            },
            "caja_inicial": caja_inicial,
            "caja_final_esperada": caja_inicial + total_efectivo,
            "caja_final_real": caja_diaria.get("caja_final_real"),
            "diferencia": caja_diaria.get("diferencia", 0),
            "cerrada": bool(caja_diaria.get("cerrada", 0)),
            "comentario": caja_diaria.get("comentario") or "",
        }

    def set_caja_inicial(self, fecha: date, monto: int) -> None:
        if monto < 0:
            raise ValueError("La caja inicial no puede ser negativa.")
        caja = self.dal.obtener_caja_diaria(fecha)
        if caja is None:
            self.dal.crear_caja_diaria(fecha=fecha, caja_inicial=monto)
        else:
            self.dal.actualizar_caja_diaria(fecha, {"caja_inicial": monto})

    def cerrar_dia(
        self,
        fecha: date,
        efectivo_real: int,
        comentario: str | None = None,
    ) -> dict:
        """Calcula totales del día y persiste el cierre en caja_diaria.

        Crea la fila si no existe (con caja_inicial=0). Idempotente: vuelve a
        cerrar el mismo día sobreescribe los totales con la realidad actual.
        """
        if efectivo_real < 0:
            raise ValueError("El efectivo contado no puede ser negativo.")
        if comentario and len(comentario) > 200:
            raise ValueError("El comentario no puede superar 200 caracteres.")

        resumen = self.resumen_dia(fecha)
        tot = resumen["totales"]
        caja_inicial = resumen["caja_inicial"]
        esperado = caja_inicial + tot["efectivo"]
        diferencia = efectivo_real - esperado

        datos = {
            "caja_inicial": caja_inicial,
            "total_efectivo": tot["efectivo"],
            "total_sumup": tot["sumup"],
            "total_iva": tot["iva"],
            "comision_sumup_total": tot["comision_sumup"],
            "caja_final_esperada": esperado,
            "caja_final_real": efectivo_real,
            "diferencia": diferencia,
            "cerrada": 1,
            "comentario": comentario or None,
        }

        caja = self.dal.obtener_caja_diaria(fecha)
        if caja is None:
            self.dal.crear_caja_diaria(fecha=fecha, **datos)
        else:
            self.dal.actualizar_caja_diaria(fecha, datos)

        return {"esperado": esperado, "diferencia": diferencia}

    def reabrir_dia(self, fecha: date) -> bool:
        """Marca el día como abierto sin perder los totales registrados."""
        caja = self.dal.obtener_caja_diaria(fecha)
        if caja is None or not caja["cerrada"]:
            return False
        return self.dal.actualizar_caja_diaria(fecha, {"cerrada": 0})

    def exportar_cierre(self, fecha: date, destino: str | Path) -> Path:
        """Exporta el cierre del día a Excel con 3 hojas: Resumen, Efectivo y SumUp."""
        datos = self.resumen_dia(fecha)
        tot = datos["totales"]

        df_resumen = pd.DataFrame([
            ("Caja inicial", tot["efectivo"] and datos["caja_inicial"] or datos["caja_inicial"]),
            ("Ventas en efectivo", tot["efectivo"]),
            ("Ventas con SumUp", tot["sumup"]),
            ("Total bruto", tot["bruto"]),
            ("IVA acumulado", tot["iva"]),
            ("Comisión SumUp", tot["comision_sumup"]),
            ("Neto", tot["neto"]),
            ("Caja final esperada", datos["caja_final_esperada"]),
            ("Caja final real", datos["caja_final_real"] if datos["caja_final_real"] is not None else ""),
            ("Diferencia", datos["diferencia"]),
            ("Cerrada", "Sí" if datos["cerrada"] else "No"),
            ("Cantidad de ventas", tot["n_ventas"]),
        ], columns=["Concepto", "Valor"])

        columnas_venta = ["pyme_nombre", "articulo", "cantidad", "total", "iva", "comision_sumup", "comentario"]
        df_efectivo = pd.DataFrame(datos["ventas_efectivo"], columns=columnas_venta)
        df_sumup = pd.DataFrame(datos["ventas_sumup"], columns=columnas_venta)

        destino = Path(destino)
        with pd.ExcelWriter(destino, engine="openpyxl") as writer:
            df_resumen.to_excel(writer, index=False, sheet_name="Resumen")
            df_efectivo.to_excel(writer, index=False, sheet_name="Efectivo")
            df_sumup.to_excel(writer, index=False, sheet_name="SumUp")
        return destino
