from __future__ import annotations

from datetime import date
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QFrame,
    QVBoxLayout,
    QLabel,
)

from src.ui.views.registro_retiro import RegistroRetiroDialog
from src.modules.retiros_module import RetirosModule
from src.ui.utils import fecha_legible

UI_PATH = str(Path(__file__).parent / "retiros.ui")


class RetirosView(QWidget):
    def __init__(self, module: RetirosModule):
        super().__init__()
        self.module = module
        self._filtro = "todos"

        uic.loadUi(UI_PATH, self)
        self.lblFecha.setText(fecha_legible(date.today()))

        self.layout_scroll = self.verticalLayout
        self.pushButton.clicked.connect(self.abrir_formulario_nuevo)
        self.btnFiltroTodos.clicked.connect(lambda: self._aplicar_filtro("todos"))
        self.btnFiltroPorCobrar.clicked.connect(lambda: self._aplicar_filtro("por_cobrar"))
        self.txtBuscar.textChanged.connect(self.actualizar_vista)
        self.actualizar_vista()

    def _aplicar_filtro(self, filtro: str) -> None:
        self._filtro = filtro
        self.actualizar_vista()

    def abrir_formulario_nuevo(self):
        dialogo = RegistroRetiroDialog(self.module, self)
        if dialogo.exec_():
            self.actualizar_vista()
            QMessageBox.information(self, "Éxito", "El paquete ha sido registrado correctamente.")

    def abrir_formulario_edicion(self, paquete_id: int):
        paquete = self.module.obtener_paquete(paquete_id)
        if not paquete:
            QMessageBox.warning(self, "No encontrado", "El paquete ya no existe.")
            self.actualizar_vista()
            return
        dialogo = RegistroRetiroDialog(self.module, self, paquete=paquete)
        if dialogo.exec_():
            self.actualizar_vista()
            QMessageBox.information(self, "Éxito", "Paquete actualizado correctamente.")

    def actualizar_vista(self):
        # HU3: solo paquetes activos en esta vista; los entregados van al historial.
        texto = self.txtBuscar.text().strip()
        if texto:
            paquetes = self.module.buscar_paquetes(
                texto,
                solo_activos=True,
                solo_por_cobrar=(self._filtro == "por_cobrar"),
            )
        elif self._filtro == "por_cobrar":
            paquetes = self.module.listar_por_cobrar()
        else:
            paquetes = self.module.listar_pendientes()

        while self.layout_scroll.count():
            item = self.layout_scroll.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for paquete in paquetes:
            self.layout_scroll.addWidget(self._crear_card_paquete(paquete))

    def _crear_card_paquete(self, paquete):
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout

        frame = QFrame()
        frame.setProperty("class", "frame-paquete")
        frame.setMinimumHeight(140)

        layout_principal = QVBoxLayout(frame)
        layout_principal.setContentsMargins(15, 12, 15, 12)
        layout_principal.setSpacing(10)

        fila_superior = QHBoxLayout()
        nombre = QLabel(paquete["nombre_destinatario"])
        nombre.setProperty("class", "paquete-nombre")
        ubicacion = QLabel(f"Ubicación {paquete['ubicacion_bodega']}")
        ubicacion.setProperty("class", "paquete-ubicacion")
        fila_superior.addWidget(nombre)
        fila_superior.addStretch()
        fila_superior.addWidget(ubicacion)

        pago = QLabel("Pagado" if paquete["estado_pago"] == "pagado" else "Por pagar")
        pago.setProperty("class", "paquete-texto")

        fila_inferior = QHBoxLayout()
        info = QLabel(f"Pyme: {paquete['nombre_pyme']} | Retira: {paquete['nombre_destinatario']}")
        info.setProperty("class", "paquete-texto")
        fila_inferior.addWidget(info)
        fila_inferior.addStretch()

        layout_botones = QVBoxLayout()
        layout_botones.setSpacing(6)

        btn_editar = QPushButton("Editar pedido")
        btn_editar.setProperty("class", "btn-secundario")
        btn_editar.clicked.connect(
            lambda _, pid=paquete["id"]: self.abrir_formulario_edicion(pid)
        )

        btn_entregar = QPushButton("Marcar Entregado")
        btn_entregar.setProperty("class", "btn-secundario")
        btn_entregar.clicked.connect(
            lambda _, paquete_id=paquete["id"]: self.marcar_entregado(paquete_id)
        )

        layout_botones.addWidget(btn_editar)
        layout_botones.addWidget(btn_entregar)
        fila_inferior.addLayout(layout_botones)

        layout_principal.addLayout(fila_superior)
        layout_principal.addWidget(pago)
        layout_principal.addLayout(fila_inferior)

        return frame

    def marcar_entregado(self, paquete_id):
        paquete = self.module.obtener_paquete(paquete_id)
        nombre = paquete["nombre_destinatario"] if paquete else "este paquete"
        confirma = QMessageBox.question(
            self,
            "Confirmar entrega",
            f"¿Marcar como entregado el paquete de {nombre}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirma != QMessageBox.Yes:
            return
        try:
            self.module.marcar_entregado(paquete_id)
            self.actualizar_vista()
            QMessageBox.information(self, "Éxito", "Paquete marcado como entregado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el paquete:\n{e}")
