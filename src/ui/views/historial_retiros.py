from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from src.modules.retiros_module import HISTORIAL_DIAS_DEFAULT, RetirosModule

UI_PATH = str(Path(__file__).parent / "historial_retiros.ui")
OPCION_TODAS = "Todas las tiendas"


class HistorialRetirosView(QWidget):
    def __init__(self, module: RetirosModule, parent=None) -> None:
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_tabla()
        self._poblar_tiendas()
        self._inicializar_fechas()
        self._conectar_signals()
        self.actualizar()

    def _configurar_tabla(self) -> None:
        tw = self.tablaHistorial
        tw.setEditTriggers(tw.NoEditTriggers)
        tw.setSelectionBehavior(tw.SelectRows)
        tw.setAlternatingRowColors(True)
        header = tw.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def _poblar_tiendas(self) -> None:
        self.cmbTienda.blockSignals(True)
        self.cmbTienda.clear()
        self.cmbTienda.addItem(OPCION_TODAS, None)
        # solo_activas=False: el historial puede tener entregas de pymes ya desactivadas.
        for p in self.module.listar_pymes(solo_activas=False):
            self.cmbTienda.addItem(p["nombre"], p["id"])
        self.cmbTienda.blockSignals(False)

    def _inicializar_fechas(self) -> None:
        hoy = date.today()
        self.fechaDesde.setDate(hoy - timedelta(days=HISTORIAL_DIAS_DEFAULT))
        self.fechaHasta.setDate(hoy)

    def _conectar_signals(self) -> None:
        self.fechaDesde.dateChanged.connect(self.actualizar)
        self.fechaHasta.dateChanged.connect(self.actualizar)
        self.cmbTienda.currentIndexChanged.connect(self.actualizar)
        self.txtBuscar.textChanged.connect(self.actualizar)
        self.btnLimpiarFiltros.clicked.connect(self._limpiar_filtros)

    def _limpiar_filtros(self) -> None:
        self.txtBuscar.blockSignals(True)
        self.cmbTienda.blockSignals(True)
        self.fechaDesde.blockSignals(True)
        self.fechaHasta.blockSignals(True)

        self.txtBuscar.clear()
        self.cmbTienda.setCurrentIndex(0)
        self._inicializar_fechas()

        self.txtBuscar.blockSignals(False)
        self.cmbTienda.blockSignals(False)
        self.fechaDesde.blockSignals(False)
        self.fechaHasta.blockSignals(False)
        self.actualizar()

    def actualizar(self) -> None:
        fecha_desde = self.fechaDesde.date().toPyDate()
        fecha_hasta = self.fechaHasta.date().toPyDate()
        pyme_id = self.cmbTienda.currentData()
        texto = self.txtBuscar.text().strip() or None

        paquetes = self.module.listar_historial(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            pyme_id=pyme_id,
            busqueda=texto,
        )

        self.lblConteo.setText(f"{len(paquetes)} entrega{'s' if len(paquetes) != 1 else ''}")
        self._pintar(paquetes)

    def _pintar(self, paquetes: list[dict]) -> None:
        tw = self.tablaHistorial
        tw.setRowCount(0)
        for p in paquetes:
            fila = tw.rowCount()
            tw.insertRow(fila)
            tw.setItem(fila, 0, self._item(self._formatear_fecha(p["fecha_entrega"]), alinear="cen"))
            tw.setItem(fila, 1, self._item(p["nombre_destinatario"], alinear="izq"))
            tw.setItem(fila, 2, self._item(p.get("nombre_pyme") or "—", alinear="izq"))
            tw.setItem(fila, 3, self._item(p["ubicacion_bodega"], alinear="cen"))
            tw.setItem(fila, 4, self._item(
                "Pagado" if p["estado_pago"] == "pagado" else "Por cobrar",
                alinear="cen",
            ))
            tw.setItem(fila, 5, self._item(p.get("descripcion") or "", alinear="izq"))

    @staticmethod
    def _formatear_fecha(valor: str | None) -> str:
        if not valor:
            return "—"
        # Soporta tanto 'YYYY-MM-DD' como 'YYYY-MM-DD HH:MM:SS'.
        return str(valor).split(" ")[0]

    @staticmethod
    def _item(texto: str, alinear: str = "der") -> QTableWidgetItem:
        item = QTableWidgetItem(str(texto))
        if alinear == "izq":
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        elif alinear == "cen":
            item.setTextAlignment(Qt.AlignCenter)
        else:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item
