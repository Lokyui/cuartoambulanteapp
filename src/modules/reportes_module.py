from src.db.dal import DAL
from typing import Any

class ReportesModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def obtener_resumen_pyme(self, pyme_id: int, inicio: str, fin: str) -> dict[str, Any]:
        """Calcula el neto liquidable restando IVA y comisiones."""
        data = self.dal.obtener_detalle_reporte_pyme(pyme_id, inicio, fin)
        
        # Podrías añadir lógica extra aquí, como calcular proyecciones 
        # o comparar contra el mes anterior.
        return data

    def generar_totales_mensuales(self, anio: int, mes: int):
        """Retorna el reporte consolidado para la tabla resumen[cite: 2, 21]."""
        return self.dal.reporte_mensual(anio, mes)