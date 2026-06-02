from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from src.modules.ventas_module import VentasModule


class FakeDAL:
    """Captura los argumentos de crear_venta sin tocar BD."""

    def __init__(self) -> None:
        self.llamadas: list[dict[str, Any]] = []
        self.proximo_id = 1
        self.caja_por_fecha: dict[Any, dict[str, Any]] = {}

    def crear_venta(self, *args: Any, **kwargs: Any) -> int:
        # Soporta tanto la firma posicional (fecha, pyme_id, metodo) como kwargs
        if args:
            posicional_keys = ("fecha", "pyme_id", "metodo")
            for key, value in zip(posicional_keys, args):
                kwargs.setdefault(key, value)
        self.llamadas.append(kwargs)
        actual = self.proximo_id
        self.proximo_id += 1
        return actual

    def obtener_caja_diaria(self, fecha: Any) -> dict[str, Any] | None:
        return self.caja_por_fecha.get(fecha)


@pytest.fixture
def fake_dal() -> FakeDAL:
    return FakeDAL()


@pytest.fixture
def modulo(fake_dal: FakeDAL) -> VentasModule:
    return VentasModule(fake_dal)  # type: ignore[arg-type]


# ── calcular_totales ─────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "total, iva_esperado",
    [
        (18000, 2874),   # seed marzo #01
        (24000, 3832),   # seed marzo #02
        (13500, 2155),   # seed marzo #03
        (8000, 1277),    # seed marzo #04
        (14000, 2235),   # seed marzo #05
        (22500, 3592),   # seed marzo #08
    ],
)
def test_iva_coincide_con_seed(modulo: VentasModule, total: int, iva_esperado: int) -> None:
    totales = modulo.calcular_totales(
        items=[{"producto": "X", "precio": total, "cantidad": 1}],
        metodo="efectivo",
    )
    assert totales["iva"] == iva_esperado


@pytest.mark.parametrize(
    "total, comision_esperada",
    [
        (24000, 420),
        (8000, 140),
        (18000, 315),
        (22500, 394),
        (10500, 184),
    ],
)
def test_comision_sumup_coincide_con_seed(
    modulo: VentasModule, total: int, comision_esperada: int
) -> None:
    totales = modulo.calcular_totales(
        items=[{"producto": "X", "precio": total, "cantidad": 1}],
        metodo="sumup",
    )
    assert totales["comision_sumup"] == comision_esperada


def test_efectivo_no_lleva_comision(modulo: VentasModule) -> None:
    totales = modulo.calcular_totales(
        items=[{"producto": "X", "precio": 5000, "cantidad": 1}],
        metodo="efectivo",
    )
    assert totales["comision_sumup"] is None


def test_total_es_suma_de_subtotales(modulo: VentasModule) -> None:
    totales = modulo.calcular_totales(
        items=[
            {"producto": "A", "precio": 1000, "cantidad": 2},  # 2000
            {"producto": "B", "precio": 500, "cantidad": 3},   # 1500
        ],
        metodo="efectivo",
    )
    assert totales["total"] == 3500


def test_metodo_invalido_lanza_error(modulo: VentasModule) -> None:
    with pytest.raises(ValueError):
        modulo.calcular_totales(
            items=[{"producto": "X", "precio": 1000, "cantidad": 1}],
            metodo="transferencia",
        )


def test_items_vacios_lanza_error(modulo: VentasModule) -> None:
    with pytest.raises(ValueError):
        modulo.calcular_totales(items=[], metodo="efectivo")


def test_precio_cero_lanza_error(modulo: VentasModule) -> None:
    with pytest.raises(ValueError):
        modulo.calcular_totales(
            items=[{"producto": "X", "precio": 0, "cantidad": 1}],
            metodo="efectivo",
        )


# ── procesar_nueva_venta ─────────────────────────────────────────────────────

# Nota: la derivación de `articulo`/`valor`/`cantidad` (agregados de cabecera)
# vive ahora en el DAL — el módulo solo orquesta cálculos. Los tests de esa
# derivación están en tests/test_dal_ventas.py.

def test_procesar_envia_totales_y_items_al_dal(
    modulo: VentasModule, fake_dal: FakeDAL
) -> None:
    modulo.procesar_nueva_venta({
        "pyme_id": 7,
        "fecha": date(2026, 5, 12),
        "metodo": "sumup",
        "items": [
            {"producto": "A", "precio": 10000, "cantidad": 1},
            {"producto": "B", "precio": 5000, "cantidad": 2},
        ],
        "comentario": "test",
    })

    args = fake_dal.llamadas[0]
    assert args["pyme_id"] == 7
    assert args["metodo"] == "sumup"
    assert args["total"] == 20000
    assert args["iva"] == int(round(20000 / 1.19 * 0.19))
    assert args["comision_sumup"] == int(round(20000 * 0.0175))
    assert args["comentario"] == "test"
    assert len(args["items"]) == 2


def test_procesar_normaliza_metodo_a_minusculas(
    modulo: VentasModule, fake_dal: FakeDAL
) -> None:
    modulo.procesar_nueva_venta({
        "pyme_id": 1,
        "fecha": date(2026, 5, 12),
        "metodo": "SUMUP",
        "items": [{"producto": "X", "precio": 1000, "cantidad": 1}],
    })
    assert fake_dal.llamadas[0]["metodo"] == "sumup"


# ── Bloqueo de ventas con caja cerrada (HU4) ────────────────────────────────

def test_procesar_falla_si_caja_del_dia_esta_cerrada(
    modulo: VentasModule, fake_dal: FakeDAL
) -> None:
    fecha = date(2026, 5, 12)
    fake_dal.caja_por_fecha[fecha] = {"cerrada": 1}

    with pytest.raises(ValueError, match="caja del día está cerrada"):
        modulo.procesar_nueva_venta({
            "pyme_id": 1,
            "fecha": fecha,
            "metodo": "efectivo",
            "items": [{"producto": "X", "precio": 1000, "cantidad": 1}],
        })

    assert fake_dal.llamadas == []


def test_procesar_permite_venta_si_caja_existe_pero_no_esta_cerrada(
    modulo: VentasModule, fake_dal: FakeDAL
) -> None:
    fecha = date(2026, 5, 12)
    fake_dal.caja_por_fecha[fecha] = {"cerrada": 0}

    modulo.procesar_nueva_venta({
        "pyme_id": 1,
        "fecha": fecha,
        "metodo": "efectivo",
        "items": [{"producto": "X", "precio": 1000, "cantidad": 1}],
    })

    assert len(fake_dal.llamadas) == 1


def test_procesar_permite_venta_si_no_existe_caja_del_dia(
    modulo: VentasModule, fake_dal: FakeDAL
) -> None:
    modulo.procesar_nueva_venta({
        "pyme_id": 1,
        "fecha": date(2026, 5, 12),
        "metodo": "efectivo",
        "items": [{"producto": "X", "precio": 1000, "cantidad": 1}],
    })

    assert len(fake_dal.llamadas) == 1
