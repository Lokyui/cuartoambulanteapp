from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QHeaderView,
)

from src.modules.reportes_module import ReportesModule

UI_PATH = str(Path(__file__).parent / "reporte_pyme.ui")

class ReportePymeView(QWidget):
    def __init__(self, module: ReportesModule):
        super().__init__()
        self.module = module
        
        # Carga del UI
        uic.loadUi(UI_PATH, self)
        
        # Configuración inicial
        self._configurar_tabla()
        self._cargar_pymes()
        
        # Fechas iniciales: desde el 1ero del mes actual hasta hoy
        from datetime import date
        hoy = date.today()
        primero_mes = date(hoy.year, hoy.month, 1)
        
        self.dateEdit.setDate(primero_mes)
        self.dateEdit_2.setDate(hoy)
        
        # Conexiones de señales
        self.comboBox.currentIndexChanged.connect(self.actualizar_reporte)
        self.dateEdit.dateChanged.connect(self.actualizar_reporte)
        self.dateEdit_2.dateChanged.connect(self.actualizar_reporte)
        
        # Carga inicial de datos
        self.actualizar_reporte()

    def _configurar_tabla(self) -> None:
        """Ajusta el comportamiento de la QTableWidget."""
        tw = self.tableWidget
        header = tw.horizontalHeader()
        # Ajuste responsivo de columnas
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Artículo se estira
        
        tw.setEditTriggers(tw.EditTrigger.NoEditTriggers)
        tw.setSelectionBehavior(tw.SelectionBehavior.SelectRows)
        tw.setAlternatingRowColors(True)

    def _cargar_pymes(self) -> None:
        """Pobla el combobox con las PYMEs activas."""
        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        try:
            pymes = self.module.dal.listar_pymes(solo_activas=True)
            for p in pymes:
                self.comboBox.addItem(p["nombre"], p["id"])
        except Exception as e:
            print(f"Error al cargar PYMEs: {e}")
        self.comboBox.blockSignals(False)

    def actualizar_reporte(self) -> None:
        """Consulta al DAL y actualiza la vista."""
        pyme_id = self.comboBox.currentData()
        if pyme_id is None:
            return

        desde = self.dateEdit.date().toString("yyyy-MM-dd")
        hasta = self.dateEdit_2.date().toString("yyyy-MM-dd")

        try:
            data = self.module.dal.obtener_detalle_reporte_pyme(pyme_id, desde, hasta)
            resumen = data["resumen"]
            detalle = data["detalle"]

            # 1. Actualizar Tarjetas de Totales (QTextEdit/QPlainTextEdit)
            self.textEdit_37.setPlainText(self._fmt(resumen['neto_liquidar']))
            self.textEdit_48.setPlainText(str(resumen['n_ventas']))
            self.textEdit_45.setPlainText(self._fmt(resumen['total_efectivo']))
            self.textEdit_42.setPlainText(self._fmt(resumen['total_sumup']))
            self.textEdit_43.setPlainText(self._fmt(resumen['total_iva']))
            self.textEdit_36.setPlainText(self._fmt(resumen['total_comision']))

            # 2. Actualizar Tabla
            self.tableWidget.setRowCount(0)
            for v in detalle:
                fila = self.tableWidget.rowCount()
                self.tableWidget.insertRow(fila)
                
                self.tableWidget.setItem(fila, 0, self._item(v["fecha"], alinear="izq"))
                self.tableWidget.setItem(fila, 1, self._item(v["articulo"], alinear="izq"))
                self.tableWidget.setItem(fila, 2, self._item(self._fmt(v["valor"])))
                self.tableWidget.setItem(fila, 3, self._item(str(v["cantidad"]), alinear="cen"))
                self.tableWidget.setItem(fila, 4, self._item(self._fmt(v["total"])))
                self.tableWidget.setItem(fila, 5, self._item(self._fmt(v["iva"])))
                self.tableWidget.setItem(fila, 6, self._item(self._fmt(v["comision_sumup"])))
                self.tableWidget.setItem(fila, 7, self._item(v["metodo"].upper(), alinear="cen"))
                self.tableWidget.setItem(fila, 8, self._item(v["comentario"] or "", alinear="izq"))

        except Exception as e:
            print(f"Error al actualizar reporte: {e}")

    @staticmethod
    def _fmt(valor: int | float | None) -> str:
        """Formatea como moneda CLP: $1.234.567"""
        if valor is None: return "$0"
        return f"${valor:,.0f}".replace(",", ".")

    @staticmethod
    def _item(texto: str, alinear: str = "der") -> QTableWidgetItem:
        item = QTableWidgetItem(str(texto))
        if alinear == "der":
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        elif alinear == "cen":
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item