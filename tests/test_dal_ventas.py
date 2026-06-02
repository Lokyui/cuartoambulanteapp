from __future__ import annotations

from datetime import date

from src.db.dal import DAL


def test_crear_venta_con_items(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    venta_id = dal.crear_venta(
        date.today(),
        pyme_id,
        "efectivo",
        iva=190,
        comision_sumup=None,
        total=1000,
        items=[
            {"producto": "A", "precio": 300, "cantidad": 2, "subtotal": 600},
            {"producto": "B", "precio": 200, "cantidad": 2, "subtotal": 400},
        ],
        comentario="Venta con items",
    )

    venta = dal.obtener_venta(venta_id)
    items = dal.listar_venta_items(venta_id)

    assert venta is not None
    assert venta["total"] == 1000
    assert len(items) == 2
    assert items[0]["producto"] == "A"


def test_crear_venta_sin_items_usa_cabecera_generica(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    venta_id = dal.crear_venta(
        date.today(), pyme_id, "efectivo", iva=190, comision_sumup=None, total=1000
    )

    venta = dal.obtener_venta(venta_id)
    assert venta is not None
    assert venta["articulo"] == "Venta general"
    assert venta["cantidad"] == 1


def test_crear_venta_multi_item_arma_cabecera_con_extras(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    venta_id = dal.crear_venta(
        date.today(),
        pyme_id,
        "efectivo",
        iva=190,
        comision_sumup=None,
        total=900,
        items=[
            {"producto": "Camiseta", "precio": 500, "cantidad": 1, "subtotal": 500},
            {"producto": "Stickers", "precio": 200, "cantidad": 2, "subtotal": 400},
        ],
    )

    venta = dal.obtener_venta(venta_id)
    assert venta is not None
    assert venta["articulo"] == "Camiseta (+1)"
    assert venta["cantidad"] == 3


def test_listar_ventas_filtra_por_fecha_y_pyme(dal: DAL) -> None:
    pyme_a = dal.crear_pyme("PymeA")
    pyme_b = dal.crear_pyme("PymeB")
    hoy = date.today()

    dal.crear_venta(hoy, pyme_a, "efectivo", iva=190, comision_sumup=None, total=1000)
    dal.crear_venta(hoy, pyme_b, "efectivo", iva=190, comision_sumup=None, total=2000)
    dal.crear_venta(date(2024, 1, 1), pyme_a, "efectivo", iva=190, comision_sumup=None, total=500)

    del_dia = dal.listar_ventas(fecha=hoy)
    de_pyme_a = dal.listar_ventas(pyme_id=pyme_a)
    de_pyme_a_hoy = dal.listar_ventas(fecha=hoy, pyme_id=pyme_a)

    assert len(del_dia) == 2
    assert len(de_pyme_a) == 2
    assert len(de_pyme_a_hoy) == 1


def test_actualizar_venta_solo_columnas_permitidas(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    venta_id = dal.crear_venta(
        date.today(), pyme_id, "efectivo", iva=190, comision_sumup=None, total=1000
    )

    cambio = dal.actualizar_venta(venta_id, {"total": 2000, "campo_inventado": "X"})

    venta = dal.obtener_venta(venta_id)
    assert cambio is True
    assert venta is not None
    assert venta["total"] == 2000


def test_eliminar_venta(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    venta_id = dal.crear_venta(
        date.today(), pyme_id, "efectivo", iva=190, comision_sumup=None, total=1000
    )

    assert dal.eliminar_venta(venta_id) is True
    assert dal.obtener_venta(venta_id) is None
