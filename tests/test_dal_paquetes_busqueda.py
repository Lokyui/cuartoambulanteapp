from __future__ import annotations

from datetime import date

from src.db.dal import DAL


def _setup(dal: DAL) -> tuple[int, int]:
    pyme_id = dal.crear_pyme("BADTRIP")
    personal_id = dal.crear_personal("Cajero", "cajero")
    return pyme_id, personal_id


def test_busqueda_por_destinatario_case_insensitive(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Alejandro Jara", "A1", "pagado", personal_id)
    dal.crear_paquete(date.today(), pyme_id, "Carolina Silva", "B2", "pagado", personal_id)

    resultados = dal.listar_paquetes(busqueda="ALE")

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Alejandro Jara"


def test_busqueda_match_intermedio(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Alejandro", "A1", "pagado", personal_id)
    dal.crear_paquete(date.today(), pyme_id, "Carolina", "B2", "pagado", personal_id)

    resultados = dal.listar_paquetes(busqueda="rol")

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Carolina"


def test_busqueda_por_nombre_de_pyme(dal: DAL) -> None:
    badtrip = dal.crear_pyme("BADTRIP")
    nixamala = dal.crear_pyme("NIXAMALA")
    personal_id = dal.crear_personal("Cajero", "cajero")
    dal.crear_paquete(date.today(), badtrip, "Cliente1", "A1", "pagado", personal_id)
    dal.crear_paquete(date.today(), nixamala, "Cliente2", "A2", "pagado", personal_id)

    resultados = dal.listar_paquetes(busqueda="nixa")

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Cliente2"


def test_busqueda_por_ubicacion(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Cliente1", "A1", "pagado", personal_id)
    dal.crear_paquete(date.today(), pyme_id, "Cliente2", "B2", "pagado", personal_id)

    resultados = dal.listar_paquetes(busqueda="b2")

    assert len(resultados) == 1
    assert resultados[0]["ubicacion_bodega"] == "B2"


def test_busqueda_sin_resultados(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Alejandro", "A1", "pagado", personal_id)

    assert dal.listar_paquetes(busqueda="Zzz") == []


def test_busqueda_combina_con_filtro_estado(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Alejandro Activo", "A1", "pagado", personal_id)
    dal.crear_paquete(
        date.today(), pyme_id, "Alejandro Entregado", "A2", "pagado", personal_id,
        estado="entregado", fecha_entrega=date.today(),
    )

    activos = dal.listar_paquetes(busqueda="alejandro", estado="activo")
    todos = dal.listar_paquetes(busqueda="alejandro")

    assert len(activos) == 1
    assert activos[0]["nombre_destinatario"] == "Alejandro Activo"
    assert len(todos) == 2


def test_listar_sin_busqueda_devuelve_todos(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Cliente1", "A1", "pagado", personal_id)
    dal.crear_paquete(date.today(), pyme_id, "Cliente2", "B2", "pagado", personal_id)

    assert len(dal.listar_paquetes()) == 2


def test_listar_filtra_por_estado_pago(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Pago1", "A1", "pagado", personal_id)
    dal.crear_paquete(date.today(), pyme_id, "Cobrar1", "A2", "por_cobrar", personal_id)
    dal.crear_paquete(date.today(), pyme_id, "Cobrar2", "A3", "por_cobrar", personal_id)

    por_cobrar = dal.listar_paquetes(estado_pago="por_cobrar")

    assert len(por_cobrar) == 2
    assert all(p["estado_pago"] == "por_cobrar" for p in por_cobrar)


def test_resultado_incluye_nombre_pyme_resuelto(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    dal.crear_paquete(date.today(), pyme_id, "Cliente", "A1", "pagado", personal_id)

    paquete = dal.listar_paquetes()[0]

    assert paquete["nombre_pyme"] == "BADTRIP"


# ── Filtro por rango de fecha de entrega ─────────────────────────────────────

from datetime import date as _date  # alias para evitar shadowing


def _entregado(dal: DAL, pyme_id: int, personal_id: int, destinatario: str, fecha_entrega: _date) -> int:
    pid = dal.crear_paquete(
        _date(2026, 1, 1), pyme_id, destinatario, "A1", "pagado", personal_id,
    )
    dal.actualizar_paquete(pid, {"estado": "entregado", "fecha_entrega": fecha_entrega})
    return pid


def test_filtro_fecha_entrega_rango(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    _entregado(dal, pyme_id, personal_id, "Mayo15", _date(2026, 5, 15))
    _entregado(dal, pyme_id, personal_id, "Junio1", _date(2026, 6, 1))
    _entregado(dal, pyme_id, personal_id, "Julio10", _date(2026, 7, 10))

    resultados = dal.listar_paquetes(
        fecha_entrega_desde=_date(2026, 6, 1),
        fecha_entrega_hasta=_date(2026, 6, 30),
    )

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Junio1"


def test_filtro_fecha_entrega_incluye_los_bordes(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    _entregado(dal, pyme_id, personal_id, "Inicio", _date(2026, 6, 1))
    _entregado(dal, pyme_id, personal_id, "Fin", _date(2026, 6, 30))

    resultados = dal.listar_paquetes(
        fecha_entrega_desde=_date(2026, 6, 1),
        fecha_entrega_hasta=_date(2026, 6, 30),
    )

    assert len(resultados) == 2


def test_filtro_fecha_entrega_ordena_por_fecha_desc(dal: DAL) -> None:
    pyme_id, personal_id = _setup(dal)
    _entregado(dal, pyme_id, personal_id, "Viejo", _date(2026, 5, 1))
    _entregado(dal, pyme_id, personal_id, "Reciente", _date(2026, 6, 1))

    resultados = dal.listar_paquetes(
        estado="entregado",
        fecha_entrega_desde=_date(2026, 1, 1),
        fecha_entrega_hasta=_date(2026, 12, 31),
    )

    assert [p["nombre_destinatario"] for p in resultados] == ["Reciente", "Viejo"]
