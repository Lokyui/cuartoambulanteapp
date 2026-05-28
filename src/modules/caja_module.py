from datetime import date

from src.db.dal import DAL


class CajaModule:
    def __init__(self, dal: DAL):
        self.dal = dal

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

    def resumen_dia(self, fecha: date) -> dict:
        """Desglose del día separando ventas en efectivo y SumUp.

        Devuelve totales + listados detallados de cada método para mostrar en pestañas.
        """
        ventas = self.dal.listar_ventas(fecha=fecha)
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
            "caja_inicial": caja_diaria.get("caja_inicial", 0),
            "caja_final_esperada": caja_diaria.get("caja_inicial", 0) + total_efectivo,
        }
