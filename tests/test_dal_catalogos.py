from __future__ import annotations

import sqlite3

import pytest

from src.db.dal import DAL


def test_crear_y_obtener_pyme(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("BADTRIP")
    pyme = dal.obtener_pyme(pyme_id)

    assert pyme is not None
    assert pyme["nombre"] == "BADTRIP"
    assert pyme["activa"] == 1


def test_listar_pymes_filtra_activas(dal: DAL) -> None:
    dal.crear_pyme("Activa1", activa=1)
    dal.crear_pyme("Activa2", activa=1)
    inactiva_id = dal.crear_pyme("Inactiva", activa=0)

    activas = dal.listar_pymes(solo_activas=True)
    todas = dal.listar_pymes(solo_activas=False)

    assert len(activas) == 2
    assert len(todas) == 3
    assert all(p["id"] != inactiva_id for p in activas)


def test_listar_pymes_orden_alfabetico_case_insensitive(dal: DAL) -> None:
    dal.crear_pyme("zerodos")
    dal.crear_pyme("BADTRIP")
    dal.crear_pyme("milen")

    pymes = dal.listar_pymes()
    nombres = [p["nombre"] for p in pymes]

    assert nombres == ["BADTRIP", "milen", "zerodos"]


def test_actualizar_pyme(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Original")

    cambio = dal.actualizar_pyme(pyme_id, nombre="Renombrada", activa=0)
    pyme = dal.obtener_pyme(pyme_id)

    assert cambio is True
    assert pyme is not None
    assert pyme["nombre"] == "Renombrada"
    assert pyme["activa"] == 0


def test_eliminar_pyme(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Borrable")

    eliminada = dal.eliminar_pyme(pyme_id)

    assert eliminada is True
    assert dal.obtener_pyme(pyme_id) is None


def test_pyme_unique_nombre(dal: DAL) -> None:
    dal.crear_pyme("BADTRIP")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_pyme("BADTRIP")


def test_pyme_unique_nocase(dal: DAL) -> None:
    dal.crear_pyme("BADTRIP")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_pyme("badtrip")


def test_crear_y_obtener_personal(dal: DAL) -> None:
    personal_id = dal.crear_personal("Juan Perez", "cajero")
    personal = dal.obtener_personal(personal_id)

    assert personal is not None
    assert personal["nombre_display"] == "Juan Perez"
    assert personal["rol"] == "cajero"
    assert personal["activo"] == 1


def test_listar_personal_filtra_activos(dal: DAL) -> None:
    dal.crear_personal("Activa", "cajero", activo=1)
    dal.crear_personal("Inactivo", "cajero", activo=0)

    activos = dal.listar_personal(solo_activos=True)
    todos = dal.listar_personal(solo_activos=False)

    assert len(activos) == 1
    assert len(todos) == 2


def test_personal_rol_invalido(dal: DAL) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_personal("Quien Sabe", "gerente")


def test_personal_unique_nombre_display(dal: DAL) -> None:
    dal.crear_personal("Juan Perez", "cajero")

    with pytest.raises(sqlite3.IntegrityError):
        dal.crear_personal("Juan Perez", "socio")


def test_actualizar_personal(dal: DAL) -> None:
    personal_id = dal.crear_personal("Carolina", "cajero")

    cambio = dal.actualizar_personal(personal_id, nombre_display="Carolina S.", rol="socio", activo=1)
    personal = dal.obtener_personal(personal_id)

    assert cambio is True
    assert personal is not None
    assert personal["nombre_display"] == "Carolina S."
    assert personal["rol"] == "socio"


def test_eliminar_personal(dal: DAL) -> None:
    personal_id = dal.crear_personal("Borrable", "cajero")

    eliminado = dal.eliminar_personal(personal_id)

    assert eliminado is True
    assert dal.obtener_personal(personal_id) is None
