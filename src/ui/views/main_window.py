from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from ui.views.dashboard import DashboardView
from ui.views.ventas import VentasView
from ui.views.reporte_mensual import ReporteMensualView
from ui.views.retiros import RetirosView
from ui.views.resumen_caja import ResumenCajaView


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
        self.retiros = RetirosView(dal)
        self.resumen_caja = ResumenCajaView(dal)

        # =========================
        # STACKED WIDGET
        # =========================
        self.stackedWidget.addWidget(self.dashboard)
        self.stackedWidget.addWidget(self.ventas)
        self.stackedWidget.addWidget(self.reporte)
        self.stackedWidget.addWidget(self.retiros)
        self.stackedWidget.addWidget(self.resumen_caja)

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

        self.btnRetiros.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.retiros)
        )

        self.btnCierre.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.resumen_caja)
        )

        # =========================
        # INICIO
        # =========================
        self.stackedWidget.setCurrentWidget(self.dashboard)
