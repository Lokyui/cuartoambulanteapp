from __future__ import annotations

from db.dal import DAL


def test_registro_rechazos_historico_legacy(dal: DAL) -> None:
    rechazo_id = dal.crear_rechazo_legacy(
        fuente="PUNTO_DE_ENTREGA.xlsx:entregas 2025",
        payload="{\"numero\": \"\", \"motivo\": \"sin numero\"}",
        motivo="sin numero",
    )

    assert rechazo_id > 0

    rechazos = dal.listar_rechazos_legacy()
    assert len(rechazos) == 1
    assert rechazos[0]["motivo"] == "sin numero"
