from __future__ import annotations

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QFrame,
    QVBoxLayout,
    QLabel
)
from datetime import date
from ui.views.registro_retiro import RegistroRetiroDialog
from src.modules.retiros_module import RetirosModule

UI_PATH = "src/ui/views/retiros.ui"

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

class RetirosView(QWidget):
    def __init__(self, module: RetirosModule):
        super().__init__()
        self.module = module

        try:
            #Cargar el UI
            uic.loadUi("src/ui/views/retiros.ui", self)
            hoy = date.today()
            dia_semana = DIAS_ES[hoy.weekday()]
            mes = MESES_ES[hoy.month]
            fecha_texto = f"{dia_semana} {hoy.day} de {mes}, {hoy.year}"

            if hasattr(self, "plainTextEdit_10"):
                self.plainTextEdit_10.setPlainText(fecha_texto)

            if hasattr(self, 'verticalLayout'):
                self.layout_scroll = self.verticalLayout
            else:
                # Si por alguna razón cambió el nombre en el .ui, esto evita el crash
                print("Error: No se encontró 'verticalLayout' en retiros.ui")
                self.layout_scroll = QVBoxLayout() 

            #Conectar señales
            self.pushButton.clicked.connect(
                lambda: print("CLICK BOTON NUEVO PAQUETE")
            )
            self.pushButton.clicked.connect(self.abrir_formulario_nuevo)

            #Carga inicial
            self.actualizar_vista()
            
        except Exception as e:
            print(f"Error crítico al inicializar RetirosView: {e}")

    def abrir_formulario_nuevo(self):
        dialogo = RegistroRetiroDialog(self.module, self.module.dal, self)
        if dialogo.exec_():
            self.actualizar_vista()
            QMessageBox.information(self, "Éxito", "El paquete ha sido registrado correctamente.")

    def actualizar_vista(self):
        try:
            # 1. Obtener datos desde el módulo (usando el DAL interno)
            paquetes = self.module.dal.listar_paquetes()
            print("PAQUETES:", paquetes)

            # 2. Limpiar layout actual
            while self.layout_scroll.count():
                item = self.layout_scroll.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            if not paquetes:
                return

            # 3. Crear cards
            for paquete in paquetes:
                card = self._crear_card_paquete(paquete)
                self.layout_scroll.addWidget(card)
        except Exception as e:
            print(f"Error al actualizar la vista de retiros: {e}")

    def _crear_card_paquete(self, paquete):
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout

        frame = QFrame()
        frame.setObjectName("framePedido")
        frame.setMinimumHeight(140)
        frame.setStyleSheet("""
            QFrame#framePedido {
                background-color: #D9D9D9;
                border: 1px solid black;
                border-radius: 8px;
            }

            QLabel {
                border: none;
                background: transparent;
                color: black;
            }
        """)

        layout_principal = QVBoxLayout(frame)
        layout_principal.setContentsMargins(15, 12, 15, 12)
        layout_principal.setSpacing(10)

        # -------------------------
        # Fila superior
        # -------------------------
        fila_superior = QHBoxLayout()

        nombre = QLabel(paquete["nombre_destinatario"])
        nombre.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        ubicacion = QLabel(f"Ubicación {paquete['ubicacion_bodega']}")
        ubicacion.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
        """)

        fila_superior.addWidget(nombre)
        fila_superior.addStretch()
        fila_superior.addWidget(ubicacion)

        # -------------------------
        # Estado pago
        # -------------------------
        pago = QLabel(
            "Pagado" if paquete["estado_pago"] == "pagado" else "Por pagar"
        )
        pago.setStyleSheet("font-size: 14px;")

        # -------------------------
        # Fila inferior
        # -------------------------
        fila_inferior = QHBoxLayout()

        info = QLabel(
            f"Pyme: {paquete['nombre_pyme']} | Retira: {paquete['nombre_destinatario']}"
        )
        info.setStyleSheet("font-size: 14px;")

        fila_inferior.addWidget(info)
        fila_inferior.addStretch()

        # Contenedor botones derecha
        layout_botones = QVBoxLayout()
        layout_botones.setSpacing(6)

        btn_editar = QPushButton("Editar pedido")
        btn_editar.setStyleSheet("""
            background-color: #F6F6F6;
            border: 1px solid black;
            border-radius: 4px;
            padding: 6px 10px;
        """)

        btn_entregar = QPushButton()

        estado = paquete.get("estado", "activo")

        if estado == "entregado":
            btn_entregar.setText("Entregado")
            btn_entregar.setEnabled(False)
            btn_entregar.setStyleSheet("""
                background-color: #D9F5DD;
                border: 1px solid #5A9E63;
                border-radius: 4px;
                padding: 6px 10px;
            """)
        else:
            btn_entregar.setText("Marcar Entregado")
            btn_entregar.setStyleSheet("""
                background-color: #F6F6F6;
                border: 1px solid black;
                border-radius: 4px;
                padding: 6px 10px;
            """)
            btn_entregar.clicked.connect(
                lambda _, paquete_id=paquete["id"]: self.marcar_entregado(paquete_id)
            )

        layout_botones.addWidget(btn_editar)
        layout_botones.addWidget(btn_entregar)

        fila_inferior.addLayout(layout_botones)

        # -------------------------
        # Agregar todo
        # -------------------------
        layout_principal.addLayout(fila_superior)
        layout_principal.addWidget(pago)
        layout_principal.addLayout(fila_inferior)

        return frame

    def marcar_entregado(self, paquete_id):
        try:
            self.module.dal.actualizar_paquete(
                paquete_id,
                estado="entregado"
            )
            self.actualizar_vista()
            QMessageBox.information(
                self,
                "Éxito",
                "Paquete marcado como entregado."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo actualizar el paquete:\n{e}"
            )