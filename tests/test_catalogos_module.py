from __future__ import annotations

import pytest

from src.db.dal import DAL
from src.modules.catalogos_module import CatalogosModule


@pytest.fixture
def modulo(dal: DAL) -> CatalogosModule:
    return CatalogosModule(dal)


# ── Pymes ────────────────────────────────────────────────────────────────────

def test_listar_pymes_incluye_inactivas(modulo: CatalogosModule) -> None:
    modulo.crear_pyme("Activa", activa=True)
    modulo.crear_pyme("Inactiva", activa=False)

    pymes = modulo.listar_pymes()

    assert len(pymes) == 2


def test_crear_pyme_trimea_y_persiste(modulo: CatalogosModule) -> None:
    pid = modulo.crear_pyme("  BADTRIP  ", activa=True)

    pymes = modulo.listar_pymes()
    creada = next(p for p in pymes if p["id"] == pid)
    assert creada["nombre"] == "BADTRIP"
    assert creada["activa"] == 1


def test_crear_pyme_rechaza_nombre_vacio(modulo: CatalogosModule) -> None:
    with pytest.raises(ValueError):
        modulo.crear_pyme("   ", activa=True)


def test_actualizar_pyme_aplica_cambios(modulo: CatalogosModule) -> None:
    pid = modulo.crear_pyme("Original", activa=True)

    modulo.actualizar_pyme(pid, nombre="Renombrada", activa=False)

    p = next(p for p in modulo.listar_pymes() if p["id"] == pid)
    assert p["nombre"] == "Renombrada"
    assert p["activa"] == 0


def test_actualizar_pyme_rechaza_nombre_vacio(modulo: CatalogosModule) -> None:
    pid = modulo.crear_pyme("Original", activa=True)

    with pytest.raises(ValueError):
        modulo.actualizar_pyme(pid, nombre="", activa=True)


def test_eliminar_pyme_sin_referencias(modulo: CatalogosModule) -> None:
    pid = modulo.crear_pyme("Borrable", activa=True)

    assert modulo.eliminar_pyme(pid) is True
    assert all(p["id"] != pid for p in modulo.listar_pymes())


# ── Personal ─────────────────────────────────────────────────────────────────

def test_crear_personal_normaliza_y_persiste(modulo: CatalogosModule) -> None:
    pid = modulo.crear_personal("  Less  ", "socio", activo=True)

    creado = next(p for p in modulo.listar_personal() if p["id"] == pid)
    assert creado["nombre_display"] == "Less"
    assert creado["rol"] == "socio"
    assert creado["activo"] == 1


def test_crear_personal_rechaza_rol_invalido(modulo: CatalogosModule) -> None:
    with pytest.raises(ValueError):
        modulo.crear_personal("X", "gerente", activo=True)


def test_crear_personal_rechaza_nombre_vacio(modulo: CatalogosModule) -> None:
    with pytest.raises(ValueError):
        modulo.crear_personal("  ", "cajero", activo=True)


def test_actualizar_personal_aplica_cambios(modulo: CatalogosModule) -> None:
    pid = modulo.crear_personal("Carolina", "cajero", activo=True)

    modulo.actualizar_personal(pid, "Carolina S.", "socio", activo=False)

    p = next(p for p in modulo.listar_personal() if p["id"] == pid)
    assert p["nombre_display"] == "Carolina S."
    assert p["rol"] == "socio"
    assert p["activo"] == 0


def test_actualizar_personal_valida_rol(modulo: CatalogosModule) -> None:
    pid = modulo.crear_personal("Carolina", "cajero", activo=True)

    with pytest.raises(ValueError):
        modulo.actualizar_personal(pid, "Carolina", "vendedor", activo=True)


def test_eliminar_personal_sin_referencias(modulo: CatalogosModule) -> None:
    pid = modulo.crear_personal("Borrable", "cajero", activo=True)

    assert modulo.eliminar_personal(pid) is True
    assert all(p["id"] != pid for p in modulo.listar_personal())


def test_listar_personal_incluye_inactivos(modulo: CatalogosModule) -> None:
    modulo.crear_personal("Activo", "cajero", activo=True)
    modulo.crear_personal("Inactivo", "cajero", activo=False)

    assert len(modulo.listar_personal()) == 2
