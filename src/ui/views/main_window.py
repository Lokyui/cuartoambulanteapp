from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from src.ui.views.dashboard import DashboardView
from src.ui.views.ventas import VentasView
from src.ui.views.reporte_mensual import ReporteMensualView
from src.ui.views.retiros import RetirosView
from src.ui.views.historial_retiros import HistorialRetirosView
from src.ui.views.resumen_caja import ResumenCajaView
from src.ui.views.reporte_pyme import ReportePymeView
from src.ui.views.configuracion import ConfiguracionView
from src.modules.ventas_module import VentasModule
from src.modules.retiros_module import RetirosModule
from src.modules.reportes_module import ReportesModule
from src.modules.caja_module import CajaModule
from src.modules.catalogos_module import CatalogosModule


UI_PATH = str(Path(__file__).parent / "main_window.ui")


class MainWindow(QMainWindow):
    def __init__(
        self,
        ventas_mod: VentasModule,
        retiros_mod: RetirosModule,
        reportesModule: ReportesModule,
        caja_module: CajaModule,
        catalogos_module: CatalogosModule,
        parent=None,
    ):
        super().__init__(parent)

        uic.loadUi(UI_PATH, self)

        self.dashboard = DashboardView(ventas_mod, retiros_mod, caja_module)
        self.ventas = VentasView(ventas_mod)
        self.reporte = ReporteMensualView(reportesModule)
        self.retiros = RetirosView(retiros_mod)
        self.historial_retiros = HistorialRetirosView(retiros_mod)
        self.resumen_caja = ResumenCajaView(caja_module)
        self.reporte_pyme = ReportePymeView(reportesModule)
        self.configuracion = ConfiguracionView(catalogos_module)

        self.stackedWidget.addWidget(self.dashboard)
        self.stackedWidget.addWidget(self.ventas)
        self.stackedWidget.addWidget(self.reporte)
        self.stackedWidget.addWidget(self.retiros)
        self.stackedWidget.addWidget(self.historial_retiros)
        self.stackedWidget.addWidget(self.resumen_caja)
        self.stackedWidget.addWidget(self.reporte_pyme)
        self.stackedWidget.addWidget(self.configuracion)

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
        self.btnHistorialRetiros.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.historial_retiros)
        )
        self.btnCierre.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.resumen_caja)
        )
        self.btnPymes.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.reporte_pyme)
        )
        self.btnConfiguracion.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.configuracion)
        )

        self.dashboard.solicitar_vista_ventas.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ventas)
        )
        self.dashboard.solicitar_vista_retiros.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.retiros)
        )

        # Recarga centralizada: al entrar a una vista que muestra datos derivados,
        # refrescamos para que cambios hechos en otra parte se vean al volver.
        self.stackedWidget.currentChanged.connect(self._refrescar_vista_actual)
        self.stackedWidget.setCurrentWidget(self.dashboard)

    def _refrescar_vista_actual(self, _index: int) -> None:
        actual = self.stackedWidget.currentWidget()
        if actual is self.dashboard:
            self.dashboard._cargar_datos_dia()
        elif actual is self.configuracion:
            self.configuracion.recargar()
        elif actual is self.resumen_caja:
            self.resumen_caja._cargar_dia()
        elif actual is self.retiros:
            self.retiros.actualizar_vista()
        elif actual is self.historial_retiros:
            self.historial_retiros.actualizar()
        elif actual is self.reporte:
            self.reporte._cargar_reporte()
            self.reporte._cargar_detalle_dia()
        elif actual is self.reporte_pyme:
            self.reporte_pyme.actualizar_reporte()
