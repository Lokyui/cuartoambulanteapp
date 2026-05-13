from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from ui.views.dashboard import DashboardView
from ui.views.ventas import VentasView
from ui.views.reporte_mensual import ReporteMensualView
from ui.views.retiros import RetirosView
from ui.views.resumen_caja import ResumenCajaView
from ui.views.reporte_pyme import ReportePymeView
from modules.ventas_module import VentasModule
from modules.retiros_module import RetirosModule
from modules.reportes_module import ReportesModule
from modules.caja_module import CajaModule
from db.dal import DAL


UI_PATH = "src/ui/views/main_window.ui"


class MainWindow(QMainWindow):
    def __init__(self, ventas_mod: VentasModule, retiros_mod: RetirosModule, reportesModule: ReportesModule, caja_module: CajaModule, parent=None):
        super().__init__(parent)

        uic.loadUi(UI_PATH, self)

        # =========================
        # VISTAS
        # =========================
        self.dashboard = DashboardView(ventas_mod, retiros_mod, caja_module)
        self.ventas = VentasView(ventas_mod)
        self.reporte = ReporteMensualView(reportesModule)
        self.retiros = RetirosView(retiros_mod)
        self.resumen_caja = ResumenCajaView(caja_module)
        self.reporte_pyme = ReportePymeView(reportesModule)

        # =========================
        # STACKED WIDGET
        # =========================
        self.stackedWidget.addWidget(self.dashboard)
        self.stackedWidget.addWidget(self.ventas)
        self.stackedWidget.addWidget(self.reporte)
        self.stackedWidget.addWidget(self.retiros)
        self.stackedWidget.addWidget(self.resumen_caja)
        self.stackedWidget.addWidget(self.reporte_pyme)

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

        self.btnPymes.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.reporte_pyme)
        )

        # Cuando el dashboard pida ventas, cambiamos el widget actual
        self.dashboard.solicitar_vista_ventas.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ventas)
        )
        
        # Cuando el dashboard pida retiros, hacemos lo mismo
        self.dashboard.solicitar_vista_retiros.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.retiros)
        )

        # =========================
        # INICIO
        # =========================
        self.stackedWidget.setCurrentWidget(self.dashboard)
