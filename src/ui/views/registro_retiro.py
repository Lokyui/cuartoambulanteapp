from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt5 import uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QMessageBox

from src.modules.retiros_module import RetirosModule

UI_PATH = str(Path(__file__).parent / "registro_retiro.ui")

# Mismas ubicaciones que el CHECK del schema (3x3 grid).
UBICACIONES_BODEGA = [f"{letra}{num}" for letra in "ABC" for num in range(1, 4)]


class RegistroRetiroDialog(QDialog):
    def __init__(self, module: RetirosModule, parent=None, paquete: dict[str, Any] | None = None):
        super().__init__(parent)
        self.module = module
        self.paquete = paquete
        uic.loadUi(UI_PATH, self)

        self._cargar_datos_iniciales()

        if paquete is not None:
            self.label_10.setText("Editar paquete")
            self.pushButton_5.setText("Actualizar paquete")
            self._prefill(paquete)
        else:
            self.radioButton.setChecked(True)

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

    def _prefill(self, p: dict[str, Any]) -> None:
        idx_pyme = self.comboBox.findData(p["pyme_remitente_id"])
        if idx_pyme >= 0:
            self.comboBox.setCurrentIndex(idx_pyme)

        self.dateEdit.setDate(QDate.fromString(str(p["fecha_llegada"]), "yyyy-MM-dd"))
        self.lineEdit.setText(p["nombre_destinatario"])

        idx_ubic = self.comboBox_2.findText(p["ubicacion_bodega"])
        if idx_ubic >= 0:
            self.comboBox_2.setCurrentIndex(idx_ubic)

        idx_pers = self.comboBox_3.findData(p["recibido_por"])
        if idx_pers >= 0:
            self.comboBox_3.setCurrentIndex(idx_pers)

        if p["estado_pago"] == "pagado":
            self.radioButton.setChecked(True)
        else:
            self.radioButton_2.setChecked(True)

        if p.get("descripcion"):
            self.textEdit_3.setPlainText(p["descripcion"])

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
            if self.paquete is None:
                self.module.registrar_ingreso(datos)
            else:
                self.module.actualizar_paquete(self.paquete["id"], datos)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el paquete:\n{e}")
