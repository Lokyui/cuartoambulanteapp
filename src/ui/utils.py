from datetime import date

from PyQt5.QtCore import QLocale, QPropertyAnimation, QTimer, Qt, pyqtProperty
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import (
    QAbstractButton,
    QAbstractSpinBox,
    QDateEdit,
    QMessageBox,
    QSpinBox,
    QWidget,
)

LOCALE_CLP = QLocale(QLocale.Spanish, QLocale.Chile)

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def formatear_clp(valor) -> str:
    if valor is None:
        return "$0"
    return f"${valor:,.0f}".replace(",", ".")


def fecha_legible(fecha: date) -> str:
    return f"{DIAS_ES[fecha.weekday()]} {fecha.day} de {MESES_ES[fecha.month]}, {fecha.year}"


def pregunta_si_no(parent: QWidget | None, titulo: str, mensaje: str) -> bool:
    """Diálogo de confirmación con botones 'Sí' / 'No' (no 'Yes/No' por defecto de Qt)."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(titulo)
    box.setText(mensaje)
    btn_si = box.addButton("Sí", QMessageBox.YesRole)
    btn_no = box.addButton("No", QMessageBox.NoRole)
    box.setDefaultButton(btn_no)
    box.exec_()
    return box.clickedButton() is btn_si


class FechaEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDate(date.today())
        self.setDisplayFormat("dd/MM/yyyy")
        self.setMinimumWidth(130)
        self.setMaximumWidth(170)
        self.setAlignment(Qt.AlignCenter)


class _SpinBoxSeleccionable(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Sin flechas: dejan el campo más limpio y consistente con FechaEdit.
        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class MontoSpinBox(_SpinBoxSeleccionable):
    """SpinBox para montos en CLP: arranca vacío y se reemplaza al tipear."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLocale(LOCALE_CLP)
        self.setMinimum(0)
        self.setMaximum(9_999_999)
        self.setPrefix("$ ")
        self.setGroupSeparatorShown(True)


class CantidadSpinBox(_SpinBoxSeleccionable):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(1)
        self.setMaximum(9999)
        self.setValue(1)


class ToggleSwitch(QAbstractButton):
    """Interruptor ON/OFF estilo iOS. Emite toggled(bool) como un QCheckBox."""

    TRACK_OFF = QColor("#D6EFC8")
    TRACK_ON = QColor("#5BAA3D")
    THUMB_OFF = QColor("#5BAA3D")
    THUMB_ON = QColor("#FFFFFF")

    def __init__(self, parent=None, checked: bool = False):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(46, 24)
        self.setCursor(Qt.PointingHandCursor)
        self._margen = 3
        self._offset = self._x_final(checked)
        self.setChecked(checked)
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(120)
        self.toggled.connect(self._animar)

    def _x_final(self, checked: bool) -> int:
        return self.width() - self.height() + self._margen if checked else self._margen

    @pyqtProperty(int)
    def offset(self) -> int:
        return self._offset

    @offset.setter
    def offset(self, value: int) -> None:
        self._offset = value
        self.update()

    def _animar(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(self._x_final(checked))
        self._anim.start()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        radio = self.height() / 2
        p.setBrush(self.TRACK_ON if self.isChecked() else self.TRACK_OFF)
        p.drawRoundedRect(0, 0, self.width(), self.height(), radio, radio)

        p.setBrush(self.THUMB_ON if self.isChecked() else self.THUMB_OFF)
        diam = self.height() - 2 * self._margen
        p.drawEllipse(self._offset, self._margen, diam, diam)
        p.end()
