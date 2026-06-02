from __future__ import annotations

from datetime import date

import pytest

from src.db.dal import DAL
from src.modules.retiros_module import RetirosModule


@pytest.fixture
def modulo(dal: DAL) -> RetirosModule:
    return RetirosModule(dal)


@pytest.fixture
def contexto(dal: DAL) -> dict:
    return {
        "pyme_id": dal.crear_pyme("BADTRIP"),
        "personal_id": dal.crear_personal("Less", "socio"),
    }


_UBICACIONES = [f"{l}{n}" for l in "ABC" for n in range(1, 4)]
_contador_ubicacion = 0


def _datos(ctx: dict, destinatario: str = "Cliente", **overrides) -> dict:
    global _contador_ubicacion
    ubicacion = _UBICACIONES[_contador_ubicacion % len(_UBICACIONES)]
    _contador_ubicacion += 1
    base = {
        "pyme_id": ctx["pyme_id"],
        "fecha_llegada": date.today(),
        "destinatario": destinatario,
        "ubicacion": ubicacion,
        "estado_pago": "pagado",
        "recibido_por": ctx["personal_id"],
        "descripcion": None,
    }
    base.update(overrides)
    return base


# ── registrar_ingreso ────────────────────────────────────────────────────────

def test_registrar_ingreso_crea_paquete_activo(modulo: RetirosModule, contexto: dict) -> None:
    pid = modulo.registrar_ingreso(_datos(contexto))

    paquete = modulo.obtener_paquete(pid)
    assert paquete is not None
    assert paquete["estado"] == "activo"
    assert paquete["nombre_destinatario"] == "Cliente"


def test_registrar_ingreso_rechaza_ubicacion_ocupada(modulo: RetirosModule, contexto: dict) -> None:
    modulo.registrar_ingreso(_datos(contexto, destinatario="Primero", ubicacion="A1"))

    with pytest.raises(ValueError, match="ya está ocupada"):
        modulo.registrar_ingreso(_datos(contexto, destinatario="Segundo", ubicacion="A1"))


def test_ubicacion_se_libera_cuando_se_entrega(modulo: RetirosModule, contexto: dict) -> None:
    pid = modulo.registrar_ingreso(_datos(contexto, destinatario="Primero", ubicacion="A1"))
    modulo.marcar_entregado(pid)

    nuevo = modulo.registrar_ingreso(_datos(contexto, destinatario="Segundo", ubicacion="A1"))
    assert modulo.obtener_paquete(nuevo) is not None


def test_actualizar_paquete_a_ubicacion_ocupada_falla(modulo: RetirosModule, contexto: dict) -> None:
    pid1 = modulo.registrar_ingreso(_datos(contexto, destinatario="Primero", ubicacion="A1"))
    pid2 = modulo.registrar_ingreso(_datos(contexto, destinatario="Segundo", ubicacion="A2"))

    with pytest.raises(ValueError, match="ya está ocupada"):
        modulo.actualizar_paquete(pid2, {"ubicacion": "A1"})

    # control: el paquete original puede cambiar a una libre.
    assert modulo.actualizar_paquete(pid1, {"ubicacion": "B1"}) is True


# ── marcar_entregado ─────────────────────────────────────────────────────────

def test_marcar_entregado_cambia_estado_y_setea_fecha(modulo: RetirosModule, contexto: dict) -> None:
    pid = modulo.registrar_ingreso(_datos(contexto))

    cambio = modulo.marcar_entregado(pid)
    paquete = modulo.obtener_paquete(pid)

    assert cambio is True
    assert paquete["estado"] == "entregado"
    assert paquete["fecha_entrega"] is not None


# ── actualizar_paquete ───────────────────────────────────────────────────────

def test_actualizar_paquete_edita_campos(modulo: RetirosModule, contexto: dict) -> None:
    pid = modulo.registrar_ingreso(_datos(contexto, destinatario="Original"))

    modulo.actualizar_paquete(pid, {
        "destinatario": "Editado",
        "ubicacion": "B2",
        "estado_pago": "por_cobrar",
    })

    paquete = modulo.obtener_paquete(pid)
    assert paquete["nombre_destinatario"] == "Editado"
    assert paquete["ubicacion_bodega"] == "B2"
    assert paquete["estado_pago"] == "por_cobrar"


def test_actualizar_paquete_ignora_campos_no_pasados(modulo: RetirosModule, contexto: dict) -> None:
    pid = modulo.registrar_ingreso(_datos(contexto, destinatario="Original"))

    modulo.actualizar_paquete(pid, {"ubicacion": "C3"})

    paquete = modulo.obtener_paquete(pid)
    assert paquete["nombre_destinatario"] == "Original"
    assert paquete["ubicacion_bodega"] == "C3"


# ── listar_* ─────────────────────────────────────────────────────────────────

def test_listar_pendientes_excluye_entregados(modulo: RetirosModule, contexto: dict) -> None:
    pid_activo = modulo.registrar_ingreso(_datos(contexto, destinatario="Activo"))
    pid_entregado = modulo.registrar_ingreso(_datos(contexto, destinatario="Entregado"))
    modulo.marcar_entregado(pid_entregado)

    pendientes = modulo.listar_pendientes()

    assert len(pendientes) == 1
    assert pendientes[0]["id"] == pid_activo


def test_listar_por_cobrar_filtra_estado_pago(modulo: RetirosModule, contexto: dict) -> None:
    modulo.registrar_ingreso(_datos(contexto, destinatario="Pagado", estado_pago="pagado"))
    modulo.registrar_ingreso(_datos(contexto, destinatario="Pendiente", estado_pago="por_cobrar"))

    por_cobrar = modulo.listar_por_cobrar()

    assert len(por_cobrar) == 1
    assert por_cobrar[0]["nombre_destinatario"] == "Pendiente"


# ── buscar_paquetes ──────────────────────────────────────────────────────────

def test_buscar_paquetes_por_destinatario(modulo: RetirosModule, contexto: dict) -> None:
    modulo.registrar_ingreso(_datos(contexto, destinatario="Alejandro Jara"))
    modulo.registrar_ingreso(_datos(contexto, destinatario="Carolina Silva"))

    resultados = modulo.buscar_paquetes("ale")

    assert len(resultados) == 1
    assert resultados[0]["nombre_destinatario"] == "Alejandro Jara"


def test_buscar_paquetes_combinado_con_por_cobrar(modulo: RetirosModule, contexto: dict) -> None:
    modulo.registrar_ingreso(_datos(contexto, destinatario="Alejandro pagado", estado_pago="pagado"))
    modulo.registrar_ingreso(_datos(contexto, destinatario="Alejandro pendiente", estado_pago="por_cobrar"))

    resultados = modulo.buscar_paquetes("alejandro", solo_por_cobrar=True)

    assert len(resultados) == 1
    assert resultados[0]["estado_pago"] == "por_cobrar"


def test_buscar_paquetes_texto_vacio_devuelve_todos(modulo: RetirosModule, contexto: dict) -> None:
    modulo.registrar_ingreso(_datos(contexto, destinatario="A"))
    modulo.registrar_ingreso(_datos(contexto, destinatario="B"))

    assert len(modulo.buscar_paquetes("")) == 2


# ── listar_historial ─────────────────────────────────────────────────────────

from datetime import timedelta


def _registrar_y_entregar(
    modulo: RetirosModule, ctx: dict, destinatario: str, fecha_entrega
) -> int:
    pid = modulo.registrar_ingreso(_datos(ctx, destinatario=destinatario))
    modulo.marcar_entregado(pid, fecha_entrega=fecha_entrega)
    return pid


def test_historial_solo_devuelve_entregados(modulo: RetirosModule, contexto: dict) -> None:
    modulo.registrar_ingreso(_datos(contexto, destinatario="Activo"))
    _registrar_y_entregar(modulo, contexto, "Entregado", date.today())

    historial = modulo.listar_historial()

    assert len(historial) == 1
    assert historial[0]["nombre_destinatario"] == "Entregado"


def test_historial_filtra_por_rango_de_fecha(modulo: RetirosModule, contexto: dict) -> None:
    hoy = date.today()
    _registrar_y_entregar(modulo, contexto, "Hoy", hoy)
    _registrar_y_entregar(modulo, contexto, "Hace 10 dias", hoy - timedelta(days=10))
    _registrar_y_entregar(modulo, contexto, "Hace 60 dias", hoy - timedelta(days=60))

    historial = modulo.listar_historial(
        fecha_desde=hoy - timedelta(days=30),
        fecha_hasta=hoy,
    )

    nombres = {p["nombre_destinatario"] for p in historial}
    assert nombres == {"Hoy", "Hace 10 dias"}


def test_historial_filtra_por_pyme(dal: DAL, modulo: RetirosModule) -> None:
    badtrip = dal.crear_pyme("BADTRIP")
    nixamala = dal.crear_pyme("NIXAMALA")
    personal_id = dal.crear_personal("Cajero", "cajero")
    ctx_a = {"pyme_id": badtrip, "personal_id": personal_id}
    ctx_b = {"pyme_id": nixamala, "personal_id": personal_id}
    _registrar_y_entregar(modulo, ctx_a, "Cliente BADTRIP", date.today())
    _registrar_y_entregar(modulo, ctx_b, "Cliente NIXAMALA", date.today())

    historial = modulo.listar_historial(pyme_id=badtrip)

    assert len(historial) == 1
    assert historial[0]["nombre_destinatario"] == "Cliente BADTRIP"


def test_historial_filtra_por_busqueda(modulo: RetirosModule, contexto: dict) -> None:
    _registrar_y_entregar(modulo, contexto, "Alejandro Jara", date.today())
    _registrar_y_entregar(modulo, contexto, "Carolina Silva", date.today())

    historial = modulo.listar_historial(busqueda="ale")

    assert len(historial) == 1
    assert historial[0]["nombre_destinatario"] == "Alejandro Jara"


def test_historial_combina_filtros(dal: DAL, modulo: RetirosModule) -> None:
    badtrip = dal.crear_pyme("BADTRIP")
    nixamala = dal.crear_pyme("NIXAMALA")
    personal_id = dal.crear_personal("Cajero", "cajero")
    ctx_a = {"pyme_id": badtrip, "personal_id": personal_id}
    ctx_b = {"pyme_id": nixamala, "personal_id": personal_id}
    hoy = date.today()

    _registrar_y_entregar(modulo, ctx_a, "Ana", hoy)
    _registrar_y_entregar(modulo, ctx_a, "Ana vieja", hoy - timedelta(days=60))
    _registrar_y_entregar(modulo, ctx_b, "Ana otra", hoy)

    historial = modulo.listar_historial(
        fecha_desde=hoy - timedelta(days=30),
        fecha_hasta=hoy,
        pyme_id=badtrip,
        busqueda="ana",
    )

    assert len(historial) == 1
    assert historial[0]["nombre_destinatario"] == "Ana"


def test_listar_pendientes_no_incluye_entregados_despues_de_entregar(
    modulo: RetirosModule, contexto: dict
) -> None:
    activo_id = modulo.registrar_ingreso(_datos(contexto, destinatario="Activo"))
    entregado_id = modulo.registrar_ingreso(_datos(contexto, destinatario="Entregado"))
    modulo.marcar_entregado(entregado_id)

    pendientes = modulo.listar_pendientes()

    assert [p["id"] for p in pendientes] == [activo_id]
