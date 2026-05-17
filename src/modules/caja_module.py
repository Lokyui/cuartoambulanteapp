from datetime import date
from src.db.dal import DAL

class CajaModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def calcular_cierre_dia(self, fecha: date, efectivo_real: int):
        """Compara las ventas registradas contra el dinero físico."""
        ventas = self.dal.listar_ventas(fecha=fecha)
        total_efectivo = sum(v["total"] for v in ventas if v["metodo"] == "efectivo")
        
        # Lógica de negocio: Diferencia = Real - Esperado 
        caja_diaria = self.dal.obtener_caja_diaria(fecha)
        inicial = caja_diaria["caja_inicial"] if caja_diaria else 0
        esperado = inicial + total_efectivo
        
        diferencia = efectivo_real - esperado
        
        return {
            "esperado": esperado,
            "diferencia": diferencia,
            "total_efectivo": total_efectivo
        }