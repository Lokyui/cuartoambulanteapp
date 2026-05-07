from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from ui.views.dashboard import DashboardView
from ui.views.ventas import VentasView
from ui.views.reporte_mensual import ReporteMensualView


UI_PATH = "src/ui/views/main_window.ui"


class MainWindow(QMainWindow):
    def __init__(self, dal):
        super().__init__()

        uic.loadUi(UI_PATH, self)

        # =========================
        # VISTAS
        # =========================
        self.dashboard = DashboardView(dal)
        self.ventas = VentasView(dal)
        self.reporte = ReporteMensualView(dal)

        # =========================
        # STACKED WIDGET
        # =========================
        self.stackedWidget.addWidget(self.dashboard)
        self.stackedWidget.addWidget(self.ventas)
        self.stackedWidget.addWidget(self.reporte)

        # =========================
        # BOTONES DEL SIDEBAR
        # =========================
        self.btnDashboard.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.dashboard)
        )

        self.btnVentas.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ventas)
        )

        self.btnReporte.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.reporte)
        )
