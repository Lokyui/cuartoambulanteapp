from __future__ import annotations

import sqlite3
from datetime import date

import pytest

from db.dal import DAL


def test_check_metodo_invalido(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta(
            date.today(),
            pyme_id,
            "tarjeta",
            iva=190,
            comision_sumup=None,
            total=1000,
        )


def test_check_efectivo_no_admite_comision(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta(
            date.today(),
            pyme_id,
            "efectivo",
            iva=190,
            comision_sumup=18,
            total=1000,
        )


def test_check_sumup_requiere_comision(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta(
            date.today(),
            pyme_id,
            "sumup",
            iva=190,
            comision_sumup=None,
            total=1000,
        )


def test_check_total_negativo(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta(
            date.today(),
            pyme_id,
            "efectivo",
            iva=0,
            comision_sumup=None,
            total=-100,
        )


def test_fk_pyme_inexistente(dal: DAL) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta(
            date.today(),
            pyme_id=999,
            metodo="efectivo",
            iva=190,
            comision_sumup=None,
            total=1000,
        )


def test_fk_personal_inexistente_en_paquete(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_paquete(
            date.today(),
            pyme_remitente_id=pyme_id,
            nombre_destinatario="X",
            ubicacion_bodega="A1",
            estado_pago="pagado",
            recibido_por=999,
        )


def test_check_ubicacion_bodega_fuera_de_lista(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    personal_id = dal.crear_personal("Juan", "cajero")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_paquete(
            date.today(),
            pyme_remitente_id=pyme_id,
            nombre_destinatario="X",
            ubicacion_bodega="Z9",
            estado_pago="pagado",
            recibido_por=personal_id,
        )


def test_check_estado_pago_invalido(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    personal_id = dal.crear_personal("Juan", "cajero")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_paquete(
            date.today(),
            pyme_remitente_id=pyme_id,
            nombre_destinatario="X",
            ubicacion_bodega="A1",
            estado_pago="gratis",
            recibido_por=personal_id,
        )


def test_check_estado_paquete_invalido(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    personal_id = dal.crear_personal("Juan", "cajero")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_paquete(
            date.today(),
            pyme_remitente_id=pyme_id,
            nombre_destinatario="X",
            ubicacion_bodega="A1",
            estado_pago="pagado",
            recibido_por=personal_id,
            estado="perdido",
        )


def test_unique_caja_diaria_por_fecha(dal: DAL) -> None:
    fecha = date.today()
    dal.crear_caja_diaria(fecha)

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_caja_diaria(fecha)


def test_check_venta_item_cantidad_minima(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    venta_id = dal.crear_venta(
        date.today(), pyme_id, "efectivo", iva=190, comision_sumup=None, total=1000
    )

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta_item(venta_id, "X", precio=100, cantidad=0, subtotal=0)


def test_check_venta_item_precio_positivo(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    venta_id = dal.crear_venta(
        date.today(), pyme_id, "efectivo", iva=190, comision_sumup=None, total=1000
    )

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta_item(venta_id, "X", precio=0, cantidad=1, subtotal=0)


def test_cascade_eliminar_venta_borra_items(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    venta_id = dal.crear_venta(
        date.today(),
        pyme_id,
        "efectivo",
        iva=190,
        comision_sumup=None,
        total=1000,
        items=[
            {"producto": "A", "precio": 500, "cantidad": 1, "subtotal": 500},
            {"producto": "B", "precio": 500, "cantidad": 1, "subtotal": 500},
        ],
    )

    assert len(dal.listar_venta_items(venta_id)) == 2

    dal.eliminar_venta(venta_id)

    assert dal.listar_venta_items(venta_id) == []


def test_comentario_excede_200_caracteres_falla(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_venta(
            date.today(),
            pyme_id,
            "efectivo",
            iva=190,
            comision_sumup=None,
            total=1000,
            comentario="x" * 201,
        )
