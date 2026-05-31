from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

from src.modules.catalogos_module import CatalogosModule

UI_PATH = str(Path(__file__).parent / "pyme_dialog.ui")


class PymeDialog(QDialog):
    def __init__(self, module: CatalogosModule, parent=None, pyme: dict[str, Any] | None = None):
        super().__init__(parent)
        self.module = module
        self.pyme = pyme
        uic.loadUi(UI_PATH, self)

        if pyme is not None:
            self.lblTitulo.setText("Editar pyme")
            self.lineNombre.setText(pyme["nombre"])
            self.chkActiva.setChecked(bool(pyme["activa"]))

        self.btnGuardar.clicked.connect(self._guardar)
        self.btnCancelar.clicked.connect(self.reject)

    def _guardar(self) -> None:
        nombre = self.lineNombre.text().strip()
        activa = self.chkActiva.isChecked()
        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        try:
            if self.pyme is None:
                self.module.crear_pyme(nombre, activa)
            else:
                self.module.actualizar_pyme(self.pyme["id"], nombre, activa)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la pyme:\n{e}")
