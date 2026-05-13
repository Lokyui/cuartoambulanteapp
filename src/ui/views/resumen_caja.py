from __future__ import annotations

import src.ui.resources_rc 
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from db.dal import DAL
from src.modules.caja_module import CajaModule
from datetime import date

UI_PATH = "src/ui/views/resumen_caja.ui"

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

class ResumenCajaView(QWidget):
    def __init__(self, module: CajaModule, parent=None) -> None:
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)
        hoy = date.today()
        dia_semana = DIAS_ES[hoy.weekday()]
        mes = MESES_ES[hoy.month]
        fecha_texto = f"{dia_semana} {hoy.day} de {mes}, {hoy.year}"

        if hasattr(self, "label"):
            self.label.setText(fecha_texto)
        
        self._inicializar_datos()

    def _inicializar_datos(self):
        # Cargar totales del día desde el DAL para mostrar en las etiquetas
        pass