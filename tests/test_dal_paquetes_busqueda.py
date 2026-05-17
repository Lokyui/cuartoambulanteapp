from __future__ import annotations

from datetime import date, timedelta

from src.db.dal import DAL


def _setup_paquetes_demo(dal: DAL) -> tuple[int, int]:
    pyme_id = dal.crear_pyme("Pyme Test")
    personal_id = dal.crear_personal("Cajero", "cajero")
    return pyme_id, personal_id


def test_buscar_paquetes_por_nombre_parcial_case_insensitive(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    dal.crear_paquete(
        date.today(), pyme_id, "Alejandro Jara", "A1", "pagado", personal_id
    )
    dal.crear_paquete(
        date.today(), pyme_id, "Carolina Silva", "B2", "pagado", personal_id
    )
    dal.crear_paquete(
        date.today(), pyme_id, "Maria Paz", "C3", "por_cobrar", personal_id
    )

    resultados = dal.buscar_paquetes_por_nombre("ALE")

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Alejandro Jara"


def test_buscar_paquetes_por_nombre_match_intermedio(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    dal.crear_paquete(
        date.today(), pyme_id, "Alejandro Jara", "A1", "pagado", personal_id
    )
    dal.crear_paquete(
        date.today(), pyme_id, "Carolina Silva", "B2", "pagado", personal_id
    )

    resultados = dal.buscar_paquetes_por_nombre("rol")

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Carolina Silva"


def test_buscar_paquetes_excluye_entregados_por_defecto(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    dal.crear_paquete(
        date.today(),
        pyme_id,
        "Alejandro Jara",
        "A1",
        "pagado",
        personal_id,
        estado="entregado",
        fecha_entrega=date.today(),
    )

    activos = dal.buscar_paquetes_por_nombre("Alejandro")
    todos = dal.buscar_paquetes_por_nombre("Alejandro", solo_activos=False)

    assert activos == []
    assert len(todos) == 1


def test_buscar_paquetes_sin_resultados(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    dal.crear_paquete(
        date.today(), pyme_id, "Alejandro", "A1", "pagado", personal_id
    )

    assert dal.buscar_paquetes_por_nombre("Zzz") == []


def test_demorados_no_demorado_borde_inferior(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    hoy = date.today()
    dal.crear_paquete(
        hoy - timedelta(days=6), pyme_id, "Alguien", "A1", "pagado", personal_id
    )

    assert dal.listar_paquetes_demorados(hoy) == []


def test_demorados_borde_demorado_dia_8(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    hoy = date.today()
    dal.crear_paquete(
        hoy - timedelta(days=8), pyme_id, "Alguien", "A1", "pagado", personal_id
    )

    resultados = dal.listar_paquetes_demorados(hoy)

    assert len(resultados) == 1
    assert resultados[0]["nivel"] == "Demorado"
    assert resultados[0]["dias_en_bodega"] == 8


def test_demorados_borde_demorado_dia_14(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    hoy = date.today()
    dal.crear_paquete(
        hoy - timedelta(days=14), pyme_id, "Alguien", "A1", "pagado", personal_id
    )

    resultados = dal.listar_paquetes_demorados(hoy)

    assert len(resultados) == 1
    assert resultados[0]["nivel"] == "Demorado"


def test_demorados_critico_dia_15(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    hoy = date.today()
    dal.crear_paquete(
        hoy - timedelta(days=15), pyme_id, "Alguien", "A1", "pagado", personal_id
    )

    resultados = dal.listar_paquetes_demorados(hoy)

    assert len(resultados) == 1
    assert resultados[0]["nivel"] == "Crítico"


def test_demorados_orden_descendente_por_dias(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    hoy = date.today()
    dal.crear_paquete(
        hoy - timedelta(days=8), pyme_id, "Reciente", "A1", "pagado", personal_id
    )
    dal.crear_paquete(
        hoy - timedelta(days=20), pyme_id, "Antiguo", "A2", "pagado", personal_id
    )
    dal.crear_paquete(
        hoy - timedelta(days=12), pyme_id, "Medio", "A3", "pagado", personal_id
    )

    resultados = dal.listar_paquetes_demorados(hoy)

    assert [r["nombre_destinatario"] for r in resultados] == ["Antiguo", "Medio", "Reciente"]
    assert [r["dias_en_bodega"] for r in resultados] == [20, 12, 8]


def test_demorados_excluye_entregados(dal: DAL) -> None:
    pyme_id, personal_id = _setup_paquetes_demo(dal)
    hoy = date.today()
    dal.crear_paquete(
        hoy - timedelta(days=20),
        pyme_id,
        "Ya entregado",
        "A1",
        "pagado",
        personal_id,
        estado="entregado",
        fecha_entrega=hoy,
    )

    assert dal.listar_paquetes_demorados(hoy) == []
