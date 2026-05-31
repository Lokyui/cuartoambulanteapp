from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from src.modules.catalogos_module import CatalogosModule

UI_PATH = str(Path(__file__).parent / "personal_dialog.ui")


class PersonalDialog(QDialog):
    def __init__(self, module: CatalogosModule, parent=None, personal: dict[str, Any] | None = None):
        super().__init__(parent)
        self.module = module
        self.personal = personal
        uic.loadUi(UI_PATH, self)

        if personal is not None:
            self.lblTitulo.setText("Editar personal")
            self.lineNombre.setText(personal["nombre_display"])
            idx = self.cmbRol.findText(personal["rol"])
            if idx >= 0:
                self.cmbRol.setCurrentIndex(idx)
            self.chkActivo.setChecked(bool(personal["activo"]))

        self.btnGuardar.clicked.connect(self._guardar)
        self.btnCancelar.clicked.connect(self.reject)

    def _guardar(self) -> None:
        nombre = self.lineNombre.text().strip()
        rol = self.cmbRol.currentText()
        activo = self.chkActivo.isChecked()
        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        try:
            if self.personal is None:
                self.module.crear_personal(nombre, rol, activo)
            else:
                self.module.actualizar_personal(self.personal["id"], nombre, rol, activo)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el personal:\n{e}")
