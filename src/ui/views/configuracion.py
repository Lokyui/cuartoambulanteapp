from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)

from src.modules.catalogos_module import CatalogosModule
from src.ui.utils import ToggleSwitch, pregunta_si_no
from src.ui.views.personal_dialog import PersonalDialog
from src.ui.views.pyme_dialog import PymeDialog

UI_PATH = str(Path(__file__).parent / "configuracion.ui")


class ConfiguracionView(QWidget):
    def __init__(self, module: CatalogosModule, parent=None) -> None:
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_tablas()
        self._conectar_signals()
        self.recargar()

    def _configurar_tablas(self) -> None:
        for tabla in (self.tablaPymes, self.tablaPersonal):
            tabla.setEditTriggers(tabla.NoEditTriggers)
            tabla.setSelectionBehavior(tabla.SelectRows)
            tabla.setSelectionMode(tabla.SingleSelection)
            tabla.horizontalHeader().setStretchLastSection(True)

        self.tablaPymes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tablaPymes.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.tablaPersonal.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tablaPersonal.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tablaPersonal.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def _conectar_signals(self) -> None:
        self.btnNuevaPyme.clicked.connect(self._nueva_pyme)
        self.btnEditarPyme.clicked.connect(self._editar_pyme)
        self.btnEliminarPyme.clicked.connect(self._eliminar_pyme)

        self.btnNuevoPersonal.clicked.connect(self._nuevo_personal)
        self.btnEditarPersonal.clicked.connect(self._editar_personal)
        self.btnEliminarPersonal.clicked.connect(self._eliminar_personal)

    def recargar(self) -> None:
        self._pintar_pymes()
        self._pintar_personal()

    def _pintar_pymes(self) -> None:
        self.tablaPymes.setRowCount(0)
        for p in self.module.listar_pymes():
            fila = self.tablaPymes.rowCount()
            self.tablaPymes.insertRow(fila)
            self.tablaPymes.setItem(fila, 0, self._item(str(p["id"]), data=p["id"], alinear="cen"))
            self.tablaPymes.setItem(fila, 1, self._item(p["nombre"], alinear="izq"))
            self.tablaPymes.setCellWidget(fila, 2, self._celda_toggle_pyme(p))

    def _celda_toggle_pyme(self, pyme: dict[str, Any]) -> QWidget:
        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        toggle = ToggleSwitch(checked=bool(pyme["activa"]))
        # `clicked` solo se dispara con interacción del usuario, no con setChecked → permite revertir sin loop.
        toggle.clicked.connect(
            lambda activa, pid=pyme["id"], nombre=pyme["nombre"], t=toggle:
                self._cambiar_estado_pyme(pid, nombre, activa, t)
        )
        layout.addWidget(toggle)
        return contenedor

    def _cambiar_estado_pyme(self, pyme_id: int, nombre: str, activa: bool, toggle: ToggleSwitch) -> None:
        try:
            self.module.actualizar_pyme(pyme_id, nombre, activa)
        except Exception as e:
            toggle.setChecked(not activa)
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la pyme:\n{e}")

    def _pintar_personal(self) -> None:
        self.tablaPersonal.setRowCount(0)
        for p in self.module.listar_personal():
            fila = self.tablaPersonal.rowCount()
            self.tablaPersonal.insertRow(fila)
            self.tablaPersonal.setItem(fila, 0, self._item(str(p["id"]), data=p["id"], alinear="cen"))
            self.tablaPersonal.setItem(fila, 1, self._item(p["nombre_display"], alinear="izq"))
            self.tablaPersonal.setItem(fila, 2, self._item(p["rol"].capitalize(), alinear="cen"))
            self.tablaPersonal.setItem(fila, 3, self._item("Activo" if p["activo"] else "Inactivo", alinear="cen"))

    def _id_seleccionado(self, tabla) -> int | None:
        fila = tabla.currentRow()
        if fila < 0:
            return None
        item = tabla.item(fila, 0)
        return int(item.data(Qt.UserRole)) if item else None

    def _buscar_pyme(self, pyme_id: int) -> dict[str, Any] | None:
        for p in self.module.listar_pymes():
            if p["id"] == pyme_id:
                return p
        return None

    def _buscar_personal(self, personal_id: int) -> dict[str, Any] | None:
        for p in self.module.listar_personal():
            if p["id"] == personal_id:
                return p
        return None

    def _nueva_pyme(self) -> None:
        if PymeDialog(self.module, self).exec_():
            self.recargar()

    def _editar_pyme(self) -> None:
        pyme_id = self._id_seleccionado(self.tablaPymes)
        if pyme_id is None:
            QMessageBox.information(self, "Sin selección", "Selecciona una pyme para editar.")
            return
        pyme = self._buscar_pyme(pyme_id)
        if not pyme:
            self.recargar()
            return
        if PymeDialog(self.module, self, pyme=pyme).exec_():
            self.recargar()

    def _eliminar_pyme(self) -> None:
        pyme_id = self._id_seleccionado(self.tablaPymes)
        if pyme_id is None:
            QMessageBox.information(self, "Sin selección", "Selecciona una pyme para eliminar.")
            return
        pyme = self._buscar_pyme(pyme_id)
        if not pyme:
            self.recargar()
            return
        if not pregunta_si_no(self, "Eliminar pyme", f"¿Eliminar la pyme \"{pyme['nombre']}\"?"):
            return
        try:
            self.module.eliminar_pyme(pyme_id)
        except Exception as e:
            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                f"La pyme tiene ventas o paquetes asociados. Edítala y desactívala en lugar de borrarla.\n\nDetalle: {e}",
            )
            return
        self.recargar()

    def _nuevo_personal(self) -> None:
        if PersonalDialog(self.module, self).exec_():
            self.recargar()

    def _editar_personal(self) -> None:
        pid = self._id_seleccionado(self.tablaPersonal)
        if pid is None:
            QMessageBox.information(self, "Sin selección", "Selecciona un registro para editar.")
            return
        personal = self._buscar_personal(pid)
        if not personal:
            self.recargar()
            return
        if PersonalDialog(self.module, self, personal=personal).exec_():
            self.recargar()

    def _eliminar_personal(self) -> None:
        pid = self._id_seleccionado(self.tablaPersonal)
        if pid is None:
            QMessageBox.information(self, "Sin selección", "Selecciona un registro para eliminar.")
            return
        personal = self._buscar_personal(pid)
        if not personal:
            self.recargar()
            return
        if not pregunta_si_no(self, "Eliminar personal", f"¿Eliminar a \"{personal['nombre_display']}\"?"):
            return
        try:
            self.module.eliminar_personal(pid)
        except Exception as e:
            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                f"El registro tiene paquetes asociados. Edítalo y desactívalo en lugar de borrarlo.\n\nDetalle: {e}",
            )
            return
        self.recargar()

    @staticmethod
    def _item(texto: str, data: Any = None, alinear: str = "der") -> QTableWidgetItem:
        item = QTableWidgetItem(texto)
        if data is not None:
            item.setData(Qt.UserRole, data)
        if alinear == "izq":
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        elif alinear == "cen":
            item.setTextAlignment(Qt.AlignCenter)
        else:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item
