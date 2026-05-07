from __future__ import annotations

import src.ui.resources_rc 
from datetime import date
from typing import Any

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHeaderView, QTableWidgetItem, QWidget

from db.dal import DAL

UI_PATH = "src/ui/views/dashboard.ui"
 
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

class DashboardView(QWidget):
    def __init__(self, dal: DAL, parent=None) -> None:
        super().__init__(parent)
        self.dal = dal
        uic.loadUi(UI_PATH, self)

        self._configurar_tablas()
        self._cargar_datos_dia()

    def _configurar_tablas(self) -> None:
        # Tabla de ventas recientes
        tw = self.tableWidget
        tw.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Tabla de ventas por tienda
        tw2 = self.tableWidget_2
        tw2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _cargar_datos_dia(self) -> None:
        hoy = date.today()
        # Obtener nombres de las listas según el índice
        dia_semana = DIAS_ES[hoy.weekday()]
        mes = MESES_ES[hoy.month]
        fecha_formateada = f"{dia_semana} {hoy.day} de {mes}, {hoy.year}"

        # Actualizar la UI
        self.plainTextEdit_10.setPlainText(fecha_formateada)

        # Obtener ventas del día
        ventas = self.dal.listar_ventas(fecha=hoy)
        
        # 1. Calcular resumen para tarjetas
        total_diario = sum(v["total"] for v in ventas)
        n_ventas = len(ventas)
        # Nota: Estas tarjetas usan nombres de objeto similares a reporte_mensual
        self.textEdit_36.setHtml(self._html_valor(f"${total_diario:,.0f}".replace(",", ".")))
        self.textEdit_38.setHtml(self._html_valor(str(n_ventas)))

        # 2. Poblar tabla de ventas recientes (últimas 10)
        self.tableWidget.setRowCount(0)
        for v in ventas[:10]:
            fila = self.tableWidget.rowCount()
            self.tableWidget.insertRow(fila)
            self.tableWidget.setItem(fila, 0, QTableWidgetItem(str(v["fecha"])))
            self.tableWidget.setItem(fila, 3, QTableWidgetItem(f"${v['total']}"))

    @staticmethod
    def _html_valor(texto: str) -> str:
        return f'<p align="center" style="margin:0; font-size:14pt; font-weight:600;">{texto}</p>'
