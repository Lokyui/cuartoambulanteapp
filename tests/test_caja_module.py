from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.db.dal import DAL
from src.modules.caja_module import CajaModule


@pytest.fixture
def modulo(dal: DAL) -> CajaModule:
    return CajaModule(dal)


def _venta(dal: DAL, pyme_id: int, total: int, metodo: str = "efectivo") -> int:
    iva = int(round(total / 1.19 * 0.19))
    comision = int(round(total * 0.0175)) if metodo == "sumup" else None
    return dal.crear_venta(
        date.today(), pyme_id, metodo, iva=iva, comision_sumup=comision, total=total
    )


# ── resumen_dia ──────────────────────────────────────────────────────────────

def test_resumen_dia_separa_metodos_y_calcula_neto(dal: DAL, modulo: CajaModule) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    _venta(dal, pyme_id, 10000, "efectivo")
    _venta(dal, pyme_id, 20000, "sumup")

    resumen = modulo.resumen_dia(date.today())
    tot = resumen["totales"]

    assert tot["n_efectivo"] == 1
    assert tot["n_sumup"] == 1
    assert tot["efectivo"] == 10000
    assert tot["sumup"] == 20000
    assert tot["bruto"] == 30000
    assert tot["neto"] == tot["bruto"] - tot["iva"] - tot["comision_sumup"]


def test_resumen_dia_sin_ventas_devuelve_ceros(modulo: CajaModule) -> None:
    resumen = modulo.resumen_dia(date.today())

    assert resumen["totales"]["n_ventas"] == 0
    assert resumen["totales"]["bruto"] == 0
    assert resumen["caja_inicial"] == 0
    assert resumen["cerrada"] is False


def test_resumen_dia_incluye_caja_persistida(dal: DAL, modulo: CajaModule) -> None:
    fecha = date.today()
    dal.crear_caja_diaria(fecha, caja_inicial=15000, caja_final_real=18000, diferencia=-200, cerrada=1)

    resumen = modulo.resumen_dia(fecha)

    assert resumen["caja_inicial"] == 15000
    assert resumen["caja_final_real"] == 18000
    assert resumen["diferencia"] == -200
    assert resumen["cerrada"] is True


def test_resumen_dia_filtrado_por_pyme(dal: DAL, modulo: CajaModule) -> None:
    a = dal.crear_pyme("A")
    b = dal.crear_pyme("B")
    _venta(dal, a, 5000)
    _venta(dal, b, 9000)

    sin_filtro = modulo.resumen_dia(date.today())
    filtrado = modulo.resumen_dia(date.today(), pyme_id=a)

    assert sin_filtro["totales"]["bruto"] == 14000
    assert filtrado["totales"]["bruto"] == 5000


# ── set_caja_inicial ─────────────────────────────────────────────────────────

def test_set_caja_inicial_crea_si_no_existe(dal: DAL, modulo: CajaModule) -> None:
    fecha = date.today()

    modulo.set_caja_inicial(fecha, 50000)

    assert dal.obtener_caja_diaria(fecha)["caja_inicial"] == 50000


def test_set_caja_inicial_actualiza_si_existe(dal: DAL, modulo: CajaModule) -> None:
    fecha = date.today()
    dal.crear_caja_diaria(fecha, caja_inicial=10000)

    modulo.set_caja_inicial(fecha, 75000)

    assert dal.obtener_caja_diaria(fecha)["caja_inicial"] == 75000


def test_set_caja_inicial_rechaza_negativo(modulo: CajaModule) -> None:
    with pytest.raises(ValueError):
        modulo.set_caja_inicial(date.today(), -100)


# ── cerrar_dia ───────────────────────────────────────────────────────────────

def test_cerrar_dia_persiste_totales_y_diferencia(dal: DAL, modulo: CajaModule) -> None:
    fecha = date.today()
    pyme_id = dal.crear_pyme("Pyme Test")
    _venta(dal, pyme_id, 10000)
    modulo.set_caja_inicial(fecha, 5000)

    resultado = modulo.cerrar_dia(fecha, efectivo_real=15500, comentario="cuadrada")

    caja = dal.obtener_caja_diaria(fecha)
    assert resultado["esperado"] == 15000
    assert resultado["diferencia"] == 500
    assert caja["cerrada"] == 1
    assert caja["caja_final_real"] == 15500
    assert caja["diferencia"] == 500
    assert caja["comentario"] == "cuadrada"


def test_cerrar_dia_es_idempotente(dal: DAL, modulo: CajaModule) -> None:
    fecha = date.today()
    modulo.cerrar_dia(fecha, efectivo_real=0)
    modulo.cerrar_dia(fecha, efectivo_real=200, comentario="ajuste")

    caja = dal.obtener_caja_diaria(fecha)
    assert caja["caja_final_real"] == 200
    assert caja["comentario"] == "ajuste"


def test_cerrar_dia_rechaza_efectivo_negativo(modulo: CajaModule) -> None:
    with pytest.raises(ValueError):
        modulo.cerrar_dia(date.today(), efectivo_real=-100)


def test_cerrar_dia_rechaza_comentario_muy_largo(modulo: CajaModule) -> None:
    with pytest.raises(ValueError):
        modulo.cerrar_dia(date.today(), efectivo_real=0, comentario="x" * 201)


# ── reabrir_dia ──────────────────────────────────────────────────────────────

def test_reabrir_dia_dejacaja_marcada_como_abierta(dal: DAL, modulo: CajaModule) -> None:
    fecha = date.today()
    modulo.cerrar_dia(fecha, efectivo_real=0)

    cambio = modulo.reabrir_dia(fecha)

    assert cambio is True
    assert dal.obtener_caja_diaria(fecha)["cerrada"] == 0


def test_reabrir_dia_sin_cierre_previo_no_hace_nada(modulo: CajaModule) -> None:
    assert modulo.reabrir_dia(date.today()) is False


# ── exportar_cierre ──────────────────────────────────────────────────────────

def test_exportar_cierre_genera_xlsx(tmp_path: Path, dal: DAL, modulo: CajaModule) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    _venta(dal, pyme_id, 5000)
    destino = tmp_path / "cierre.xlsx"

    resultado = modulo.exportar_cierre(date.today(), destino)

    assert resultado == destino
    assert destino.exists()
    assert destino.stat().st_size > 0


# ── listar_pymes ─────────────────────────────────────────────────────────────

def test_listar_pymes_solo_devuelve_activas(dal: DAL, modulo: CajaModule) -> None:
    dal.crear_pyme("Activa", activa=1)
    dal.crear_pyme("Inactiva", activa=0)

    pymes = modulo.listar_pymes()

    assert len(pymes) == 1
    assert pymes[0]["nombre"] == "Activa"
