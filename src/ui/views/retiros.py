from __future__ import annotations

import src.ui.resources_rc 
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from db.dal import DAL

UI_PATH = "src/ui/views/retiros.ui"

class RetirosView(QWidget):
    def __init__(self, dal: DAL, parent=None) -> None:
        super().__init__(parent)
        self.dal = dal
        uic.loadUi(UI_PATH, self)
        
        # Aquí solo conectamos botones a funciones locales que
        # llamarán a la lógica de negocio en src/modules/retiros.py
        self._configurar_ui()

    def _configurar_ui(self):
        # Ejemplo: Conectar botón de marcar entregado
        # self.pushButton_17.clicked.connect(self._handle_entrega)
        pass

    def cargar_retiros_activos(self):
        # Esta función poblará el scrollArea con los datos del DAL
        pass