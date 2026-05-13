from datetime import date
from typing import Any
from db.dal import DAL

class VentasModule:
    def __init__(self, dal: DAL):
        self.dal = dal
        self.IVA_FACTOR = 0.19
        self.COMISION_SUMUP_FACTOR = 0.029 # Ejemplo de comisión del 2.9% + IVA

    def procesar_nueva_venta(self, datos: dict[str, Any]) -> int:
        """Calcula impuestos/comisiones y registra la venta."""
        valor_total = int(datos["valor"]) * int(datos["cantidad"])
        iva = int(valor_total * self.IVA_FACTOR)
        
        comision = None
        if datos["metodo"].lower() == "sumup":
            # Lógica de negocio: SumUp siempre lleva comisión calculada [cite: 3]
            comision = int(valor_total * self.COMISION_SUMUP_FACTOR)

        return self.dal.crear_venta(
            fecha=datos.get("fecha", date.today()),
            pyme_id=datos["pyme_id"],
            articulo=datos["articulo"],
            valor=datos["valor"],
            cantidad=datos["cantidad"],
            metodo=datos["metodo"],
            iva=iva,
            comision_sumup=comision,
            total=valor_total,
            comentario=datos.get("comentario")
        )