from __future__ import annotations

import src.ui.resources_rc 
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from db.dal import DAL

UI_PATH = "src/ui/views/resumen_caja.ui"

class ResumenCajaView(QWidget):
    def __init__(self, dal: DAL, parent=None) -> None:
        super().__init__(parent)
        self.dal = dal
        uic.loadUi(UI_PATH, self)
        
        self._inicializar_datos()

    def _inicializar_datos(self):
        # Cargar totales del día desde el DAL para mostrar en las etiquetas
        pass