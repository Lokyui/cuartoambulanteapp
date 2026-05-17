from __future__ import annotations

import sqlite3
from datetime import date

import pytest

from src.db.dal import DAL


def _setup_caja_cerrada_con_venta(dal: DAL) -> tuple[int, int, int]:
    pyme_id = dal.crear_pyme("Pyme Test")
    venta_id = dal.crear_venta(
        date.today(),
        pyme_id,
        "efectivo",
        iva=190,
        comision_sumup=None,
        total=1000,
        items=[{"producto": "A", "precio": 1000, "cantidad": 1, "subtotal": 1000}],
    )
    items = dal.listar_venta_items(venta_id)
    item_id = items[0]["id"]
    dal.crear_caja_diaria(
        date.today(),
        caja_inicial=0,
        total_efectivo=1000,
        total_sumup=0,
        total_iva=190,
        comision_sumup_total=0,
        caja_final_esperada=1000,
        caja_final_real=1000,
        diferencia=0,
        cerrada=1,
    )
    return pyme_id, venta_id, item_id


def test_trigger_bloquea_update_venta_si_caja_cerrada(dal: DAL) -> None:
    _, venta_id, _ = _setup_caja_cerrada_con_venta(dal)

    with pytest.raises(sqlite3.IntegrityError, match="caja cerrada"):
        dal.actualizar_venta(venta_id, {"total": 9999})


def test_trigger_bloquea_delete_venta_si_caja_cerrada(dal: DAL) -> None:
    _, venta_id, _ = _setup_caja_cerrada_con_venta(dal)

    with pytest.raises(sqlite3.IntegrityError, match="caja cerrada"):
        dal.eliminar_venta(venta_id)


def test_trigger_bloquea_insert_venta_item_si_caja_cerrada(dal: DAL) -> None:
    _, venta_id, _ = _setup_caja_cerrada_con_venta(dal)

    with pytest.raises(sqlite3.IntegrityError, match="caja cerrada"):
        dal.crear_venta_item(venta_id, "B", precio=500, cantidad=1, subtotal=500)


def test_trigger_bloquea_update_venta_item_si_caja_cerrada(dal: DAL) -> None:
    _, _, item_id = _setup_caja_cerrada_con_venta(dal)

    with pytest.raises(sqlite3.IntegrityError, match="caja cerrada"):
        dal.actualizar_venta_item(item_id, {"cantidad": 2, "subtotal": 2000})


def test_trigger_bloquea_delete_venta_item_si_caja_cerrada(dal: DAL) -> None:
    _, _, item_id = _setup_caja_cerrada_con_venta(dal)

    with pytest.raises(sqlite3.IntegrityError, match="caja cerrada"):
        dal.eliminar_venta_item(item_id)


def test_caja_reabierta_permite_editar(dal: DAL) -> None:
    _, venta_id, _ = _setup_caja_cerrada_con_venta(dal)

    dal.actualizar_caja_diaria(date.today(), {"cerrada": 0})

    cambio = dal.actualizar_venta(venta_id, {"comentario": "Editado tras reapertura"})

    assert cambio is True
    venta = dal.obtener_venta(venta_id)
    assert venta is not None
    assert venta["comentario"] == "Editado tras reapertura"
