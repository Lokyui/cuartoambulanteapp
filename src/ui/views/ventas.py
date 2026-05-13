from __future__ import annotations

import src.ui.resources_rc 
from datetime import date
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from db.dal import DAL
from src.modules.ventas_module import VentasModule

UI_PATH = "src/ui/views/ventas.ui"

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

class VentasView(QDialog):
    def __init__(self, module: VentasModule) -> None:
        super().__init__()
        self.module = module
        uic.loadUi(UI_PATH, self)

        hoy = date.today()
        self.dateEdit.setDate(hoy)

        #mostrar la fecha formateada
        dia_semana = DIAS_ES[hoy.weekday()]
        mes = MESES_ES[hoy.month]
        fecha_texto = f"{dia_semana} {hoy.day} de {mes}, {hoy.year}"
        
        if hasattr(self, 'label_2'): 
            self.label_2.setText(fecha_texto)

        self._poblar_pymes()
        self.pushButton_5.clicked.connect(self._guardar_venta)
        self.pushButton_6.clicked.connect(self.reject)

    def _poblar_pymes(self) -> None:
        self.comboBox.clear()
        self.pymes = self.module.dal.listar_pymes()
        for p in self.pymes:
            self.comboBox.addItem(p["nombre"], p["id"])

    def _guardar_venta(self) -> None:
        pyme_id = self.comboBox.currentData()
        valor = self.spinBox_precio.value()
        cantidad = self.spinBox_cantidad.value()
        fecha = self.dateEdit.date().toPyDate()
        metodo = "sumup" if self.radioButton_2.isChecked() else "efectivo"

        datos = {
            "pyme_id": pyme_id,
            "articulo": self.textEdit.toPlainText() if hasattr(self, 'textEdit') else "Venta general",
            "valor": valor,
            "cantidad": cantidad,
            "fecha": self.dateEdit.date().toPyDate(),
            "metodo": "sumup" if self.radioButton_2.isChecked() else "efectivo",
            "comentario": self.textEdit_3.toPlainText() if hasattr(self, 'textEdit_3') else ""
        }

        try:
            self.module.procesar_nueva_venta(datos)
            QMessageBox.information(self, "Éxito", "Venta registrada correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

        if not pyme_id:
            return QMessageBox.warning(self, "Error", "Debe seleccionar una Pyme.")
        