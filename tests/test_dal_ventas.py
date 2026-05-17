from __future__ import annotations

from datetime import date

import pytest

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


def test_bloquea_venta_si_caja_cerrada(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    dal.crear_caja_diaria(
        date.today(),
        caja_inicial=0,
        total_efectivo=0,
        total_sumup=0,
        total_iva=0,
        comision_sumup_total=0,
        caja_final_esperada=0,
        caja_final_real=0,
        diferencia=0,
        cerrada=1,
    )

    with pytest.raises(Exception, match="caja cerrada"):
        dal.crear_venta(
            date.today(),
            pyme_id,
            "efectivo",
            iva=190,
            comision_sumup=None,
            total=1000,
            items=[{"producto": "A", "precio": 1000, "cantidad": 1, "subtotal": 1000}],
        )
