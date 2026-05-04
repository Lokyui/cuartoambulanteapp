from __future__ import annotations

from datetime import date

from db.dal import DAL


def _venta(
    dal: DAL,
    pyme_id: int,
    fecha: date,
    metodo: str,
    total: int,
    iva: int,
    comision: int | None,
    items: list[dict] | None = None,
) -> int:
    return dal.crear_venta(
        fecha,
        pyme_id,
        metodo,
        iva=iva,
        comision_sumup=comision,
        total=total,
        items=items,
    )


def test_resumen_dashboard_calcula_neto(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    hoy = date.today()
    _venta(dal, pyme_id, hoy, "efectivo", total=2000, iva=319, comision=None)
    _venta(dal, pyme_id, hoy, "sumup", total=2000, iva=319, comision=35)

    resumen = dal.obtener_resumen_dashboard(hoy)

    assert resumen["total_diario"] == 4000
    assert resumen["numero_ventas"] == 2
    assert resumen["neto"] == 4000 - 319 - 319 - 35


def test_resumen_dashboard_dia_sin_ventas(dal: DAL) -> None:
    resumen = dal.obtener_resumen_dashboard(date.today())

    assert resumen["total_diario"] == 0
    assert resumen["numero_ventas"] == 0
    assert resumen["neto"] == 0
    assert resumen["caja_cerrada"] is False


def test_resumen_dashboard_caja_cerrada(dal: DAL) -> None:
    hoy = date.today()
    dal.crear_caja_diaria(hoy, cerrada=1)

    resumen = dal.obtener_resumen_dashboard(hoy)

    assert resumen["caja_cerrada"] is True


def test_resumen_dashboard_cuenta_paquetes_pendientes(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    personal_id = dal.crear_personal("Cajero", "cajero")
    hoy = date.today()
    dal.crear_paquete(hoy, pyme_id, "Activo 1", "A1", "pagado", personal_id)
    dal.crear_paquete(hoy, pyme_id, "Activo 2", "A2", "por_cobrar", personal_id)
    dal.crear_paquete(
        hoy,
        pyme_id,
        "Entregado",
        "B1",
        "pagado",
        personal_id,
        estado="entregado",
        fecha_entrega=hoy,
    )

    resumen = dal.obtener_resumen_dashboard(hoy)

    assert resumen["entregas_pendientes"] == 2


def test_ventas_por_pyme_del_dia_orden_descendente(dal: DAL) -> None:
    pyme_a = dal.crear_pyme("Pyme A")
    pyme_b = dal.crear_pyme("Pyme B")
    pyme_c = dal.crear_pyme("Pyme C")
    hoy = date.today()

    _venta(dal, pyme_a, hoy, "efectivo", total=1000, iva=159, comision=None)
    _venta(dal, pyme_b, hoy, "efectivo", total=5000, iva=798, comision=None)
    _venta(dal, pyme_b, hoy, "sumup", total=2000, iva=319, comision=35)
    _venta(dal, pyme_c, hoy, "efectivo", total=3000, iva=479, comision=None)

    ranking = dal.ventas_por_pyme_del_dia(hoy)

    assert [r["pyme_nombre"] for r in ranking] == ["Pyme B", "Pyme C", "Pyme A"]
    assert [r["total"] for r in ranking] == [7000, 3000, 1000]


def test_ventas_por_pyme_del_dia_ignora_otros_dias(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme A")
    _venta(dal, pyme_id, date(2026, 4, 27), "efectivo", total=1000, iva=159, comision=None)
    _venta(dal, pyme_id, date(2026, 4, 28), "efectivo", total=2000, iva=319, comision=None)

    ranking = dal.ventas_por_pyme_del_dia(date(2026, 4, 28))

    assert len(ranking) == 1
    assert ranking[0]["total"] == 2000


def test_listar_ventas_recientes_join_pyme_y_primer_producto(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("BADTRIP")
    hoy = date.today()
    _venta(
        dal,
        pyme_id,
        hoy,
        "efectivo",
        total=1500,
        iva=239,
        comision=None,
        items=[
            {"producto": "Polera", "precio": 1000, "cantidad": 1, "subtotal": 1000},
            {"producto": "Sticker", "precio": 500, "cantidad": 1, "subtotal": 500},
        ],
    )

    ventas = dal.listar_ventas_recientes(hoy)

    assert len(ventas) == 1
    venta = ventas[0]
    assert venta["pyme_nombre"] == "BADTRIP"
    assert venta["primer_producto"] == "Polera"
    assert venta["cantidad_items"] == 2
    assert venta["total"] == 1500


def test_listar_ventas_recientes_orden_y_limit(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme")
    hoy = date.today()
    for i in range(5):
        _venta(dal, pyme_id, hoy, "efectivo", total=100 * (i + 1), iva=0, comision=None)

    ventas = dal.listar_ventas_recientes(hoy, limit=3)

    assert len(ventas) == 3
    ids = [v["id"] for v in ventas]
    assert ids == sorted(ids, reverse=True)


def test_listar_ventas_recientes_sin_items(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme")
    hoy = date.today()
    _venta(dal, pyme_id, hoy, "efectivo", total=1000, iva=159, comision=None)

    ventas = dal.listar_ventas_recientes(hoy)

    assert ventas[0]["primer_producto"] is None
    assert ventas[0]["cantidad_items"] == 0


def test_resumen_mensual_por_pyme_calcula_neto_liquidar(dal: DAL) -> None:
    pyme_a = dal.crear_pyme("Pyme A")
    pyme_b = dal.crear_pyme("Pyme B")

    _venta(dal, pyme_a, date(2026, 4, 5), "efectivo", total=1000, iva=159, comision=None)
    _venta(dal, pyme_a, date(2026, 4, 20), "sumup", total=2000, iva=319, comision=35)
    _venta(dal, pyme_b, date(2026, 4, 10), "efectivo", total=5000, iva=798, comision=None)
    _venta(dal, pyme_b, date(2026, 5, 1), "efectivo", total=9999, iva=1597, comision=None)

    resumen = dal.resumen_mensual_por_pyme(2026, 4)

    assert len(resumen) == 2
    pyme_b_data = next(r for r in resumen if r["pyme_id"] == pyme_b)
    pyme_a_data = next(r for r in resumen if r["pyme_id"] == pyme_a)

    assert pyme_b_data["total_bruto"] == 5000
    assert pyme_b_data["total_efectivo"] == 5000
    assert pyme_b_data["total_sumup"] == 0
    assert pyme_b_data["neto_liquidar"] == 5000 - 798

    assert pyme_a_data["total_bruto"] == 3000
    assert pyme_a_data["total_efectivo"] == 1000
    assert pyme_a_data["total_sumup"] == 2000
    assert pyme_a_data["neto_liquidar"] == 3000 - (159 + 319) - 35


def test_resumen_mensual_orden_por_total_descendente(dal: DAL) -> None:
    pyme_a = dal.crear_pyme("Pyme A")
    pyme_b = dal.crear_pyme("Pyme B")
    _venta(dal, pyme_a, date(2026, 4, 5), "efectivo", total=1000, iva=159, comision=None)
    _venta(dal, pyme_b, date(2026, 4, 6), "efectivo", total=5000, iva=798, comision=None)

    resumen = dal.resumen_mensual_por_pyme(2026, 4)

    assert [r["pyme_id"] for r in resumen] == [pyme_b, pyme_a]


def test_resumen_mensual_diciembre_no_se_pasa_de_anio(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme A")
    _venta(dal, pyme_id, date(2026, 12, 31), "efectivo", total=1000, iva=159, comision=None)
    _venta(dal, pyme_id, date(2027, 1, 1), "efectivo", total=2000, iva=319, comision=None)

    resumen = dal.resumen_mensual_por_pyme(2026, 12)

    assert len(resumen) == 1
    assert resumen[0]["total_bruto"] == 1000
