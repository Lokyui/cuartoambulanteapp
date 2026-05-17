from __future__ import annotations

from datetime import date
from pathlib import Path

import src.ui.resources_rc  # noqa: F401
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from src.modules.ventas_module import VentasModule
from src.modules.retiros_module import RetirosModule
from src.modules.caja_module import CajaModule

UI_PATH = str(Path(__file__).parent / "dashboard.ui")

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


class DashboardView(QWidget):
    solicitar_vista_ventas = pyqtSignal()
    solicitar_vista_retiros = pyqtSignal()

    def __init__(self, ventas_mod: VentasModule, retiros_mod: RetirosModule, caja_module: CajaModule, parent=None) -> None:
        super().__init__(parent)
        self.ventas_mod = ventas_mod
        self.retiros_mod = retiros_mod
        self.caja_module = caja_module
        uic.loadUi(UI_PATH, self)

        self._configurar_tablas()
        self._cargar_datos_dia()

        self.btnRegistrarVenta.clicked.connect(self.solicitar_vista_ventas.emit)
        self.btnNuevoRetiro.clicked.connect(self.solicitar_vista_retiros.emit)

    def _configurar_tablas(self) -> None:
        self.tablaVentasRecientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablaVentasPorTienda.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _cargar_datos_dia(self) -> None:
        hoy = date.today()
        dia_semana = DIAS_ES[hoy.weekday()]
        mes = MESES_ES[hoy.month]
        fecha_formateada = f"{dia_semana} {hoy.day} de {mes}, {hoy.year}"

        self.lblFecha.setText(fecha_formateada)

        ventas = self.ventas_mod.dal.listar_ventas(fecha=hoy)

        total_diario = sum(v["total"] for v in ventas)
        n_ventas = len(ventas)
        self.lblTotalDia.setText(f"${total_diario:,.0f}".replace(",", "."))
        self.lblNumeroVentas.setText(str(n_ventas))

        self.tablaVentasRecientes.setRowCount(0)
        for v in ventas[:10]:
            fila = self.tablaVentasRecientes.rowCount()
            self.tablaVentasRecientes.insertRow(fila)
            self.tablaVentasRecientes.setItem(fila, 0, QTableWidgetItem(str(v["fecha"])))
            self.tablaVentasRecientes.setItem(fila, 3, QTableWidgetItem(f"${v['total']}"))
