from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any, Iterator


def _to_fecha(valor: str | date) -> str:
    if isinstance(valor, date):
        return valor.isoformat()
    return str(valor)


class DAL:
    def __init__(self, db_path: str | Path | None = None) -> None:
        base = Path(__file__).resolve().parent
        self.db_path = Path(db_path) if db_path else base / "cuarto_ambulante.db"
        self.schema_path = base / "schema.sql"

    @contextmanager
    def conexion(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def inicializar(self, schema_path: str | Path | None = None) -> None:
        path = Path(schema_path) if schema_path else self.schema_path
        sql = path.read_text(encoding="utf-8")
        with self.conexion() as conn:
            conn.executescript(sql)

    @staticmethod
    def _fila(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row else None

    @staticmethod
    def _filas(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        return [dict(row) for row in rows]

    def crear_pyme(self, nombre: str, activa: int = 1) -> int:
        with self.conexion() as conn:
            cur = conn.execute(
                "INSERT INTO pymes (nombre, activa) VALUES (?, ?)",
                (nombre, activa),
            )
            return int(cur.lastrowid)

    def obtener_pyme(self, pyme_id: int) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT id, nombre, activa FROM pymes WHERE id = ?",
                (pyme_id,),
            ).fetchone()
            return self._fila(row)

    def listar_pymes(self, solo_activas: bool = True) -> list[dict[str, Any]]:
        sql = "SELECT id, nombre, activa FROM pymes"
        params: list[Any] = []
        if solo_activas:
            sql += " WHERE activa = 1"
        sql += " ORDER BY nombre COLLATE NOCASE"
        with self.conexion() as conn:
            rows = conn.execute(sql, params).fetchall()
            return self._filas(rows)

    def actualizar_pyme(self, pyme_id: int, nombre: str, activa: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute(
                "UPDATE pymes SET nombre = ?, activa = ? WHERE id = ?",
                (nombre, activa, pyme_id),
            )
            return cur.rowcount > 0

    def eliminar_pyme(self, pyme_id: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM pymes WHERE id = ?", (pyme_id,))
            return cur.rowcount > 0

    def crear_personal(self, nombre_display: str, rol: str, activo: int = 1) -> int:
        with self.conexion() as conn:
            cur = conn.execute(
                "INSERT INTO personal (nombre_display, rol, activo) VALUES (?, ?, ?)",
                (nombre_display, rol, activo),
            )
            return int(cur.lastrowid)

    def obtener_personal(self, personal_id: int) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT id, nombre_display, rol, activo FROM personal WHERE id = ?",
                (personal_id,),
            ).fetchone()
            return self._fila(row)

    def listar_personal(self, solo_activos: bool = True) -> list[dict[str, Any]]:
        sql = "SELECT id, nombre_display, rol, activo FROM personal"
        if solo_activos:
            sql += " WHERE activo = 1"
        sql += " ORDER BY nombre_display COLLATE NOCASE"
        with self.conexion() as conn:
            rows = conn.execute(sql).fetchall()
            return self._filas(rows)

    def actualizar_personal(
        self,
        personal_id: int,
        nombre_display: str,
        rol: str,
        activo: int,
    ) -> bool:
        with self.conexion() as conn:
            cur = conn.execute(
                "UPDATE personal SET nombre_display = ?, rol = ?, activo = ? WHERE id = ?",
                (nombre_display, rol, activo, personal_id),
            )
            return cur.rowcount > 0

    def eliminar_personal(self, personal_id: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM personal WHERE id = ?", (personal_id,))
            return cur.rowcount > 0

    def crear_venta(
        self,
        fecha: str | date,
        pyme_id: int,
        articulo: str | None,
        valor: int,
        cantidad: int,
        metodo: str,
        iva: int,
        comision_sumup: int | None,
        total: int,
        comentario: str | None = None,
    ) -> int:
        with self.conexion() as conn:
            cur = conn.execute(
                """
                INSERT INTO ventas
                (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _to_fecha(fecha),
                    pyme_id,
                    articulo,
                    valor,
                    cantidad,
                    metodo,
                    iva,
                    comision_sumup,
                    total,
                    comentario,
                ),
            )
            return int(cur.lastrowid)

    def obtener_venta(self, venta_id: int) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT * FROM ventas WHERE id = ?",
                (venta_id,),
            ).fetchone()
            return self._fila(row)

    def listar_ventas(
        self,
        fecha: str | date | None = None,
        pyme_id: int | None = None,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM ventas"
        where: list[str] = []
        params: list[Any] = []

        if fecha is not None:
            where.append("fecha = ?")
            params.append(_to_fecha(fecha))
        if pyme_id is not None:
            where.append("pyme_id = ?")
            params.append(pyme_id)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY fecha DESC, id DESC"

        with self.conexion() as conn:
            rows = conn.execute(sql, params).fetchall()
            return self._filas(rows)

    def actualizar_venta(self, venta_id: int, datos: dict[str, Any]) -> bool:
        permitidos = {
            "fecha",
            "pyme_id",
            "articulo",
            "valor",
            "cantidad",
            "metodo",
            "iva",
            "comision_sumup",
            "total",
            "comentario",
        }
        cambios = {k: v for k, v in datos.items() if k in permitidos}
        if "fecha" in cambios:
            cambios["fecha"] = _to_fecha(cambios["fecha"])
        if not cambios:
            return False

        set_sql = ", ".join(f"{col} = ?" for col in cambios)
        params = [*cambios.values(), venta_id]

        with self.conexion() as conn:
            cur = conn.execute(f"UPDATE ventas SET {set_sql} WHERE id = ?", params)
            return cur.rowcount > 0

    def eliminar_venta(self, venta_id: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
            return cur.rowcount > 0

    def crear_caja_diaria(
        self,
        fecha: str | date,
        caja_inicial: int = 0,
        total_efectivo: int = 0,
        total_sumup: int = 0,
        total_iva: int = 0,
        comision_sumup_total: int = 0,
        caja_final_esperada: int = 0,
        caja_final_real: int | None = None,
        diferencia: int = 0,
        cerrada: int = 0,
    ) -> int:
        with self.conexion() as conn:
            cur = conn.execute(
                """
                INSERT INTO caja_diaria
                (
                    fecha, caja_inicial, total_efectivo, total_sumup, total_iva,
                    comision_sumup_total, caja_final_esperada, caja_final_real, diferencia, cerrada
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _to_fecha(fecha),
                    caja_inicial,
                    total_efectivo,
                    total_sumup,
                    total_iva,
                    comision_sumup_total,
                    caja_final_esperada,
                    caja_final_real,
                    diferencia,
                    cerrada,
                ),
            )
            return int(cur.lastrowid)

    def obtener_caja_diaria(self, fecha: str | date) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT * FROM caja_diaria WHERE fecha = ?",
                (_to_fecha(fecha),),
            ).fetchone()
            return self._fila(row)

    def listar_cajas_diarias(self) -> list[dict[str, Any]]:
        with self.conexion() as conn:
            rows = conn.execute("SELECT * FROM caja_diaria ORDER BY fecha DESC").fetchall()
            return self._filas(rows)

    def actualizar_caja_diaria(self, fecha: str | date, datos: dict[str, Any]) -> bool:
        permitidos = {
            "caja_inicial",
            "total_efectivo",
            "total_sumup",
            "total_iva",
            "comision_sumup_total",
            "caja_final_esperada",
            "caja_final_real",
            "diferencia",
            "cerrada",
        }
        cambios = {k: v for k, v in datos.items() if k in permitidos}
        if not cambios:
            return False

        set_sql = ", ".join(f"{col} = ?" for col in cambios)
        params = [*cambios.values(), _to_fecha(fecha)]

        with self.conexion() as conn:
            cur = conn.execute(
                f"UPDATE caja_diaria SET {set_sql} WHERE fecha = ?",
                params,
            )
            return cur.rowcount > 0

    def eliminar_caja_diaria(self, fecha: str | date) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM caja_diaria WHERE fecha = ?", (_to_fecha(fecha),))
            return cur.rowcount > 0

    def crear_paquete(
        self,
        fecha_llegada: str | date,
        pyme_remitente_id: int,
        nombre_destinatario: str,
        ubicacion_bodega: str,
        estado_pago: str,
        recibido_por: int,
        entregado_por: str | None = None,
        fecha_entrega: str | date | None = None,
        estado: str = "activo",
        descripcion: str | None = None,
    ) -> int:
        with self.conexion() as conn:
            cur = conn.execute(
                """
                INSERT INTO paquetes
                (
                    fecha_llegada, pyme_remitente_id, nombre_destinatario, ubicacion_bodega,
                    estado_pago, recibido_por, entregado_por, fecha_entrega, estado, descripcion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _to_fecha(fecha_llegada),
                    pyme_remitente_id,
                    nombre_destinatario,
                    ubicacion_bodega,
                    estado_pago,
                    recibido_por,
                    entregado_por,
                    _to_fecha(fecha_entrega) if fecha_entrega is not None else None,
                    estado,
                    descripcion,
                ),
            )
            return int(cur.lastrowid)

    def obtener_paquete(self, paquete_id: int) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT * FROM paquetes WHERE id = ?",
                (paquete_id,),
            ).fetchone()
            return self._fila(row)

    def listar_paquetes(
        self,
        estado: str | None = None,
        estado_pago: str | None = None,
        pyme_remitente_id: int | None = None,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM paquetes"
        where: list[str] = []
        params: list[Any] = []

        if estado is not None:
            where.append("estado = ?")
            params.append(estado)
        if estado_pago is not None:
            where.append("estado_pago = ?")
            params.append(estado_pago)
        if pyme_remitente_id is not None:
            where.append("pyme_remitente_id = ?")
            params.append(pyme_remitente_id)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY fecha_llegada DESC, id DESC"

        with self.conexion() as conn:
            rows = conn.execute(sql, params).fetchall()
            return self._filas(rows)

    def actualizar_paquete(self, paquete_id: int, datos: dict[str, Any]) -> bool:
        permitidos = {
            "fecha_llegada",
            "pyme_remitente_id",
            "nombre_destinatario",
            "ubicacion_bodega",
            "estado_pago",
            "recibido_por",
            "entregado_por",
            "fecha_entrega",
            "estado",
            "descripcion",
        }
        cambios = {k: v for k, v in datos.items() if k in permitidos}
        if "fecha_llegada" in cambios:
            cambios["fecha_llegada"] = _to_fecha(cambios["fecha_llegada"])
        if "fecha_entrega" in cambios and cambios["fecha_entrega"] is not None:
            cambios["fecha_entrega"] = _to_fecha(cambios["fecha_entrega"])
        if not cambios:
            return False

        set_sql = ", ".join(f"{col} = ?" for col in cambios)
        params = [*cambios.values(), paquete_id]

        with self.conexion() as conn:
            cur = conn.execute(f"UPDATE paquetes SET {set_sql} WHERE id = ?", params)
            return cur.rowcount > 0

    def eliminar_paquete(self, paquete_id: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM paquetes WHERE id = ?", (paquete_id,))
            return cur.rowcount > 0
