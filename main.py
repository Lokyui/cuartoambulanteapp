from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# ── Ajuste de sys.path para que los imports funcionen desde la raíz ──────────
ROOT = Path(__file__).resolve().parent
SRC  = ROOT / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

from db.dal import DAL  # noqa: E402  (import después del path-hack)
from ui.views.main_window import MainWindow
from ui.views.ventas import VentasView
from ui.views.reporte_mensual import ReporteMensualView

# ── Rutas ────────────────────────────────────────────────────────────────────
DB_PATH     = SRC / "db" / "cuarto_ambulante.db"
SCHEMA_PATH = SRC / "db" / "schema.sql"
SEEDS = [
    SRC / "db" / "seed.sql",
    SRC / "db" / "seed_ventas.sql",
]


def preparar_base_de_datos(dal: DAL) -> None:
    db_nueva = not DB_PATH.exists() or DB_PATH.stat().st_size == 0

    dal.inicializar(SCHEMA_PATH)

    if db_nueva:
        print("[main] Base de datos nueva — cargando seeds...")
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

    # Crear e inicializar el DAL apuntando a la BD de src/db/
    dal = DAL(db_path=DB_PATH)
    preparar_base_de_datos(dal)

    ventana = MainWindow(dal)
    ventana.setWindowTitle("Dashboard — Cuarto Ambulante [PRUEBA]")
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
