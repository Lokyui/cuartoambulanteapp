import pandas as pd
from datetime import datetime

print("=" * 60)
print("ANALISIS VENTAS CONSOLIDADAS — TOTAL_ABRIL_2026.xlsx")
print(f"Ejecutado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 60)

try:
    df = pd.read_excel("TOTAL_ABRIL_2026.xlsx", sheet_name="Hoja 1", header=0)
    df.columns = df.columns.str.strip()

    # Separar filas numericas (dias reales) de feriados
    df_num = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notna()].copy()
    df_feriado = df[df["TOTAL REAL"] == "FERIADO"]

    print(f"\nDias con registro numerico : {len(df_num)}")
    print(f"Dias marcados como FERIADO : {len(df_feriado)}")

    # ── Ventas por pyme ────────────────────────────────────────────
    pymes = [
        "BADTRIP", "NIXAMALA", "SAIHOU", "TERNUROI", "CLAU", "CUARTO",
        "MILEN", "ZERODOS", "TITEREMANIA", "TENSHI", "CHILL", "LOSTO", "DULCE"
    ]
    pymes_ok = [p for p in pymes if p in df_num.columns]

    print(f"\nVENTAS TOTALES POR PYME (abril 2026):")
    totales = {}
    for p in pymes_ok:
        total = pd.to_numeric(df_num[p], errors="coerce").sum()
        totales[p] = total

    for p, t in sorted(totales.items(), key=lambda x: -x[1]):
        bar = "█" * int(t / 15000)
        print(f"  {p:<14} ${t:>12,.0f}  {bar}")

    # ── Resumen caja ───────────────────────────────────────────────
    total_real = pd.to_numeric(df_num["TOTAL REAL"], errors="coerce").sum()
    total_iva  = pd.to_numeric(df_num["IVA"], errors="coerce").sum()
    total_sup  = pd.to_numeric(df_num["SUMUP"], errors="coerce").sum()
    total_neto = total_real - total_iva - total_sup

    print(f"\nRESUMEN CAJA TOTAL ABRIL:")
    print(f"  Total ventas brutas : ${total_real:>12,.0f}")
    print(f"  Total IVA           : ${total_iva:>12,.0f}")
    print(f"  Total SumUp         : ${total_sup:>12,.0f}")
    print(f"  Total neto (sin IVA/SumUp): ${total_neto:>8,.0f}")

    # ── Promedio diario ────────────────────────────────────────────
    if len(df_num) > 0:
        promedio = total_real / len(df_num)
        print(f"\n  Promedio diario de ventas : ${promedio:>10,.0f}")

except FileNotFoundError:
    print("\n[ERROR] No se encontro TOTAL_ABRIL_2026.xlsx")
    print("  Verifica que el script este en la misma carpeta que los .xlsx")

print("\n" + "=" * 60)
print("Script 3 finalizado.")
print("=" * 60)