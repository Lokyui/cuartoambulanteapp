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
from src.ui.utils import fecha_legible, formatear_clp

UI_PATH = str(Path(__file__).parent / "dashboard.ui")


class DashboardView(QWidget):
    solicitar_vista_ventas = pyqtSignal()
    solicitar_vista_retiros = pyqtSignal()

    def __init__(
        self,
        ventas_mod: VentasModule,
        retiros_mod: RetirosModule,
        caja_module: CajaModule,
        parent=None,
    ) -> None:
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
        self.lblFecha.setText(fecha_legible(hoy))

        resumen = self.ventas_mod.resumen_del_dia(hoy)
        pendientes = self.retiros_mod.listar_pendientes()

        self._pintar_tarjetas(resumen, pendientes)
        self._pintar_ventas_recientes(resumen["recientes"])
        self._pintar_ventas_por_tienda(resumen["por_tienda"])
        self._pintar_retiros_pendientes(pendientes)

    def _pintar_tarjetas(self, resumen, pendientes) -> None:
        self.lblNumeroVentas.setText(str(resumen["n_ventas"]))
        self.lblTotalDia.setText(formatear_clp(resumen["total"]))
        self.lblTotalSinComision.setText(formatear_clp(resumen["sin_comision"]))
        self.lblEntregasPendientes.setText(str(len(pendientes)))

    def _pintar_ventas_recientes(self, recientes) -> None:
        self.tablaVentasRecientes.setRowCount(0)
        for v in recientes:
            fila = self.tablaVentasRecientes.rowCount()
            self.tablaVentasRecientes.insertRow(fila)
            self.tablaVentasRecientes.setItem(fila, 0, QTableWidgetItem(str(v["fecha"])))
            self.tablaVentasRecientes.setItem(fila, 1, QTableWidgetItem(v["pyme_nombre"]))
            self.tablaVentasRecientes.setItem(fila, 2, QTableWidgetItem(v["articulo"]))
            self.tablaVentasRecientes.setItem(fila, 3, QTableWidgetItem(formatear_clp(v["total"])))
            self.tablaVentasRecientes.setItem(fila, 4, QTableWidgetItem(v["metodo"].capitalize()))

    def _pintar_ventas_por_tienda(self, por_tienda) -> None:
        self.tablaVentasPorTienda.setRowCount(0)
        for nombre, total in por_tienda:
            fila = self.tablaVentasPorTienda.rowCount()
            self.tablaVentasPorTienda.insertRow(fila)
            self.tablaVentasPorTienda.setItem(fila, 0, QTableWidgetItem(nombre))
            self.tablaVentasPorTienda.setItem(fila, 1, QTableWidgetItem(formatear_clp(total)))

    def _pintar_retiros_pendientes(self, paquetes) -> None:
        cards = [
            (self.cardRetiro1, self.lblRetiroNombre1, self.lblRetiroEstado1, self.lblRetiroUbicacion1),
            (self.cardRetiro2, self.lblRetiroNombre2, self.lblRetiroEstado2, self.lblRetiroUbicacion2),
            (self.cardRetiro3, self.lblRetiroNombre3, self.lblRetiroEstado3, self.lblRetiroUbicacion3),
        ]
        self.cardSinRetiros.setVisible(not paquetes)
        for i, (card, nombre, estado, ubic) in enumerate(cards):
            if i >= len(paquetes):
                card.setVisible(False)
                continue
            p = paquetes[i]
            card.setVisible(True)
            nombre.setText(p["nombre_destinatario"])
            estado.setText("Pagado" if p["estado_pago"] == "pagado" else "Por cobrar")
            ubic.setText(p["ubicacion_bodega"])
