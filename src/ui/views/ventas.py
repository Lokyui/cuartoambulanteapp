from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import src.ui.resources_rc  # noqa: F401
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QWidget

from src.modules.ventas_module import VentasModule
from src.ui.utils import fecha_legible, formatear_clp

UI_PATH = str(Path(__file__).parent / "ventas.ui")

COL_PRODUCTO, COL_PRECIO, COL_CANTIDAD, COL_SUBTOTAL = 0, 1, 2, 3


class VentasView(QWidget):
    def __init__(self, module: VentasModule) -> None:
        super().__init__()
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_widgets()
        self._poblar_pymes()
        self._conectar_signals()
        self._actualizar_resumen()

    def _configurar_widgets(self) -> None:
        self.lblFechaLegible.setText(fecha_legible(date.today()))

        self.tablaProductos.setRowCount(0)
        self.tablaProductos.setColumnCount(4)
        self.tablaProductos.setHorizontalHeaderLabels(
            ["Producto", "Precio", "Cantidad", "Subtotal"]
        )
        self.tablaProductos.setEditTriggers(self.tablaProductos.NoEditTriggers)

        self.rbEfectivo.setChecked(True)

        self.txtComentario.setPlaceholderText("Nota breve sobre la venta (máx. 200 caracteres)")

    def _conectar_signals(self) -> None:
        self.btnAgregarProducto.clicked.connect(self._agregar_producto)
        self.btnEliminarProducto.clicked.connect(self._eliminar_producto)
        self.btnGuardarVenta.clicked.connect(self._guardar_venta)
        self.btnCancelar.clicked.connect(self._reset_form)

        self.cmbPyme.currentIndexChanged.connect(self._actualizar_resumen)
        self.rbEfectivo.toggled.connect(self._actualizar_resumen)
        self.rbSumUp.toggled.connect(self._actualizar_resumen)
        self.dateEdit.dateChanged.connect(
            lambda qd: self.lblFechaLegible.setText(fecha_legible(qd.toPyDate()))
        )

    def _poblar_pymes(self) -> None:
        self.cmbPyme.clear()
        self.pymes = self.module.listar_pymes()
        for p in self.pymes:
            self.cmbPyme.addItem(p["nombre"], p["id"])

    def _agregar_producto(self) -> None:
        nombre = self.txtNombreProducto.text().strip()
        precio = int(self.Valor.value())
        cantidad = int(self.cantidad.value())

        if not nombre:
            QMessageBox.warning(self, "Falta el nombre", "Indica el nombre del producto.")
            return
        if precio <= 0:
            QMessageBox.warning(self, "Precio inválido", "El precio debe ser mayor a 0.")
            return

        subtotal = precio * cantidad
        fila = self.tablaProductos.rowCount()
        self.tablaProductos.insertRow(fila)

        item_prod = QTableWidgetItem(nombre)
        item_prec = QTableWidgetItem(formatear_clp(precio))
        item_prec.setData(Qt.UserRole, precio)
        item_cant = QTableWidgetItem(str(cantidad))
        item_cant.setData(Qt.UserRole, cantidad)
        item_sub = QTableWidgetItem(formatear_clp(subtotal))
        item_sub.setData(Qt.UserRole, subtotal)

        for col, it in enumerate((item_prod, item_prec, item_cant, item_sub)):
            self.tablaProductos.setItem(fila, col, it)

        self.txtNombreProducto.clear()
        self.cantidad.setValue(1)
        self.Valor.setValue(0)
        self.txtNombreProducto.setFocus()

        self._actualizar_resumen()

    def _eliminar_producto(self) -> None:
        fila = self.tablaProductos.currentRow()
        if fila < 0:
            QMessageBox.information(
                self,
                "Sin selección",
                "Selecciona un producto de la tabla antes de eliminar.",
            )
            return
        self.tablaProductos.removeRow(fila)
        self._actualizar_resumen()

    def _items_actuales(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for fila in range(self.tablaProductos.rowCount()):
            prod_item = self.tablaProductos.item(fila, COL_PRODUCTO)
            prec_item = self.tablaProductos.item(fila, COL_PRECIO)
            cant_item = self.tablaProductos.item(fila, COL_CANTIDAD)
            if not (prod_item and prec_item and cant_item):
                continue
            items.append({
                "producto": prod_item.text(),
                "precio": int(prec_item.data(Qt.UserRole)),
                "cantidad": int(cant_item.data(Qt.UserRole)),
            })
        return items

    def _metodo_actual(self) -> str:
        return "sumup" if self.rbSumUp.isChecked() else "efectivo"

    def _actualizar_resumen(self) -> None:
        items = self._items_actuales()
        pyme_nombre = self.cmbPyme.currentText() if self.cmbPyme.count() else "—"
        metodo = self._metodo_actual()
        metodo_label = "SumUp" if metodo == "sumup" else "Efectivo"

        if items:
            totales = self.module.calcular_totales(items, metodo)
            total = int(totales["total"])
            iva = int(totales["iva"])
            comision = totales["comision_sumup"]
        else:
            total = iva = 0
            comision = None

        cant_productos = sum(int(i["cantidad"]) for i in items)
        productos_txt = f"{cant_productos} producto{'s' if cant_productos != 1 else ''}"

        self._set_resumen_celda(0, 1, pyme_nombre)
        self._set_resumen_celda(1, 1, metodo_label)
        self._set_resumen_celda(2, 1, productos_txt)
        self._set_resumen_celda(3, 1, formatear_clp(total))
        self._set_resumen_celda(4, 1, formatear_clp(iva))
        self._set_resumen_celda(5, 1, formatear_clp(comision) if comision is not None else "$0")

        self._set_total_celda(formatear_clp(total))

    def _set_resumen_celda(self, fila: int, col: int, texto: str) -> None:
        item = self.tablaResumen.item(fila, col)
        if item is None:
            item = QTableWidgetItem()
            self.tablaResumen.setItem(fila, col, item)
        item.setText(texto)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def _set_total_celda(self, texto: str) -> None:
        item = self.tablaTotal.item(0, 1)
        if item is None:
            item = QTableWidgetItem()
            self.tablaTotal.setItem(0, 1, item)
        item.setText(texto)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def _guardar_venta(self) -> None:
        pyme_id = self.cmbPyme.currentData()
        if pyme_id is None:
            QMessageBox.warning(self, "Falta Pyme", "Selecciona una Pyme antes de guardar.")
            return

        items = self._items_actuales()
        if not items:
            QMessageBox.warning(
                self,
                "Sin productos",
                "Agrega al menos un producto antes de guardar la venta.",
            )
            return

        if not (self.rbEfectivo.isChecked() or self.rbSumUp.isChecked()):
            QMessageBox.warning(self, "Falta método", "Selecciona efectivo o SumUp.")
            return

        error = self._guardar_venta_validaciones()
        if error:
            QMessageBox.warning(self, "Comentario inválido", error)
            return

        comentario = self.txtComentario.toPlainText().strip()
        datos = {
            "pyme_id": pyme_id,
            "fecha": self.dateEdit.date().toPyDate(),
            "metodo": self._metodo_actual(),
            "items": items,
            "comentario": comentario or None,
        }

        try:
            self.module.procesar_nueva_venta(datos)
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar la venta:\n{e}")
            return

        QMessageBox.information(self, "Éxito", "Venta registrada correctamente.")
        self._reset_form()

    def _guardar_venta_validaciones(self) -> str | None:
        if len(self.txtComentario.toPlainText()) > 200:
            return "El comentario no puede superar 200 caracteres."
        return None

    def _reset_form(self) -> None:
        self.tablaProductos.setRowCount(0)
        self.txtNombreProducto.clear()
        self.txtComentario.clear()
        self.cantidad.setValue(1)
        self.Valor.setValue(0)
        self.dateEdit.setDate(date.today())
        self._actualizar_resumen()
