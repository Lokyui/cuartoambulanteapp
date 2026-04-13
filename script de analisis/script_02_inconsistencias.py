import pandas as pd
from datetime import datetime

print("=" * 60)
print("DETECCION DE INCONSISTENCIAS — PUNTO_DE_ENTREGA.xlsx")
print(f"Ejecutado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 60)

try:
    df = pd.read_excel(
        "PUNTO_DE_ENTREGA.xlsx",
        sheet_name="entregas viejas",
        header=0,
        usecols=range(10)
    )
    df.columns = [
        "numero", "fecha_llegada", "quien_trajo", "info_extra",
        "quien_retira", "info_extra2", "pagado", "descripcion",
        "quien_recibio", "estado"
    ]

    total = len(df)
    print(f"\nTotal de registros analizados : {total}")

    # ── Campos vacios ──────────────────────────────────────────────
    print(f"\nCAMPOS VACIOS POR COLUMNA:")
    for col in df.columns:
        nulls = df[col].isna().sum()
        pct = (nulls / total) * 100
        bar = "█" * int(pct / 5)
        print(f"  {col:<18} {nulls:>4} vacios  ({pct:5.1f}%)  {bar}")

    # ── Codigos de descripcion ─────────────────────────────────────
    print(f"\nCODIGOS DESCRIPCION (sin texto legible):")
    codigos = df["descripcion"].dropna().unique()
    muestra = [c for c in codigos if isinstance(c, str) and len(c) <= 5][:15]
    print(f"  {muestra}")

    # ── Inconsistencias en campo 'estado' ──────────────────────────
    print(f"\nVALORES EN CAMPO 'estado' (quien recibio el paquete):")
    for estado, cnt in df["estado"].value_counts().items():
        alerta = " ← posible duplicado o error tipografico" if str(estado).strip().lower() in [
            str(e).strip().lower() for e in df["estado"].value_counts().index
            if str(e).strip() != str(estado).strip() and
            str(e).strip().lower() == str(estado).strip().lower()
        ] else ""
        print(f"  '{estado}': {cnt} registros{alerta}")

    # ── Resumen de inconsistencias detectadas ──────────────────────
    print(f"\nINCONSISTENCIAS DETECTADAS (mismo nombre, escritura diferente):")
    nombres = df["estado"].dropna().astype(str).str.strip()
    grupos = nombres.str.lower().value_counts()
    for nombre_lower, total_variantes in grupos.items():
        variantes = nombres[nombres.str.lower() == nombre_lower].unique()
        if len(variantes) > 1:
            print(f"  '{nombre_lower}' → variantes encontradas: {list(variantes)}")

except FileNotFoundError:
    print("\n[ERROR] No se encontro PUNTO_DE_ENTREGA.xlsx")
    print("  Verifica que el script este en la misma carpeta que los .xlsx")

print("\n" + "=" * 60)
print("Script 2 finalizado.")
print("=" * 60)