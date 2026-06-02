from __future__ import annotations

from datetime import date

from src.db.dal import DAL


def test_crear_y_obtener_caja_diaria(dal: DAL) -> None:
    fecha = date.today()
    caja_id = dal.crear_caja_diaria(
        fecha,
        caja_inicial=50000,
        total_efectivo=10000,
        total_sumup=5000,
        total_iva=2390,
        comision_sumup_total=88,
        caja_final_esperada=60000,
        caja_final_real=60000,
        diferencia=0,
        cerrada=1,
    )

    caja = dal.obtener_caja_diaria(fecha)

    assert caja_id > 0
    assert caja is not None
    assert caja["caja_inicial"] == 50000
    assert caja["cerrada"] == 1


def test_obtener_caja_inexistente_devuelve_none(dal: DAL) -> None:
    assert dal.obtener_caja_diaria(date.today()) is None


def test_actualizar_caja_diaria(dal: DAL) -> None:
    fecha = date.today()
    dal.crear_caja_diaria(fecha, caja_inicial=10000)

    cambio = dal.actualizar_caja_diaria(fecha, {"caja_inicial": 25000, "cerrada": 1})

    caja = dal.obtener_caja_diaria(fecha)
    assert cambio is True
    assert caja is not None
    assert caja["caja_inicial"] == 25000
    assert caja["cerrada"] == 1


def test_actualizar_caja_ignora_columnas_no_permitidas(dal: DAL) -> None:
    fecha = date.today()
    dal.crear_caja_diaria(fecha, caja_inicial=10000)

    cambio = dal.actualizar_caja_diaria(fecha, {"caja_inicial": 20000, "campo_falso": 99})

    assert cambio is True
    assert dal.obtener_caja_diaria(fecha)["caja_inicial"] == 20000


def test_listar_cajas_ordena_por_fecha_desc(dal: DAL) -> None:
    dal.crear_caja_diaria(date(2026, 1, 1))
    dal.crear_caja_diaria(date(2026, 3, 1))
    dal.crear_caja_diaria(date(2026, 2, 1))

    cajas = dal.listar_cajas_diarias()

    assert [c["fecha"] for c in cajas] == ["2026-03-01", "2026-02-01", "2026-01-01"]


def test_comentario_persiste(dal: DAL) -> None:
    fecha = date.today()
    dal.crear_caja_diaria(fecha, comentario="cierre con descuadre menor")

    caja = dal.obtener_caja_diaria(fecha)
    assert caja["comentario"] == "cierre con descuadre menor"
