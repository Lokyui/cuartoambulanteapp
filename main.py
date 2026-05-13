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
from ui.views.resumen_caja import ResumenCajaView
from ui.views.reporte_pyme import ReportePymeView
from modules.ventas_module import VentasModule
from modules.retiros_module import RetirosModule
from modules.reportes_module import ReportesModule
from modules.caja_module import CajaModule

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
    dal = DAL(db_path=DB_PATH)
    preparar_base_de_datos(dal)

    # 1. Instanciar los módulos de lógica
    ventas_mod = VentasModule(dal)
    retiros_mod = RetirosModule(dal)
    reportes_mod = ReportesModule(dal)
    caja_mod = CajaModule(dal)

    # 2. Pasar los módulos a las vistas (en lugar del dal)
    # Ejemplo con MainWindow (puedes pasarle todos o solo los necesarios)
    ventana = MainWindow(
        ventas_mod=ventas_mod,
        retiros_mod=retiros_mod,
        reportesModule=reportes_mod,
        caja_module=caja_mod
    )
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    
