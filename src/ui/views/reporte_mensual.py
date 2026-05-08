"""
Carga el .ui generado por Qt Designer y conecta la lógica
de consulta a través del DAL. No contiene SQL directo.
"""
from __future__ import annotations
 
import src.ui.resources_rc 
import calendar
from datetime import date
from typing import Any
import calendar
 
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog,
    QHeaderView,
    QTableWidgetItem,
    QMessageBox,
)
 
from db.dal import DAL
 
# Ruta al archivo .ui relativa a este módulo
UI_PATH = "src/ui/views/reporte_mensual.ui"
 
# Meses en español para poblar el ComboBox
MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
 
# Columnas de la QTableWidget (deben coincidir con el .ui)
COL_PYME        = 0
COL_EFECTIVO    = 1
COL_SUMUP       = 2
COL_TOTAL_BRUTO = 3
COL_IVA         = 4
COL_COMISION    = 5
COL_NETO        = 6
COL_N_VENTAS    = 7
 
# Color de la fila de totales
COLOR_FILA_TOTALES = QColor("#D6EAF8")
 
 
class ReporteMensualView(QDialog):
    """
    Diálogo de reporte mensual.
 
    Uso:
        dal = DAL()
        vista = ReporteMensualView(dal, parent=main_window)
        vista.exec()
    """
 
    def __init__(self, dal: DAL, parent=None) -> None:
        super().__init__(parent)
        self.dal = dal
        uic.loadUi(UI_PATH, self)
 
        self._configurar_tabla()
        self._poblar_combos()
        self._conectar_senales()
 
        # Cargar el mes y año actuales al abrir
        hoy = date.today()
        self.comboBox.setCurrentIndex(hoy.month - 1)
        self.comboBox_2.setCurrentText(str(hoy.year))
        self._cargar_reporte()
 
    # ─────────────────────────────────────────────
    # Configuración inicial de widgets
    # ─────────────────────────────────────────────
 
    def _configurar_tabla(self) -> None:
        """Ajusta comportamiento de la QTableWidget."""
        tw = self.tableWidget
        tw.setEditTriggers(tw.EditTrigger.NoEditTriggers)
        tw.setSelectionBehavior(tw.SelectionBehavior.SelectRows)
        tw.setAlternatingRowColors(True)
 
        header = tw.horizontalHeader()
        # Pyme/Tienda se expande; el resto toma su contenido
        header.setSectionResizeMode(COL_PYME, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 8):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
 
        tw.setSortingEnabled(True)
 
    def _poblar_combos(self) -> None:
        """Rellena los ComboBox de mes y año."""
        self.comboBox.clear()
        self.comboBox.addItems(MESES)
 
        self.comboBox_2.clear()
        anio_actual = date.today().year
        # Ofrecer 3 años hacia atrás y el año actual
        for anio in range(anio_actual - 3, anio_actual + 1):
            self.comboBox_2.addItem(str(anio))
        self.comboBox_2.setCurrentText(str(anio_actual))
 
    def _conectar_senales(self) -> None:
        """Conecta señales de los widgets a sus manejadores."""
        self.comboBox.currentIndexChanged.connect(self._cargar_reporte)
        self.comboBox_2.currentIndexChanged.connect(self._cargar_reporte)
 
    # ─────────────────────────────────────────────
    # Lógica de carga de datos
    # ─────────────────────────────────────────────
 
    def _cargar_reporte(self) -> None:
        """
        Obtiene los datos del período seleccionado y actualiza
        las tarjetas de resumen y la tabla.
        """
        mes  = self.comboBox.currentIndex() + 1   # 1–12
        anio = int(self.comboBox_2.currentText())
 
        try:
            filas = self.dal.reporte_mensual(anio, mes)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error al cargar reporte",
                f"No se pudo obtener el reporte mensual:\n{exc}",
            )
            return
 
        self._actualizar_tarjetas(filas)
        self._actualizar_tabla(filas)
 
    def _actualizar_tarjetas(self, filas: list[dict[str, Any]]) -> None:
        """Calcula los totales consolidados y los muestra en las tarjetas."""
        total_bruto  = sum(f["total_bruto"]    for f in filas)
        total_ef     = sum(f["efectivo"]        for f in filas)
        total_su     = sum(f["sumup"]           for f in filas)
        total_iva    = sum(f["iva"]             for f in filas)
        total_comis  = sum(f["comision_sumup"]  for f in filas)
        total_neto   = sum(f["neto"]            for f in filas)
 
        # textEdit_36 → Total bruto
        self.textEdit_36.setHtml(self._html_valor(self._fmt(total_bruto)))
        # textEdit_37 → Total efectivo
        self.textEdit_37.setHtml(self._html_valor(self._fmt(total_ef)))
        # textEdit_38 → Total SumUp
        self.textEdit_38.setHtml(self._html_valor(self._fmt(total_su)))
        # textEdit_39 → IVA total
        self.textEdit_39.setHtml(self._html_valor(self._fmt(total_iva)))
        # textEdit_41 → Comisión SumUp total
        self.textEdit_41.setHtml(self._html_valor(self._fmt(total_comis)))
        # textEdit_43 → Neto a liquidar
        self.textEdit_43.setHtml(self._html_valor(self._fmt(total_neto)))
 
    def _actualizar_tabla(self, filas: list[dict[str, Any]]) -> None:
        """Rellena la QTableWidget con una fila por pyme y una fila de totales."""
        tw = self.tableWidget
        # Deshabilitar sorting temporalmente para evitar reordenamientos durante insert
        tw.setSortingEnabled(False)
        tw.setRowCount(0)
 
        for datos in filas:
            self._insertar_fila(datos)
 
        # Fila de totales
        self._insertar_fila_totales(filas)
 
        tw.setSortingEnabled(True)
 
    def _insertar_fila(self, datos: dict[str, Any]) -> None:
        """Agrega una fila de datos de pyme a la tabla."""
        tw = self.tableWidget
        fila = tw.rowCount()
        tw.insertRow(fila)
 
        tw.setItem(fila, COL_PYME,        self._item(datos["nombre"],           alinear="izq"))
        tw.setItem(fila, COL_EFECTIVO,    self._item(self._fmt(datos["efectivo"])))
        tw.setItem(fila, COL_SUMUP,       self._item(self._fmt(datos["sumup"])))
        tw.setItem(fila, COL_TOTAL_BRUTO, self._item(self._fmt(datos["total_bruto"])))
        tw.setItem(fila, COL_IVA,         self._item(self._fmt(datos["iva"])))
        tw.setItem(fila, COL_COMISION,    self._item(self._fmt(datos["comision_sumup"])))
        tw.setItem(fila, COL_NETO,        self._item(self._fmt(datos["neto"])))
        tw.setItem(fila, COL_N_VENTAS,    self._item(str(datos["n_ventas"])))
 
    def _insertar_fila_totales(self, filas: list[dict[str, Any]]) -> None:
        """Agrega la fila de totales con fondo destacado al final de la tabla."""
        tw = self.tableWidget
        fila = tw.rowCount()
        tw.insertRow(fila)
 
        totales = {
            "nombre":        "TOTAL",
            "efectivo":      sum(f["efectivo"]       for f in filas),
            "sumup":         sum(f["sumup"]          for f in filas),
            "total_bruto":   sum(f["total_bruto"]    for f in filas),
            "iva":           sum(f["iva"]            for f in filas),
            "comision_sumup":sum(f["comision_sumup"] for f in filas),
            "neto":          sum(f["neto"]           for f in filas),
            "n_ventas":      sum(f["n_ventas"]       for f in filas),
        }
 
        items = [
            self._item(totales["nombre"],                   alinear="izq", negrita=True),
            self._item(self._fmt(totales["efectivo"]),      negrita=True),
            self._item(self._fmt(totales["sumup"]),         negrita=True),
            self._item(self._fmt(totales["total_bruto"]),   negrita=True),
            self._item(self._fmt(totales["iva"]),           negrita=True),
            self._item(self._fmt(totales["comision_sumup"]),negrita=True),
            self._item(self._fmt(totales["neto"]),          negrita=True),
            self._item(str(totales["n_ventas"]),            negrita=True),
        ]
 
        for col, item in enumerate(items):
            item.setBackground(COLOR_FILA_TOTALES)
            tw.setItem(fila, col, item)
 
    # ─────────────────────────────────────────────
    # Helpers de formato y construcción de items
    # ─────────────────────────────────────────────
 
    @staticmethod
    def _fmt(valor: int | None) -> str:
        """Formatea un entero como moneda CLP: $1.234.567"""
        if valor is None:
            return "$0"
        return f"${valor:,.0f}".replace(",", ".")
 
    @staticmethod
    def _html_valor(texto: str, pt: int = 14) -> str:
        """Genera HTML de una línea centrada para los QTextEdit de las tarjetas."""
        return (
            f'<p align="center" style="margin:0; font-size:{pt}pt;">'
            f"{texto}</p>"
        )
 
    @staticmethod
    def _item(
        texto: str,
        alinear: str = "der",
        negrita: bool = False,
    ) -> QTableWidgetItem:
        """Crea un QTableWidgetItem con alineación y estilo opcionales."""
        item = QTableWidgetItem(texto)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
 
        if alinear == "der":
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        else:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
 
        if negrita:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
 
        return item

