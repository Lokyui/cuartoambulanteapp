from __future__ import annotations

import sys
from pathlib import Path

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252 por defecto y revienta con → o ⚠)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from PyQt5.QtWidgets import QApplication

from src.db.dal import DAL
from src.ui.views.main_window import MainWindow
from src.modules.ventas_module import VentasModule
from src.modules.retiros_module import RetirosModule
from src.modules.reportes_module import ReportesModule
from src.modules.caja_module import CajaModule

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DB_PATH = SRC / "db" / "cuarto_ambulante.db"
SCHEMA_PATH = SRC / "db" / "schema.sql"
THEME_PATH = SRC / "ui" / "assets" / "theme.qss"
SEEDS = [
    SRC / "db" / "seed.sql",
    SRC / "db" / "seed_ventas.sql",
]


def _necesita_seeds(dal: DAL) -> bool:
    """Decide si hay que cargar seeds revisando si la tabla pymes tiene filas.

    Chequear solo si el archivo .db existe no basta: si un seed falla a
    mitad de carga, el archivo queda creado pero las tablas vacías.
    """
    with dal.conexion() as conn:
        count = conn.execute("SELECT COUNT(*) FROM pymes").fetchone()[0]
    return count == 0


def preparar_base_de_datos(dal: DAL) -> None:
    dal.inicializar(SCHEMA_PATH)

    if _necesita_seeds(dal):
        print("[main] Base de datos vacía — cargando seeds...")
        with dal.conexion() as conn:
            for seed in SEEDS:
                if seed.exists():
                    print(f"  → {seed.name}")
                    conn.executescript(seed.read_text(encoding="utf-8"))
                else:
                    print(f"  ⚠ seed no encontrado: {seed.name}")
        print("[main] Seeds cargados.")
    else:
        print(f"[main] BD existente: {DB_PATH}")


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME_PATH.read_text(encoding="utf-8"))
    dal = DAL(db_path=DB_PATH)
    preparar_base_de_datos(dal)

    ventas_mod = VentasModule(dal)
    retiros_mod = RetirosModule(dal)
    reportes_mod = ReportesModule(dal)
    caja_mod = CajaModule(dal)

    ventana = MainWindow(
        ventas_mod=ventas_mod,
        retiros_mod=retiros_mod,
        reportesModule=reportes_mod,
        caja_module=caja_mod,
    )
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
