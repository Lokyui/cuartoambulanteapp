from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.db.dal import DAL
from src.modules.reportes_module import ReportesModule


@pytest.fixture
def modulo(dal: DAL) -> ReportesModule:
    return ReportesModule(dal)


def _venta(dal: DAL, pyme_id: int, fecha: date, total: int, metodo: str = "efectivo") -> int:
    iva = int(round(total / 1.19 * 0.19))
    comision = int(round(total * 0.0175)) if metodo == "sumup" else None
    return dal.crear_venta(
        fecha, pyme_id, metodo, iva=iva, comision_sumup=comision, total=total
    )


# ── reporte_mensual ──────────────────────────────────────────────────────────

def test_reporte_mensual_agrega_totales_generales(dal: DAL, modulo: ReportesModule) -> None:
    a = dal.crear_pyme("PymeA")
    b = dal.crear_pyme("PymeB")
    _venta(dal, a, date(2026, 5, 1), 10000)
    _venta(dal, b, date(2026, 5, 10), 20000, "sumup")

    reporte = modulo.reporte_mensual(2026, 5)

    assert len(reporte["filas"]) == 2
    assert reporte["totales"]["total_bruto"] == 30000
    assert reporte["totales"]["n_ventas"] == 2


def test_reporte_mensual_solo_incluye_pymes_con_ventas(dal: DAL, modulo: ReportesModule) -> None:
    a = dal.crear_pyme("Con ventas")
    dal.crear_pyme("Sin ventas")
    _venta(dal, a, date(2026, 5, 1), 5000)

    reporte = modulo.reporte_mensual(2026, 5)

    assert len(reporte["filas"]) == 1
    assert reporte["filas"][0]["nombre"] == "Con ventas"


def test_reporte_mensual_no_mezcla_otros_meses(dal: DAL, modulo: ReportesModule) -> None:
    a = dal.crear_pyme("PymeA")
    _venta(dal, a, date(2026, 4, 1), 5000)
    _venta(dal, a, date(2026, 5, 1), 8000)
    _venta(dal, a, date(2026, 6, 1), 3000)

    reporte = modulo.reporte_mensual(2026, 5)

    assert reporte["totales"]["total_bruto"] == 8000


def test_reporte_mensual_sin_datos_devuelve_filas_vacias(modulo: ReportesModule) -> None:
    reporte = modulo.reporte_mensual(2026, 5)

    assert reporte["filas"] == []
    assert reporte["totales"]["total_bruto"] == 0


# ── detalle_pyme ─────────────────────────────────────────────────────────────

def test_detalle_pyme_filtra_por_rango_de_fechas(dal: DAL, modulo: ReportesModule) -> None:
    pyme_id = dal.crear_pyme("Pyme")
    _venta(dal, pyme_id, date(2026, 5, 1), 1000)
    _venta(dal, pyme_id, date(2026, 5, 15), 2000)
    _venta(dal, pyme_id, date(2026, 6, 1), 3000)

    data = modulo.detalle_pyme(pyme_id, "2026-05-01", "2026-05-31")

    assert len(data["detalle"]) == 2
    assert data["resumen"]["n_ventas"] == 2


def test_detalle_pyme_sin_ventas_devuelve_ceros(modulo: ReportesModule, dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme")

    data = modulo.detalle_pyme(pyme_id, "2026-01-01", "2026-12-31")

    assert data["detalle"] == []
    assert data["resumen"]["n_ventas"] == 0


# ── detalle_dia ──────────────────────────────────────────────────────────────

def test_detalle_dia_resuelve_nombre_de_pyme(dal: DAL, modulo: ReportesModule) -> None:
    pyme_id = dal.crear_pyme("BADTRIP")
    _venta(dal, pyme_id, date.today(), 1000)

    ventas = modulo.detalle_dia(date.today())

    assert len(ventas) == 1
    assert ventas[0]["pyme_nombre"] == "BADTRIP"


def test_detalle_dia_filtra_por_pyme(dal: DAL, modulo: ReportesModule) -> None:
    a = dal.crear_pyme("A")
    b = dal.crear_pyme("B")
    _venta(dal, a, date.today(), 1000)
    _venta(dal, b, date.today(), 2000)

    solo_a = modulo.detalle_dia(date.today(), pyme_id=a)

    assert len(solo_a) == 1
    assert solo_a[0]["pyme_nombre"] == "A"


# ── exportar_* ───────────────────────────────────────────────────────────────

def test_exportar_reporte_mensual_genera_xlsx(tmp_path: Path, dal: DAL, modulo: ReportesModule) -> None:
    pyme_id = dal.crear_pyme("Pyme")
    _venta(dal, pyme_id, date(2026, 5, 1), 5000)
    destino = tmp_path / "rep.xlsx"

    resultado = modulo.exportar_reporte_mensual(2026, 5, destino)

    assert resultado == destino
    assert destino.exists() and destino.stat().st_size > 0


def test_exportar_detalle_pyme_genera_xlsx(tmp_path: Path, dal: DAL, modulo: ReportesModule) -> None:
    pyme_id = dal.crear_pyme("Pyme")
    _venta(dal, pyme_id, date(2026, 5, 1), 5000)
    destino = tmp_path / "pyme.xlsx"

    resultado = modulo.exportar_detalle_pyme(pyme_id, "2026-05-01", "2026-05-31", destino)

    assert resultado == destino
    assert destino.exists() and destino.stat().st_size > 0
