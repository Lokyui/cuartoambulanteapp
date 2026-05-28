from datetime import date

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QAbstractSpinBox, QDateEdit, QSpinBox

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
