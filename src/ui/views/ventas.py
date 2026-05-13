from __future__ import annotations

from datetime import date
from typing import Any

import src.ui.resources_rc  # noqa: F401 — registra recursos Qt
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QWidget

from src.modules.ventas_module import VentasModule

UI_PATH = "src/ui/views/ventas.ui"

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Columnas de la tabla de productos
COL_PRODUCTO, COL_PRECIO, COL_CANTIDAD, COL_SUBTOTAL = 0, 1, 2, 3


def _formatear_clp(monto: int) -> str:
    return "$" + f"{int(monto):,}".replace(",", ".")


def _fecha_legible(fecha: date) -> str:
    return f"{DIAS_ES[fecha.weekday()]} {fecha.day} de {MESES_ES[fecha.month]}, {fecha.year}"

class VentasView(QWidget):
    def __init__(self, module: VentasModule) -> None:
        super().__init__()
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_widgets()
        self._poblar_pymes()
        self._conectar_signals()
        self._actualizar_resumen()

    # ── setup ────────────────────────────────────────────────────────────────

    def _configurar_widgets(self) -> None:
        hoy = date.today()
        self.dateEdit.setDate(hoy)
        self.dateEdit.setCalendarPopup(True)
        self.label_2.setText(_fecha_legible(hoy))

        # Spinboxes del formulario "agregar producto"
        self.cantidad.setMinimum(1)
        self.cantidad.setMaximum(9999)
        self.cantidad.setValue(1)

        self.Valor.setMinimum(1)
        self.Valor.setMaximum(9_999_999)
        self.Valor.setValue(1)
        self.Valor.setPrefix("$ ")

        # Limpiar las filas dummy de Qt Designer
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Producto", "Precio", "Cantidad", "Subtotal"]
        )
        self.tableWidget.setEditTriggers(self.tableWidget.NoEditTriggers)

        self.radioButton.setChecked(True)  # efectivo por defecto

        self.textEdit_3.setPlaceholderText("Comentario opcional (máx. 200 caracteres)")

    def _conectar_signals(self) -> None:
        self.pushButton.clicked.connect(self._agregar_producto)        # "Agregar producto"
        self.btnEliminarProducto.clicked.connect(self._eliminar_producto)  # "Eliminar producto"
        self.pushButton_5.clicked.connect(self._guardar_venta)         # "Guardar venta"
        self.pushButton_6.clicked.connect(self._reset_form)            # "Cancelar"

        # Cualquier cambio que afecte el resumen
        self.comboBox.currentIndexChanged.connect(self._actualizar_resumen)
        self.radioButton.toggled.connect(self._actualizar_resumen)
        self.radioButton_2.toggled.connect(self._actualizar_resumen)
        self.dateEdit.dateChanged.connect(
            lambda qd: self.label_2.setText(_fecha_legible(qd.toPyDate()))
        )

    def _poblar_pymes(self) -> None:
        self.comboBox.clear()
        self.pymes = self.module.dal.listar_pymes()
        for p in self.pymes:
            self.comboBox.addItem(p["nombre"], p["id"])

    # ── acciones ─────────────────────────────────────────────────────────────

    def _agregar_producto(self) -> None:
        nombre = self.textEdit.toPlainText().strip()
        precio = int(self.Valor.value())
        cantidad = int(self.cantidad.value())

        if not nombre:
            QMessageBox.warning(self, "Falta el nombre", "Indicá el nombre del producto.")
            return
        if precio <= 0:
            QMessageBox.warning(self, "Precio inválido", "El precio debe ser mayor a 0.")
            return

        subtotal = precio * cantidad
        fila = self.tableWidget.rowCount()
        self.tableWidget.insertRow(fila)

        item_prod = QTableWidgetItem(nombre)
        item_prec = QTableWidgetItem(_formatear_clp(precio))
        item_prec.setData(Qt.UserRole, precio)
        item_cant = QTableWidgetItem(str(cantidad))
        item_cant.setData(Qt.UserRole, cantidad)
        item_sub = QTableWidgetItem(_formatear_clp(subtotal))
        item_sub.setData(Qt.UserRole, subtotal)

        for col, it in enumerate((item_prod, item_prec, item_cant, item_sub)):
            self.tableWidget.setItem(fila, col, it)

        # Reset del mini-form
        self.textEdit.clear()
        self.cantidad.setValue(1)
        self.Valor.setValue(1)
        self.textEdit.setFocus()

        self._actualizar_resumen()

    def _eliminar_producto(self) -> None:
        fila = self.tableWidget.currentRow()
        if fila < 0:
            QMessageBox.information(
                self,
                "Sin selección",
                "Seleccioná un producto de la tabla antes de eliminar.",
            )
            return
        self.tableWidget.removeRow(fila)
        self._actualizar_resumen()

    def _items_actuales(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for fila in range(self.tableWidget.rowCount()):
            prod_item = self.tableWidget.item(fila, COL_PRODUCTO)
            prec_item = self.tableWidget.item(fila, COL_PRECIO)
            cant_item = self.tableWidget.item(fila, COL_CANTIDAD)
            if not (prod_item and prec_item and cant_item):
                continue
            items.append({
                "producto": prod_item.text(),
                "precio": int(prec_item.data(Qt.UserRole)),
                "cantidad": int(cant_item.data(Qt.UserRole)),
            })
        return items

    def _metodo_actual(self) -> str:
        return "sumup" if self.radioButton_2.isChecked() else "efectivo"

    def _actualizar_resumen(self) -> None:
        items = self._items_actuales()
        pyme_nombre = self.comboBox.currentText() if self.comboBox.count() else "—"
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

        # tableWidget_2 columnas: 0=etiqueta (ya viene del .ui), 1=valor
        self._set_resumen_celda(0, 1, pyme_nombre)
        self._set_resumen_celda(1, 1, metodo_label)
        self._set_resumen_celda(2, 1, productos_txt)
        self._set_resumen_celda(3, 1, _formatear_clp(total))
        self._set_resumen_celda(4, 1, _formatear_clp(iva))
        self._set_resumen_celda(5, 1, _formatear_clp(comision) if comision is not None else "$0")

        # tableWidget_3: total final (única fila, columna 1)
        self._set_total_celda(_formatear_clp(total))

    def _set_resumen_celda(self, fila: int, col: int, texto: str) -> None:
        item = self.tableWidget_2.item(fila, col)
        if item is None:
            item = QTableWidgetItem()
            self.tableWidget_2.setItem(fila, col, item)
        item.setText(texto)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def _set_total_celda(self, texto: str) -> None:
        item = self.tableWidget_3.item(0, 1)
        if item is None:
            item = QTableWidgetItem()
            self.tableWidget_3.setItem(0, 1, item)
        item.setText(texto)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    # ── guardar / reset ──────────────────────────────────────────────────────

    def _guardar_venta(self) -> None:
        pyme_id = self.comboBox.currentData()
        if pyme_id is None:
            QMessageBox.warning(self, "Falta Pyme", "Seleccioná una Pyme antes de guardar.")
            return

        items = self._items_actuales()
        if not items:
            QMessageBox.warning(
                self,
                "Sin productos",
                "Agregá al menos un producto antes de guardar la venta.",
            )
            return

        if not (self.radioButton.isChecked() or self.radioButton_2.isChecked()):
            QMessageBox.warning(self, "Falta método", "Seleccioná efectivo o SumUp.")
            return

        comentario = self.textEdit_3.toPlainText().strip()
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

    def _reset_form(self) -> None:
        self.tableWidget.setRowCount(0)
        self.textEdit.clear()
        self.textEdit_3.clear()
        self.cantidad.setValue(1)
        self.Valor.setValue(1)
        self.dateEdit.setDate(date.today())
        self._actualizar_resumen()
