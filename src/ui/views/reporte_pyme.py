from __future__ import annotations

from datetime import date
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from src.modules.reportes_module import ReportesModule
from src.ui.utils import formatear_clp

UI_PATH = str(Path(__file__).parent / "reporte_pyme.ui")


class ReportePymeView(QWidget):
    def __init__(self, module: ReportesModule):
        super().__init__()
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_tabla()
        self._cargar_pymes()

        hoy = date.today()
        self.dateEdit.setDate(date(hoy.year, hoy.month, 1))
        self.dateEdit_2.setDate(hoy)

        self.comboBox.currentIndexChanged.connect(self.actualizar_reporte)
        self.dateEdit.dateChanged.connect(self.actualizar_reporte)
        self.dateEdit_2.dateChanged.connect(self.actualizar_reporte)

        self.actualizar_reporte()

    def _configurar_tabla(self) -> None:
        tw = self.tableWidget
        header = tw.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        tw.setEditTriggers(tw.EditTrigger.NoEditTriggers)
        tw.setSelectionBehavior(tw.SelectionBehavior.SelectRows)
        tw.setAlternatingRowColors(True)

    def _cargar_pymes(self) -> None:
        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        for p in self.module.listar_pymes():
            self.comboBox.addItem(p["nombre"], p["id"])
        self.comboBox.blockSignals(False)

    def actualizar_reporte(self) -> None:
        pyme_id = self.comboBox.currentData()
        if pyme_id is None:
            return

        desde = self.dateEdit.date().toString("yyyy-MM-dd")
        hasta = self.dateEdit_2.date().toString("yyyy-MM-dd")
        data = self.module.detalle_pyme(pyme_id, desde, hasta)
        resumen = data["resumen"]

        self.lblIvaTotal.setText(formatear_clp(resumen["total_iva"]))
        self.lblTotalSumUp.setText(formatear_clp(resumen["total_sumup"]))
        self.lblComisionSumUp.setText(formatear_clp(resumen["total_comision"]))
        self.lblTotalEfectivo.setText(formatear_clp(resumen["total_efectivo"]))
        self.lblNVentas.setText(str(resumen["n_ventas"]))
        self.lblNetoLiquidar.setText(formatear_clp(resumen["neto_liquidar"]))

        self.tableWidget.setRowCount(0)
        for v in data["detalle"]:
            fila = self.tableWidget.rowCount()
            self.tableWidget.insertRow(fila)
            self.tableWidget.setItem(fila, 0, self._item(v["fecha"], alinear="izq"))
            self.tableWidget.setItem(fila, 1, self._item(v["articulo"], alinear="izq"))
            self.tableWidget.setItem(fila, 2, self._item(formatear_clp(v["valor"])))
            self.tableWidget.setItem(fila, 3, self._item(str(v["cantidad"]), alinear="cen"))
            self.tableWidget.setItem(fila, 4, self._item(formatear_clp(v["total"])))
            self.tableWidget.setItem(fila, 5, self._item(formatear_clp(v["iva"])))
            self.tableWidget.setItem(fila, 6, self._item(formatear_clp(v["comision_sumup"])))
            self.tableWidget.setItem(fila, 7, self._item(v["metodo"].upper(), alinear="cen"))
            self.tableWidget.setItem(fila, 8, self._item(v["comentario"] or "", alinear="izq"))

    @staticmethod
    def _item(texto: str, alinear: str = "der") -> QTableWidgetItem:
        item = QTableWidgetItem(str(texto))
        if alinear == "cen":
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        elif alinear == "izq":
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return item
