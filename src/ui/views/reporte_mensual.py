from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import src.ui.resources_rc  # noqa: F401
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)

from src.modules.reportes_module import ReportesModule
from src.ui.utils import formatear_clp

UI_PATH = str(Path(__file__).parent / "reporte_mensual.ui")

MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

COL_PYME, COL_EFECTIVO, COL_SUMUP, COL_TOTAL_BRUTO = 0, 1, 2, 3
COL_IVA, COL_COMISION, COL_NETO, COL_N_VENTAS = 4, 5, 6, 7

CAMPOS_AGREGABLES = ["efectivo", "sumup", "total_bruto", "iva", "comision_sumup", "neto", "n_ventas"]
COLOR_FILA_TOTALES = QColor("#D6EAF8")
OPCION_TODAS = "Todas las tiendas"


class ReporteMensualView(QWidget):
    def __init__(self, module: ReportesModule, parent=None) -> None:
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_tabla()
        self._configurar_tabla_dia()
        self._poblar_combos()

        self.comboBox.currentIndexChanged.connect(self._cargar_reporte)
        self.comboBox_2.currentIndexChanged.connect(self._cargar_reporte)
        self.cmbTienda.currentIndexChanged.connect(self._cargar_reporte)
        self.cmbTienda.currentIndexChanged.connect(self._cargar_detalle_dia)
        self.fechaDia.dateChanged.connect(self._cargar_detalle_dia)

        hoy = date.today()
        self.comboBox.setCurrentIndex(hoy.month - 1)
        self.comboBox_2.setCurrentText(str(hoy.year))
        self._cargar_reporte()
        self._cargar_detalle_dia()

    def _configurar_tabla(self) -> None:
        tw = self.tableWidget
        tw.setEditTriggers(tw.EditTrigger.NoEditTriggers)
        tw.setSelectionBehavior(tw.SelectionBehavior.SelectRows)
        tw.setAlternatingRowColors(True)
        tw.setSortingEnabled(True)

        header = tw.horizontalHeader()
        header.setSectionResizeMode(COL_PYME, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 8):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

    def _configurar_tabla_dia(self) -> None:
        td = self.tablaDia
        td.setEditTriggers(td.EditTrigger.NoEditTriggers)
        td.setSelectionBehavior(td.SelectionBehavior.SelectRows)
        td.setAlternatingRowColors(True)
        td.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        td.horizontalHeader().setStretchLastSection(True)

    def _poblar_combos(self) -> None:
        self.comboBox.clear()
        self.comboBox.addItems(MESES)

        self.comboBox_2.clear()
        anio_actual = date.today().year
        for anio in range(anio_actual - 3, anio_actual + 1):
            self.comboBox_2.addItem(str(anio))
        self.comboBox_2.setCurrentText(str(anio_actual))

        self.cmbTienda.clear()
        self.cmbTienda.addItem(OPCION_TODAS, None)
        for p in self.module.listar_pymes():
            self.cmbTienda.addItem(p["nombre"], p["id"])

    def _filtrar_filas(self, filas: list[dict[str, Any]]) -> list[dict[str, Any]]:
        nombre = self.cmbTienda.currentText()
        if nombre == OPCION_TODAS:
            return filas
        return [f for f in filas if f["nombre"] == nombre]

    def _cargar_reporte(self) -> None:
        mes = self.comboBox.currentIndex() + 1
        anio = int(self.comboBox_2.currentText())

        try:
            data = self.module.reporte_mensual(anio, mes)
        except Exception as exc:
            QMessageBox.critical(self, "Error al cargar reporte", f"No se pudo obtener el reporte:\n{exc}")
            return

        filas = self._filtrar_filas(data["filas"])
        totales = {c: sum(f[c] for f in filas) for c in CAMPOS_AGREGABLES}

        self._pintar_tarjetas(totales)
        self._pintar_tabla(filas, totales)

    def _cargar_detalle_dia(self) -> None:
        fecha = self.fechaDia.date().toPyDate()
        pyme_id = self.cmbTienda.currentData()
        try:
            ventas = self.module.detalle_dia(fecha, pyme_id=pyme_id)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el detalle:\n{exc}")
            return

        td = self.tablaDia
        td.setRowCount(0)
        for v in ventas:
            fila = td.rowCount()
            td.insertRow(fila)
            td.setItem(fila, 0, self._item(v.get("pyme_nombre", "—"), alinear="izq"))
            td.setItem(fila, 1, self._item(v["articulo"], alinear="izq"))
            td.setItem(fila, 2, self._item(str(v["cantidad"]), alinear="cen"))
            td.setItem(fila, 3, self._item(formatear_clp(v["total"])))
            td.setItem(fila, 4, self._item(v["metodo"].upper(), alinear="cen"))
            td.setItem(fila, 5, self._item(v.get("comentario") or "", alinear="izq"))

        suf = "" if pyme_id is None else f" — {self.cmbTienda.currentText()}"
        self.lblDetalleTitulo.setText(f"Ventas del día{suf} ({len(ventas)})")

    def _pintar_tarjetas(self, totales: dict[str, Any]) -> None:
        self.lblTotalBruto.setText(formatear_clp(totales["total_bruto"]))
        self.lblTotalEfectivo.setText(formatear_clp(totales["efectivo"]))
        self.lblTotalSumUp.setText(formatear_clp(totales["sumup"]))
        self.lblIvaTotal.setText(formatear_clp(totales["iva"]))
        self.lblComisionSumUp.setText(formatear_clp(totales["comision_sumup"]))
        self.lblNetoLiquidar.setText(formatear_clp(totales["neto"]))

    def _pintar_tabla(self, filas: list[dict[str, Any]], totales: dict[str, Any]) -> None:
        tw = self.tableWidget
        tw.setSortingEnabled(False)
        tw.setRowCount(0)

        for datos in filas:
            self._insertar_fila(datos)
        if filas:
            self._insertar_fila_totales(totales)

        tw.setSortingEnabled(True)

    def _insertar_fila(self, datos: dict[str, Any]) -> None:
        tw = self.tableWidget
        fila = tw.rowCount()
        tw.insertRow(fila)
        tw.setItem(fila, COL_PYME,        self._item(datos["nombre"], alinear="izq"))
        tw.setItem(fila, COL_EFECTIVO,    self._item(formatear_clp(datos["efectivo"])))
        tw.setItem(fila, COL_SUMUP,       self._item(formatear_clp(datos["sumup"])))
        tw.setItem(fila, COL_TOTAL_BRUTO, self._item(formatear_clp(datos["total_bruto"])))
        tw.setItem(fila, COL_IVA,         self._item(formatear_clp(datos["iva"])))
        tw.setItem(fila, COL_COMISION,    self._item(formatear_clp(datos["comision_sumup"])))
        tw.setItem(fila, COL_NETO,        self._item(formatear_clp(datos["neto"])))
        tw.setItem(fila, COL_N_VENTAS,    self._item(str(datos["n_ventas"])))

    def _insertar_fila_totales(self, totales: dict[str, Any]) -> None:
        tw = self.tableWidget
        fila = tw.rowCount()
        tw.insertRow(fila)
        items = [
            self._item("TOTAL", alinear="izq", negrita=True),
            self._item(formatear_clp(totales["efectivo"]),       negrita=True),
            self._item(formatear_clp(totales["sumup"]),          negrita=True),
            self._item(formatear_clp(totales["total_bruto"]),    negrita=True),
            self._item(formatear_clp(totales["iva"]),            negrita=True),
            self._item(formatear_clp(totales["comision_sumup"]), negrita=True),
            self._item(formatear_clp(totales["neto"]),           negrita=True),
            self._item(str(totales["n_ventas"]),                 negrita=True),
        ]
        for col, item in enumerate(items):
            item.setBackground(COLOR_FILA_TOTALES)
            tw.setItem(fila, col, item)

    @staticmethod
    def _item(texto: str, alinear: str = "der", negrita: bool = False) -> QTableWidgetItem:
        item = QTableWidgetItem(texto)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if alinear == "izq":
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        elif alinear == "cen":
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if negrita:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        return item
