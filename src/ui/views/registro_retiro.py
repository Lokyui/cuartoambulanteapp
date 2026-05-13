from __future__ import annotations

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from db.dal import DAL
from src.modules.retiros_module import RetirosModule

UI_PATH = "src/ui/views/registro_retiro.ui"

class RegistroRetiroDialog(QDialog):
    def __init__(self, module: RetirosModule, dal: DAL, parent=None):
        super().__init__(parent)
        self.module = module
        self.dal = dal
        uic.loadUi(UI_PATH, self)
        
        # Poblar ComboBoxes con datos reales de la BD
        self._cargar_datos_iniciales()
        
        # Conexiones de botones según tu .ui
        self.pushButton_5.clicked.connect(self.guardar_paquete) # Botón "Guardar venta"
        self.pushButton_6.clicked.connect(self.reject)         # Botón "Cancelar"

    def _cargar_datos_iniciales(self):
        """Carga PYMEs y Personal desde el DAL."""
        # Cargar PYMEs en comboBox
        pymes = self.dal.listar_pymes(solo_activas=True)
        self.comboBox.clear()
        for p in pymes:
            self.comboBox.addItem(p["nombre"], p["id"])
            
        # Cargar Personal en comboBox_3 (Recibido por)
        personal = self.dal.listar_personal(solo_activos=True)
        self.comboBox_3.clear()
        for pers in personal:
            self.comboBox_3.addItem(pers["nombre_display"], pers["id"])

    def guardar_paquete(self):
        """Extrae datos y llama a crear_paquete en el DAL."""
        # 1. Extraer valores del formulario
        pyme_id = self.comboBox.currentData()
        fecha_llegada = self.dateEdit.date().toPyDate()
        destinatario = self.lineEdit.text().strip()
        ubicacion = self.comboBox_2.currentText() # Ubicación en bodega (A1, A2...)
        recibido_por_id = self.comboBox_3.currentData()
        descripcion = self.textEdit_3.toPlainText().strip()
        
        # Determinar estado de pago desde RadioButtons
        estado_pago = "pagado" if self.radioButton.isChecked() else "por_cobrar"
        
        # 2. Validación básica
        if not destinatario:
            QMessageBox.warning(self, "Validación", "El nombre del destinatario es obligatorio.")
            return

        # 3. Guardar en BD usando crear_paquete del dal.py
        try:
            self.dal.crear_paquete(
                fecha_llegada=fecha_llegada,
                pyme_remitente_id=pyme_id,
                nombre_destinatario=destinatario,
                ubicacion_bodega=ubicacion,
                estado_pago=estado_pago,
                recibido_por=recibido_por_id,
                descripcion=descripcion,
                estado="activo" # Estado inicial por defecto
            )
            self.accept() # Cierra el diálogo con éxito
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el paquete:\n{e}")