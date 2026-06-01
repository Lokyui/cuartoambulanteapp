from __future__ import annotations

from datetime import date
from typing import Any

from src.db.dal import DAL


# Fórmulas oficiales (ver seed_ventas.sql y CLAUDE.md):
#   iva            = ROUND(total / 1.19 * 0.19)   — IVA incluido en el precio
#   comision_sumup = ROUND(total * 0.0175)        — solo si metodo='sumup'
IVA_DIVISOR = 1.19
IVA_FACTOR = 0.19
COMISION_SUMUP_FACTOR = 0.0175


class VentasModule:
    def __init__(self, dal: DAL):
        self.dal = dal

    def listar_pymes(self) -> list[dict[str, Any]]:
        return self.dal.listar_pymes(solo_activas=True)

    def resumen_del_dia(self, fecha: date) -> dict[str, Any]:
        ventas = self.dal.listar_ventas(fecha=fecha)
        # Incluye inactivas: los movimientos históricos deben mostrar el nombre real,
        # no aparecer como "—" si la pyme fue desactivada después.
        pymes = {p["id"]: p["nombre"] for p in self.dal.listar_pymes(solo_activas=False)}

        por_tienda: dict[str, int] = {}
        for v in ventas:
            nombre = pymes.get(v["pyme_id"], "—")
            por_tienda[nombre] = por_tienda.get(nombre, 0) + v["total"]

        recientes = [
            {**v, "pyme_nombre": pymes.get(v["pyme_id"], "—")}
            for v in ventas[:10]
        ]

        return {
            "n_ventas": len(ventas),
            "total": sum(v["total"] for v in ventas),
            "sin_comision": sum(
                v["total"] - v["iva"] - (v["comision_sumup"] or 0) for v in ventas
            ),
            "por_tienda": sorted(por_tienda.items(), key=lambda kv: -kv[1]),
            "recientes": recientes,
        }

    def calcular_totales(
        self,
        items: list[dict[str, Any]],
        metodo: str,
    ) -> dict[str, int | None]:
        if not items:
            raise ValueError("Una venta debe tener al menos un item.")

        total = 0
        for item in items:
            precio = int(item["precio"])
            cantidad = int(item["cantidad"])
            if precio <= 0 or cantidad < 1:
                raise ValueError("Precio debe ser > 0 y cantidad >= 1.")
            total += precio * cantidad

        iva = int(round(total / IVA_DIVISOR * IVA_FACTOR))
        metodo_norm = metodo.lower()
        if metodo_norm == "sumup":
            comision = int(round(total * COMISION_SUMUP_FACTOR))
        elif metodo_norm == "efectivo":
            comision = None
        else:
            raise ValueError(f"Método inválido: {metodo!r}. Debe ser 'efectivo' o 'sumup'.")

        return {"total": total, "iva": iva, "comision_sumup": comision}

    def procesar_nueva_venta(self, datos: dict[str, Any]) -> int:
        """Calcula totales y delega la inserción al DAL (transaccional).

        Espera en `datos`:
            pyme_id (int), fecha (date|str), metodo ('efectivo'|'sumup'),
            items (list[{producto, precio, cantidad}]), comentario (str, opcional)

        La derivación de `articulo`/`valor`/`cantidad` (agregados de cabecera)
        vive en el DAL — esto es solo orquestación de cálculos de negocio.
        Si la caja del día está cerrada, levanta ValueError antes de tocar la BD.
        """
        items = list(datos["items"])
        metodo = datos["metodo"]
        fecha = datos.get("fecha", date.today())
        self._verificar_caja_abierta(fecha)
        totales = self.calcular_totales(items, metodo)

        return self.dal.crear_venta(
            fecha=fecha,
            pyme_id=int(datos["pyme_id"]),
            metodo=metodo.lower(),
            iva=totales["iva"],
            comision_sumup=totales["comision_sumup"],
            total=totales["total"],
            items=items,
            comentario=datos.get("comentario") or None,
        )

    def _verificar_caja_abierta(self, fecha) -> None:
        caja = self.dal.obtener_caja_diaria(fecha)
        if caja and caja["cerrada"]:
            raise ValueError(
                "La caja del día está cerrada. Reábrela desde Cierre de caja para registrar ventas."
            )