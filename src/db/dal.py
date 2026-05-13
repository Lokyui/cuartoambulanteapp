from __future__ import annotations

import sqlite3
import calendar
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
            self._aplicar_migraciones(conn)

    @staticmethod
    def _fila(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row else None

    @staticmethod
    def _filas(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        return [dict(row) for row in rows]

    @staticmethod
    def _columnas_tabla(conn: sqlite3.Connection, tabla: str) -> set[str]:
        rows = conn.execute(f"PRAGMA table_info({tabla})").fetchall()
        return {str(row["name"]) for row in rows}

    def _aplicar_migraciones(self, conn: sqlite3.Connection) -> None:
        columnas_caja = self._columnas_tabla(conn, "caja_diaria")
        if "comentario" not in columnas_caja:
            conn.execute(
                "ALTER TABLE caja_diaria "
                "ADD COLUMN comentario TEXT CHECK (LENGTH(comentario) <= 200)"
            )

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

    def reporte_mensual(self, anio: int, mes: int) -> list[dict[str, Any]]:
        """
        Devuelve una fila por pyme con los totales del mes indicado.
        Solo incluye pymes que tuvieron al menos una venta en el período.
        Resultado ordenado por total_bruto DESC.
        """
        # Construir rango de fechas del mes
        import calendar
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fecha_desde = f"{anio}-{mes:02d}-01"
        fecha_hasta = f"{anio}-{mes:02d}-{ultimo_dia:02d}"
 
        sql = """
            SELECT
                p.nombre,
                COALESCE(SUM(CASE WHEN v.metodo = 'efectivo' THEN v.total ELSE 0 END), 0)
                    AS efectivo,
                COALESCE(SUM(CASE WHEN v.metodo = 'sumup'    THEN v.total ELSE 0 END), 0)
                    AS sumup,
                COALESCE(SUM(v.total), 0)
                    AS total_bruto,
                COALESCE(SUM(v.iva), 0)
                    AS iva,
                COALESCE(SUM(COALESCE(v.comision_sumup, 0)), 0)
                    AS comision_sumup,
                COALESCE(SUM(v.total), 0)
                    - COALESCE(SUM(v.iva), 0)
                    - COALESCE(SUM(COALESCE(v.comision_sumup, 0)), 0)
                    AS neto,
                COUNT(v.id)
                    AS n_ventas
            FROM pymes p
            INNER JOIN ventas v
                ON v.pyme_id = p.id
               AND v.fecha BETWEEN ? AND ?
            GROUP BY p.id, p.nombre
            ORDER BY total_bruto DESC
        """
        with self.conexion() as conn:
            rows = conn.execute(sql, (fecha_desde, fecha_hasta)).fetchall()
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

    def crear_venta_item(
        self,
        venta_id: int,
        producto: str,
        precio: int,
        cantidad: int,
        subtotal: int | None = None,
    ) -> int:
        subtotal_calc = subtotal if subtotal is not None else precio * cantidad
        with self.conexion() as conn:
            cur = conn.execute(
                """
                INSERT INTO venta_items
                (venta_id, producto, precio, cantidad, subtotal)
                VALUES (?, ?, ?, ?, ?)
                """,
                (venta_id, producto, precio, cantidad, subtotal_calc),
            )
            return int(cur.lastrowid)

    def obtener_venta_item(self, item_id: int) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT * FROM venta_items WHERE id = ?",
                (item_id,),
            ).fetchone()
            return self._fila(row)

    def listar_venta_items(self, venta_id: int) -> list[dict[str, Any]]:
        with self.conexion() as conn:
            rows = conn.execute(
                "SELECT * FROM venta_items WHERE venta_id = ? ORDER BY id ASC",
                (venta_id,),
            ).fetchall()
            return self._filas(rows)

    def actualizar_venta_item(self, item_id: int, datos: dict[str, Any]) -> bool:
        permitidos = {"producto", "precio", "cantidad", "subtotal"}
        cambios = {k: v for k, v in datos.items() if k in permitidos}
        if not cambios:
            return False

        if "subtotal" not in cambios and ("precio" in cambios or "cantidad" in cambios):
            actual = self.obtener_venta_item(item_id)
            if actual is None:
                return False
            precio = int(cambios.get("precio", actual["precio"]))
            cantidad = int(cambios.get("cantidad", actual["cantidad"]))
            cambios["subtotal"] = precio * cantidad

        set_sql = ", ".join(f"{col} = ?" for col in cambios)
        params = [*cambios.values(), item_id]

        with self.conexion() as conn:
            cur = conn.execute(f"UPDATE venta_items SET {set_sql} WHERE id = ?", params)
            return cur.rowcount > 0

    def eliminar_venta_item(self, item_id: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM venta_items WHERE id = ?", (item_id,))
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
        comentario: str | None = None,
    ) -> int:
        with self.conexion() as conn:
            cur = conn.execute(
                """
                INSERT INTO caja_diaria
                (
                    fecha, caja_inicial, total_efectivo, total_sumup, total_iva,
                    comision_sumup_total, caja_final_esperada, caja_final_real, diferencia, cerrada, comentario
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    comentario,
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
            "comentario",
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
        
    def obtener_detalle_reporte_pyme(self, pyme_id: int, fecha_desde: str, fecha_hasta: str) -> dict[str, Any]:
        """
        Obtiene el listado de ventas detallado y los totales agregados 
        para una PYME específica en un rango de fechas.
        """
        # 1. Obtener el listado para la tabla
        sql_detalle = """
            SELECT fecha, articulo, valor, cantidad, total, iva, 
                   COALESCE(comision_sumup, 0) as comision_sumup, metodo, comentario
            FROM ventas
            WHERE pyme_id = ? AND fecha BETWEEN ? AND ?
            ORDER BY fecha ASC
        """
        
        # 2. Obtener los totales para los GroupBox (Cuadros de colores)
        sql_totales = """
            SELECT 
                COUNT(id) as n_ventas,
                SUM(CASE WHEN metodo = 'efectivo' THEN total ELSE 0 END) as total_efectivo,
                SUM(CASE WHEN metodo = 'sumup' THEN total ELSE 0 END) as total_sumup,
                SUM(iva) as total_iva,
                SUM(COALESCE(comision_sumup, 0)) as total_comision,
                SUM(total) - SUM(iva) - SUM(COALESCE(comision_sumup, 0)) as neto_liquidar
            FROM ventas
            WHERE pyme_id = ? AND fecha BETWEEN ? AND ?
        """
        
        with self.conexion() as conn:
            detalle = self._filas(conn.execute(sql_detalle, (pyme_id, fecha_desde, fecha_hasta)).fetchall())
            totales = self._fila(conn.execute(sql_totales, (pyme_id, fecha_desde, fecha_hasta)).fetchone())
            
        return {
            "detalle": detalle,
            "resumen": totales if totales["n_ventas"] > 0 else {
                "n_ventas": 0, "total_efectivo": 0, "total_sumup": 0, 
                "total_iva": 0, "total_comision": 0, "neto_liquidar": 0
            }
        }

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

        sql = """
            SELECT
                paquetes.*,
                pymes.nombre AS nombre_pyme
            FROM paquetes
            LEFT JOIN pymes
                ON paquetes.pyme_remitente_id = pymes.id
        """

        where: list[str] = []
        params: list[Any] = []

        if estado is not None:
            where.append("paquetes.estado = ?")
            params.append(estado)

        if estado_pago is not None:
            where.append("paquetes.estado_pago = ?")
            params.append(estado_pago)

        if pyme_remitente_id is not None:
            where.append("paquetes.pyme_remitente_id = ?")
            params.append(pyme_remitente_id)

        if where:
            sql += " WHERE " + " AND ".join(where)

        sql += " ORDER BY paquetes.fecha_llegada DESC, paquetes.id DESC"

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

    def crear_historico_legacy(
        self,
        fuente: str,
        payload: str,
        motivo: str | None = None,
        creado_en: str | None = None,
    ) -> int:
        with self.conexion() as conn:
            if creado_en is None:
                cur = conn.execute(
                    """
                    INSERT INTO historico_legacy (fuente, payload, motivo)
                    VALUES (?, ?, ?)
                    """,
                    (fuente, payload, motivo),
                )
            else:
                cur = conn.execute(
                    """
                    INSERT INTO historico_legacy (fuente, payload, motivo, creado_en)
                    VALUES (?, ?, ?, ?)
                    """,
                    (fuente, payload, motivo, creado_en),
                )
            return int(cur.lastrowid)

    def obtener_historico_legacy(self, historico_id: int) -> dict[str, Any] | None:
        with self.conexion() as conn:
            row = conn.execute(
                "SELECT * FROM historico_legacy WHERE id = ?",
                (historico_id,),
            ).fetchone()
            return self._fila(row)

    def listar_historico_legacy(
        self,
        limite: int = 100,
        fuente: str | None = None,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM historico_legacy"
        params: list[Any] = []
        if fuente is not None:
            sql += " WHERE fuente = ?"
            params.append(fuente)
        sql += " ORDER BY creado_en DESC, id DESC LIMIT ?"
        params.append(int(limite))

        with self.conexion() as conn:
            rows = conn.execute(sql, params).fetchall()
            return self._filas(rows)

    def eliminar_historico_legacy(self, historico_id: int) -> bool:
        with self.conexion() as conn:
            cur = conn.execute("DELETE FROM historico_legacy WHERE id = ?", (historico_id,))
            return cur.rowcount > 0
           
           
 
    # ──────────────────────────────────────────────────────────────────────────
    # Reportes
    # ──────────────────────────────────────────────────────────────────────────
 
    def reporte_mensual(self, anio: int, mes: int) -> list[dict[str, Any]]:
        """
        Devuelve una fila por pyme con los totales agregados del mes indicado.
 
        Cada dict contiene:
            nombre          str   — nombre de la pyme
            efectivo        int   — suma de ventas en efectivo
            sumup           int   — suma de ventas con SumUp
            total_bruto     int   — efectivo + sumup
            iva             int   — suma de IVA del período
            comision_sumup  int   — suma de comisiones SumUp (0 si no aplica)
            neto            int   — total_bruto - iva - comision_sumup
            n_ventas        int   — cantidad de registros de ventas
 
        Solo incluye pymes con al menos una venta en el período.
        Resultado ordenado por total_bruto DESC.
        """
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fecha_desde = f"{anio}-{mes:02d}-01"
        fecha_hasta = f"{anio}-{mes:02d}-{ultimo_dia:02d}"
 
        sql = """
            SELECT
                p.nombre,
                COALESCE(SUM(CASE WHEN v.metodo = 'efectivo'
                                  THEN v.total ELSE 0 END), 0)   AS efectivo,
                COALESCE(SUM(CASE WHEN v.metodo = 'sumup'
                                  THEN v.total ELSE 0 END), 0)   AS sumup,
                COALESCE(SUM(v.total), 0)                        AS total_bruto,
                COALESCE(SUM(v.iva), 0)                          AS iva,
                COALESCE(SUM(COALESCE(v.comision_sumup, 0)), 0)  AS comision_sumup,
                COALESCE(SUM(v.total), 0)
                    - COALESCE(SUM(v.iva), 0)
                    - COALESCE(SUM(COALESCE(v.comision_sumup, 0)), 0)
                                                                 AS neto,
                COUNT(v.id)                                      AS n_ventas
            FROM pymes p
            INNER JOIN ventas v
                ON  v.pyme_id = p.id
                AND v.fecha BETWEEN ? AND ?
            GROUP BY p.id, p.nombre
            ORDER BY total_bruto DESC
        """
        with self.conexion() as conn:
            rows = conn.execute(sql, (fecha_desde, fecha_hasta)).fetchall()
            return self._filas(rows)

