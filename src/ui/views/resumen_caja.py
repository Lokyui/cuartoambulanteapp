from __future__ import annotations

from datetime import date
from pathlib import Path

import src.ui.resources_rc  # noqa: F401
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QMessageBox, QTableWidgetItem, QWidget

from src.modules.caja_module import CajaModule
from src.ui.utils import fecha_legible, formatear_clp

UI_PATH = str(Path(__file__).parent / "resumen_caja.ui")
OPCION_TODAS = "Todas las tiendas"


class ResumenCajaView(QWidget):
    def __init__(self, module: CajaModule, parent=None) -> None:
        super().__init__(parent)
        self.module = module
        uic.loadUi(UI_PATH, self)

        self._configurar_tablas()
        self._poblar_tiendas()
        self.fechaEdit.dateChanged.connect(self._cargar_dia)
        self.cmbTienda.currentIndexChanged.connect(self._cargar_dia)
        self.spinEfectivoReal.valueChanged.connect(self._actualizar_diferencia)
        self.btnGuardarInicial.clicked.connect(self._guardar_caja_inicial)
        self.btnCerrarCaja.clicked.connect(self._cerrar_caja)
        self.btnReabrirCaja.clicked.connect(self._reabrir_caja)
        self.btnExportarCierre.clicked.connect(self._exportar_cierre)
        self._cargar_dia()

    def _poblar_tiendas(self) -> None:
        self.cmbTienda.blockSignals(True)
        self.cmbTienda.clear()
        self.cmbTienda.addItem(OPCION_TODAS, None)
        for p in self.module.listar_pymes():
            self.cmbTienda.addItem(p["nombre"], p["id"])
        self.cmbTienda.blockSignals(False)

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
        pyme_id = self.cmbTienda.currentData()
        self.lblFechaLegible.setText(fecha_legible(fecha))

        datos = self.module.resumen_dia(fecha, pyme_id=pyme_id)
        tot = datos["totales"]
        self._datos_dia = datos
        self._pyme_filtrada = pyme_id is not None

        self.lblTotalEfectivo.setText(formatear_clp(tot["efectivo"]))
        self.lblNEfectivo.setText(f"{tot['n_efectivo']} venta{'s' if tot['n_efectivo'] != 1 else ''}")
        self.lblTotalSumUp.setText(formatear_clp(tot["sumup"]))
        self.lblNSumUp.setText(f"{tot['n_sumup']} venta{'s' if tot['n_sumup'] != 1 else ''}")
        self.lblTotalBruto.setText(formatear_clp(tot["bruto"]))
        self.lblNeto.setText(formatear_clp(tot["neto"]))

        self._pintar_resumen(datos, tot)
        self._pintar_ventas(self.tablaEfectivo, datos["ventas_efectivo"], incluir_comision=False)
        self._pintar_ventas(self.tablaSumUp, datos["ventas_sumup"], incluir_comision=True)
        self._sincronizar_cierre(datos)

    def _sincronizar_cierre(self, datos) -> None:
        # blockSignals: cargar valores persistidos sin disparar valueChanged → recalcular antes de tiempo.
        self.spinCajaInicial.blockSignals(True)
        self.spinCajaInicial.setValue(int(datos["caja_inicial"]))
        self.spinCajaInicial.blockSignals(False)

        real = datos["caja_final_real"]
        self.spinEfectivoReal.blockSignals(True)
        self.spinEfectivoReal.setValue(int(real) if real is not None else 0)
        self.spinEfectivoReal.blockSignals(False)

        self.txtComentarioCaja.setPlainText(datos.get("comentario", ""))

        if self._pyme_filtrada:
            self.lblEstadoCierre.setText("Vista filtrada por tienda — el cierre aplica al día completo.")
            self.btnCerrarCaja.setEnabled(False)
            self.btnReabrirCaja.setEnabled(False)
            self.btnGuardarInicial.setEnabled(False)
        elif datos["cerrada"]:
            self.lblEstadoCierre.setText(
                f"Estado: CERRADA — diferencia {formatear_clp(datos['diferencia'])}"
            )
            self.btnCerrarCaja.setText("Re-cerrar caja")
            self.btnCerrarCaja.setEnabled(True)
            self.btnReabrirCaja.setEnabled(True)
            self.btnGuardarInicial.setEnabled(True)
        else:
            self.lblEstadoCierre.setText("Estado: abierta")
            self.btnCerrarCaja.setText("Cerrar caja")
            self.btnCerrarCaja.setEnabled(True)
            self.btnReabrirCaja.setEnabled(False)
            self.btnGuardarInicial.setEnabled(True)

        self._actualizar_diferencia()

    def _actualizar_diferencia(self) -> None:
        esperado = self._datos_dia["caja_final_esperada"]
        diferencia = int(self.spinEfectivoReal.value()) - esperado
        self.lblDiferencia.setText(
            f"Esperado: {formatear_clp(esperado)}  |  Diferencia: {formatear_clp(diferencia)}"
        )
        self.lblDiferencia.setProperty("class", "diff-ok" if diferencia == 0 else "diff-bad")
        # Repolish para que QSS recoja el cambio de la dynamic property.
        self.lblDiferencia.style().unpolish(self.lblDiferencia)
        self.lblDiferencia.style().polish(self.lblDiferencia)

    def _guardar_caja_inicial(self) -> None:
        fecha = self.fechaEdit.date().toPyDate()
        monto = int(self.spinCajaInicial.value())
        try:
            self.module.set_caja_inicial(fecha, monto)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la caja inicial:\n{e}")
            return
        self._cargar_dia()
        QMessageBox.information(self, "Listo", "Caja inicial guardada.")

    def _cerrar_caja(self) -> None:
        fecha = self.fechaEdit.date().toPyDate()
        efectivo_real = int(self.spinEfectivoReal.value())
        comentario = self.txtComentarioCaja.toPlainText().strip() or None

        try:
            resultado = self.module.cerrar_dia(fecha, efectivo_real, comentario)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cerrar la caja:\n{e}")
            return

        self._cargar_dia()
        QMessageBox.information(
            self,
            "Caja cerrada",
            f"Esperado: {formatear_clp(resultado['esperado'])}\n"
            f"Diferencia: {formatear_clp(resultado['diferencia'])}",
        )

    def _reabrir_caja(self) -> None:
        fecha = self.fechaEdit.date().toPyDate()
        confirma = QMessageBox.question(
            self,
            "Reabrir caja",
            f"¿Reabrir la caja del {fecha.isoformat()}? Permitirá registrar nuevas ventas en ese día.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirma != QMessageBox.Yes:
            return
        try:
            self.module.reabrir_dia(fecha)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo reabrir la caja:\n{e}")
            return
        self._cargar_dia()

    def _exportar_cierre(self) -> None:
        fecha = self.fechaEdit.date().toPyDate()
        sugerido = f"cierre_{fecha.isoformat()}.xlsx"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar cierre del día", sugerido, "Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            destino = self.module.exportar_cierre(fecha, ruta)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{exc}")
            return
        QMessageBox.information(self, "Exportado", f"Archivo guardado en:\n{destino}")

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
