from __future__ import annotations

from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from src.modules.retiros_module import RetirosModule

UI_PATH = str(Path(__file__).parent / "registro_retiro.ui")

UBICACIONES_BODEGA = [f"{letra}{num}" for letra in "ABCD" for num in range(1, 5)] + ["ESCALERA", "OTRO"]


class RegistroRetiroDialog(QDialog):
    def __init__(self, module: RetirosModule, parent=None):
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._cargar_datos_iniciales()

        self.pushButton_5.clicked.connect(self.guardar_paquete)
        self.pushButton_6.clicked.connect(self.reject)

    def _cargar_datos_iniciales(self):
        self.comboBox.clear()
        for p in self.module.listar_pymes():
            self.comboBox.addItem(p["nombre"], p["id"])

        self.comboBox_2.clear()
        self.comboBox_2.addItems(UBICACIONES_BODEGA)

        self.comboBox_3.clear()
        for pers in self.module.listar_personal():
            self.comboBox_3.addItem(pers["nombre_display"], pers["id"])

    def guardar_paquete(self):
        destinatario = self.lineEdit.text().strip()
        if not destinatario:
            QMessageBox.warning(self, "Validación", "El nombre del destinatario es obligatorio.")
            return

        datos = {
            "pyme_id": self.comboBox.currentData(),
            "fecha_llegada": self.dateEdit.date().toPyDate(),
            "destinatario": destinatario,
            "ubicacion": self.comboBox_2.currentText(),
            "estado_pago": "pagado" if self.radioButton.isChecked() else "por_cobrar",
            "recibido_por": self.comboBox_3.currentData(),
            "descripcion": self.textEdit_3.toPlainText().strip(),
        }

        try:
            self.module.registrar_ingreso(datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el paquete:\n{e}")
