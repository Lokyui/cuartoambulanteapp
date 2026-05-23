from __future__ import annotations

from datetime import date
from pathlib import Path

import src.ui.resources_rc  # noqa: F401
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from src.modules.caja_module import CajaModule
from src.ui.utils import fecha_legible, formatear_clp

UI_PATH = str(Path(__file__).parent / "resumen_caja.ui")


class ResumenCajaView(QWidget):
    def __init__(self, module: CajaModule, parent=None) -> None:
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_tablas()
        self.fechaEdit.dateChanged.connect(self._cargar_dia)
        self._cargar_dia()

    def _configurar_tablas(self) -> None:
        for tabla in (self.tablaEfectivo, self.tablaSumUp):
            tabla.setEditTriggers(tabla.NoEditTriggers)
            tabla.setSelectionBehavior(tabla.SelectRows)
            tabla.setAlternatingRowColors(True)
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tablaResumen.setColumnCount(2)
        self.tablaResumen.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tablaResumen.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tablaResumen.setEditTriggers(self.tablaResumen.NoEditTriggers)
        self.tablaResumen.setSelectionMode(self.tablaResumen.NoSelection)

    def _cargar_dia(self) -> None:
        fecha = self.fechaEdit.date().toPyDate()
        self.lblFechaLegible.setText(fecha_legible(fecha))

        datos = self.module.resumen_dia(fecha)
        tot = datos["totales"]

        self.lblTotalEfectivo.setText(formatear_clp(tot["efectivo"]))
        self.lblNEfectivo.setText(f"{tot['n_efectivo']} venta{'s' if tot['n_efectivo'] != 1 else ''}")
        self.lblTotalSumUp.setText(formatear_clp(tot["sumup"]))
        self.lblNSumUp.setText(f"{tot['n_sumup']} venta{'s' if tot['n_sumup'] != 1 else ''}")
        self.lblTotalBruto.setText(formatear_clp(tot["bruto"]))
        self.lblNeto.setText(formatear_clp(tot["neto"]))

        self._pintar_resumen(datos, tot)
        self._pintar_ventas(self.tablaEfectivo, datos["ventas_efectivo"], incluir_comision=False)
        self._pintar_ventas(self.tablaSumUp, datos["ventas_sumup"], incluir_comision=True)

    def _pintar_resumen(self, datos, tot) -> None:
        filas = [
            ("Caja inicial", formatear_clp(datos["caja_inicial"])),
            ("Ventas en efectivo", formatear_clp(tot["efectivo"])),
            ("Ventas con SumUp", formatear_clp(tot["sumup"])),
            ("Total bruto del día", formatear_clp(tot["bruto"])),
            ("IVA acumulado", formatear_clp(tot["iva"])),
            ("Comisión SumUp", formatear_clp(tot["comision_sumup"])),
            ("Neto (sin IVA ni comisión)", formatear_clp(tot["neto"])),
            ("Caja final esperada", formatear_clp(datos["caja_final_esperada"])),
            ("Cantidad de ventas", str(tot["n_ventas"])),
        ]
        self.tablaResumen.setRowCount(len(filas))
        for i, (etiqueta, valor) in enumerate(filas):
            item_lbl = QTableWidgetItem(etiqueta)
            font = item_lbl.font()
            font.setBold(etiqueta in ("Total bruto del día", "Neto (sin IVA ni comisión)", "Caja final esperada"))
            item_lbl.setFont(font)

            item_val = QTableWidgetItem(valor)
            item_val.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_val.setFont(font)

            self.tablaResumen.setItem(i, 0, item_lbl)
            self.tablaResumen.setItem(i, 1, item_val)

    def _pintar_ventas(self, tabla, ventas, incluir_comision: bool) -> None:
        tabla.setRowCount(0)
        for v in ventas:
            fila = tabla.rowCount()
            tabla.insertRow(fila)
            tabla.setItem(fila, 0, QTableWidgetItem(v.get("pyme_nombre", "—")))
            tabla.setItem(fila, 1, QTableWidgetItem(v["articulo"]))

            item_cant = QTableWidgetItem(str(v["cantidad"]))
            item_cant.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(fila, 2, item_cant)

            item_total = QTableWidgetItem(formatear_clp(v["total"]))
            item_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            tabla.setItem(fila, 3, item_total)

            if incluir_comision:
                item_com = QTableWidgetItem(formatear_clp(v.get("comision_sumup") or 0))
                item_com.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tabla.setItem(fila, 4, item_com)
