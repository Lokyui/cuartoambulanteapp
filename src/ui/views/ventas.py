from __future__ import annotations

import src.ui.resources_rc 
from datetime import date
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from db.dal import DAL

UI_PATH = "src/ui/views/ventas.ui"

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

class VentasView(QDialog):
    def __init__(self, dal: DAL, parent=None) -> None:
        super().__init__(parent)
        self.dal = dal
        uic.loadUi(UI_PATH, self)

        hoy = date.today()
        self.dateEdit.setDate(hoy)

        #mostrar la fecha formateada
        dia_semana = DIAS_ES[hoy.weekday()]
        mes = MESES_ES[hoy.month]
        fecha_texto = f"{dia_semana} {hoy.day} de {mes}, {hoy.year}"
        
        if hasattr(self, 'label_fecha'): 
            self.label_fecha.setText(fecha_texto)

        self._poblar_pymes()
        self.pushButton_5.clicked.connect(self._guardar_venta)
        self.pushButton_6.clicked.connect(self.reject)

    def _poblar_pymes(self) -> None:
        self.comboBox.clear()
        self.pymes = self.dal.listar_pymes()
        for p in self.pymes:
            self.comboBox.addItem(p["nombre"], p["id"])

    def _guardar_venta(self) -> None:
        pyme_id = self.comboBox.currentData()
        valor = self.spinBox_precio.value()
        cantidad = self.spinBox_cantidad.value()
        fecha = self.dateEdit.date().toPyDate()
        metodo = "sumup" if self.radioButton_2.isChecked() else "efectivo"

        if not pyme_id:
            return QMessageBox.warning(self, "Error", "Debe seleccionar una Pyme.")
        
        #crearfunción en el módulo de ventas
        # calculos = procesar_datos_venta(valor, cantidad, metodo)
        
"""         try:
            self.dal.crear_venta(
                fecha=fecha,
                pyme_id=pyme_id,
                articulo="Venta general",
                valor=valor,
                cantidad=1,
                metodo=metodo,
                iva=iva,
                total=monto_total,
                comentario=self.textEdit_3.toPlainText()
            )
            QMessageBox.information(self, "Éxito", "Venta registrada correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}") """
