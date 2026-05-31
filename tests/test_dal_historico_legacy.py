from __future__ import annotations

from src.db.dal import DAL


def test_crear_y_listar_historico_legacy(dal: DAL) -> None:
    rid = dal.crear_historico_legacy(
        fuente="PUNTO_DE_ENTREGA.xlsx:entregas viejas",
        payload='{"quien_trajo": "memory lab", "fecha": "2026-01-02"}',
        motivo="pyme no registrada",
    )

    rechazos = dal.listar_historico_legacy()

    assert rid > 0
    assert len(rechazos) == 1
    assert rechazos[0]["motivo"] == "pyme no registrada"


def test_listar_filtra_por_fuente(dal: DAL) -> None:
    dal.crear_historico_legacy(fuente="A", payload="{}")
    dal.crear_historico_legacy(fuente="B", payload="{}")
    dal.crear_historico_legacy(fuente="A", payload="{}")

    solo_a = dal.listar_historico_legacy(fuente="A")

    assert len(solo_a) == 2
    assert all(r["fuente"] == "A" for r in solo_a)


def test_listar_aplica_limite(dal: DAL) -> None:
    for i in range(5):
        dal.crear_historico_legacy(fuente="x", payload=str(i))

    assert len(dal.listar_historico_legacy(limite=2)) == 2


def test_eliminar_historico_legacy(dal: DAL) -> None:
    rid = dal.crear_historico_legacy(fuente="x", payload="{}")

    assert dal.eliminar_historico_legacy(rid) is True
    assert dal.obtener_historico_legacy(rid) is None
