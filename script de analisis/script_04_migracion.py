"""Migración histórica desde los Excel del cliente hacia la BD nueva.

Migra:
  - PUNTO_DE_ENTREGA.xlsx (hojas 'entregas viejas' y 'entregas 2025') → paquetes
  - TOTAL_ABRIL_2026.xlsx (hoja 'Hoja 1')                              → caja_diaria

Filas que no cumplen los CHECK/NOT NULL del schema se descartan y se vuelcan a
historico_legacy como JSON con el motivo, para que queden auditables.

Uso:
    python script_04_migracion.py              # ejecuta la migración real
    python script_04_migracion.py --dry-run    # simula, no escribe nada

Idempotencia: el script revisa duplicados aproximados antes de insertar
(misma fecha + destinatario + pyme para paquetes; misma fecha para caja).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.dal import DAL  # noqa: E402

EXCEL_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT / "src" / "db" / "cuarto_ambulante.db"
SCHEMA_PATH = ROOT / "src" / "db" / "schema.sql"

UBICACIONES_VALIDAS = {f"{l}{n}" for l in "ABC" for n in range(1, 4)}
RE_UBICACION = re.compile(r"^[ABC][1-3]$")


def normalizar_pyme(nombre: str | None) -> str:
    return (nombre or "").strip().lower()


def construir_indice_pymes(dal: DAL) -> dict[str, int]:
    return {normalizar_pyme(p["nombre"]): p["id"] for p in dal.listar_pymes(solo_activas=False)}


def construir_indice_personal(dal: DAL) -> dict[str, int]:
    return {normalizar_pyme(p["nombre_display"]): p["id"] for p in dal.listar_personal(solo_activos=False)}


def obtener_o_crear_personal(dal: DAL, indice: dict[str, int], nombre: str | None, dry_run: bool) -> int | None:
    clave = normalizar_pyme(nombre)
    if not clave:
        return None
    if clave in indice:
        return indice[clave]
    if dry_run:
        # En dry-run inventamos un id placeholder negativo para no chocar luego.
        nuevo_id = -(len(indice) + 1)
    else:
        nuevo_id = dal.crear_personal(nombre.strip(), "cajero", 1)
    indice[clave] = nuevo_id
    return nuevo_id


def parsear_ubicacion(descripcion: Any) -> tuple[str, str | None]:
    """Devuelve (ubicacion_bodega, descripcion_restante)."""
    if descripcion is None:
        return "A1", None
    texto = str(descripcion).strip()
    if not texto:
        return "A1", None
    candidato = texto.upper()
    if RE_UBICACION.match(candidato):
        return candidato, None
    # Si el primer token es una ubicación válida, lo extraemos.
    partes = texto.split(None, 1)
    primero = partes[0].upper()
    if RE_UBICACION.match(primero):
        resto = partes[1].strip() if len(partes) > 1 else None
        return primero, resto
    return "A1", texto[:150]


def parsear_pago(valor: Any) -> str:
    texto = str(valor or "").strip().lower()
    if texto.startswith("pagado"):
        return "pagado"
    return "por_cobrar"


def parsear_fecha(valor: Any) -> str | None:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    try:
        parsed = pd.to_datetime(valor, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date().isoformat()
    except (ValueError, TypeError):
        return None


def existe_paquete(dal: DAL, fecha: str, destinatario: str, pyme_id: int) -> bool:
    paquetes = dal.listar_paquetes(pyme_remitente_id=pyme_id)
    objetivo = destinatario.strip().lower()
    return any(
        p["fecha_llegada"] == fecha and (p["nombre_destinatario"] or "").strip().lower() == objetivo
        for p in paquetes
    )


def registrar_legacy(dal: DAL, fuente: str, payload: dict, motivo: str, dry_run: bool) -> None:
    if dry_run:
        return
    dal.crear_historico_legacy(fuente=fuente, payload=json.dumps(payload, default=str, ensure_ascii=False), motivo=motivo)


def migrar_paquetes(dal: DAL, archivo: Path, dry_run: bool) -> dict[str, int]:
    stats = {"insertados": 0, "duplicados": 0, "descartados": 0}
    if not archivo.exists():
        print(f"  [omitido] {archivo.name} no encontrado")
        return stats

    wb = openpyxl.load_workbook(archivo, data_only=True)
    hojas_objetivo = [s for s in wb.sheetnames if "entrega" in s.lower()]

    pymes = construir_indice_pymes(dal)
    personal = construir_indice_personal(dal)

    columnas = [
        "numero", "fecha_llegada", "quien_trajo", "info_extra",
        "quien_retira", "info_extra2", "pagado", "descripcion",
        "quien_recibio", "estado",
    ]

    for hoja in hojas_objetivo:
        print(f"  hoja: {hoja}")
        df = pd.read_excel(archivo, sheet_name=hoja, header=0, usecols=range(10))
        df.columns = columnas

        for idx, fila in df.iterrows():
            payload = {k: (None if pd.isna(v) else v) for k, v in fila.items()}

            fecha = parsear_fecha(payload["fecha_llegada"])
            destinatario = (str(payload["quien_retira"]).strip() if payload["quien_retira"] else "")
            pyme_id = pymes.get(normalizar_pyme(payload["quien_trajo"]))

            if not fecha or not destinatario or pyme_id is None:
                stats["descartados"] += 1
                motivo = []
                if not fecha:
                    motivo.append("fecha inválida")
                if not destinatario:
                    motivo.append("sin destinatario")
                if pyme_id is None:
                    motivo.append(f"pyme '{payload['quien_trajo']}' no registrada")
                registrar_legacy(dal, f"paquetes:{hoja}:{idx}", payload, "; ".join(motivo), dry_run)
                continue

            if existe_paquete(dal, fecha, destinatario, pyme_id):
                stats["duplicados"] += 1
                continue

            recibido_por = obtener_o_crear_personal(dal, personal, payload.get("quien_recibio") or payload.get("estado"), dry_run)
            if recibido_por is None or recibido_por < 0 and not dry_run:
                stats["descartados"] += 1
                registrar_legacy(dal, f"paquetes:{hoja}:{idx}", payload, "sin personal receptor", dry_run)
                continue

            ubicacion, descripcion_resto = parsear_ubicacion(payload.get("descripcion"))
            descripcion_final = descripcion_resto

            datos_insert = dict(
                fecha_llegada=fecha,
                pyme_remitente_id=pyme_id,
                nombre_destinatario=destinatario,
                ubicacion_bodega=ubicacion,
                estado_pago=parsear_pago(payload["pagado"]),
                recibido_por=recibido_por,
                descripcion=descripcion_final,
                estado="activo",
            )

            if dry_run:
                stats["insertados"] += 1
                continue

            try:
                dal.crear_paquete(**datos_insert)
                stats["insertados"] += 1
            except Exception as exc:
                stats["descartados"] += 1
                registrar_legacy(dal, f"paquetes:{hoja}:{idx}", payload, f"insert falló: {exc}", dry_run)

    return stats


def migrar_caja_abril(dal: DAL, archivo: Path, dry_run: bool) -> dict[str, int]:
    stats = {"insertados": 0, "duplicados": 0, "descartados": 0}
    if not archivo.exists():
        print(f"  [omitido] {archivo.name} no encontrado")
        return stats

    df = pd.read_excel(archivo, sheet_name="Hoja 1", header=0)
    df.columns = df.columns.str.strip()
    df_num = df[pd.to_numeric(df.iloc[:, 0], errors="coerce").notna()].copy()

    anio, mes = 2026, 4
    for _, fila in df_num.iterrows():
        try:
            dia = int(fila.iloc[0])
            fecha = date(anio, mes, dia).isoformat()
        except (ValueError, TypeError):
            stats["descartados"] += 1
            continue

        total_real = pd.to_numeric(fila.get("TOTAL REAL"), errors="coerce")
        iva = pd.to_numeric(fila.get("IVA"), errors="coerce")
        sumup = pd.to_numeric(fila.get("SUMUP"), errors="coerce")
        if pd.isna(total_real):
            stats["descartados"] += 1
            continue

        total_real, iva, sumup = int(total_real), int(iva or 0), int(sumup or 0)
        efectivo = max(total_real - sumup, 0)

        if dal.obtener_caja_diaria(fecha) is not None:
            stats["duplicados"] += 1
            continue

        if dry_run:
            stats["insertados"] += 1
            continue

        dal.crear_caja_diaria(
            fecha=fecha,
            caja_inicial=0,
            total_efectivo=efectivo,
            total_sumup=sumup,
            total_iva=iva,
            comision_sumup_total=int(round(sumup * 0.0175)),
            caja_final_esperada=efectivo,
            diferencia=0,
            cerrada=1,
            comentario="Migrado desde TOTAL_ABRIL_2026.xlsx",
        )
        stats["insertados"] += 1

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Migración histórica de Excel a BD.")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin escribir en la BD.")
    args = parser.parse_args()

    dal = DAL(db_path=DB_PATH)
    dal.inicializar(SCHEMA_PATH)

    print("=" * 60)
    print(f"MIGRACIÓN HISTÓRICA{'  [DRY-RUN]' if args.dry_run else ''}")
    print(f"DB: {DB_PATH}")
    print("=" * 60)

    print("\n[1/2] Paquetes (PUNTO_DE_ENTREGA.xlsx)")
    s_paq = migrar_paquetes(dal, EXCEL_DIR / "PUNTO_DE_ENTREGA.xlsx", args.dry_run)
    print(f"      insertados={s_paq['insertados']}  duplicados={s_paq['duplicados']}  descartados={s_paq['descartados']}")

    print("\n[2/2] Caja diaria abril (TOTAL_ABRIL_2026.xlsx)")
    s_caj = migrar_caja_abril(dal, EXCEL_DIR / "TOTAL_ABRIL_2026.xlsx", args.dry_run)
    print(f"      insertados={s_caj['insertados']}  duplicados={s_caj['duplicados']}  descartados={s_caj['descartados']}")

    print("\n" + "=" * 60)
    print("Migración finalizada.")
    if args.dry_run:
        print("Nada se escribió en la BD. Quita --dry-run para aplicar.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
