from __future__ import annotations

from datetime import date, datetime

from db.dal import DAL


def test_crear_paquete_con_fecha_entrega(dal: DAL) -> None:
    pyme_id = dal.crear_pyme("Pyme Test")
    personal_id = dal.crear_personal("Juan Perez", "cajero")

    entrega = datetime.now()
    paquete_id = dal.crear_paquete(
        date.today(),
        pyme_id,
        "Destinatario",
        "A1",
        "pagado",
        personal_id,
        entregado_por="Juan Perez",
        fecha_entrega=entrega,
        estado="entregado",
        descripcion="OK",
    )

    paquete = dal.obtener_paquete(paquete_id)
    assert paquete is not None
    assert paquete["fecha_entrega"] is not None
