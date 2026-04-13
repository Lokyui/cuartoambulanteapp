# Como utilizar los scripts de analisis

## Requisitos
- Tener Python 3 instalado.
- Instalar dependencias una sola vez:

```bash
pip install pandas openpyxl
```

## Ubicacion y ejecucion
Estos scripts deben ejecutarse dentro de la misma carpeta donde se encuentran los archivos Excel, porque estos leen archivos Excel por nombre directo.

### 1) Entrar a la carpeta
En PowerShell:

```powershell
cd "script de analisis"
```

### 2) Ejecutar cada script por separado

```powershell
python script_01_estructura.py
python script_02_inconsistencias.py
python script_03_ventas.py
```

## Que hace cada script

### script_01_estructura.py
- Analiza la estructura de los archivos:
  - `PLANTILLA.xlsx`
  - `TOTAL_ABRIL_2026.xlsx`
  - `PUNTO_DE_ENTREGA.xlsx`
- Muestra:
  - numero de hojas por archivo,
  - nombres de hojas,
  - cantidad de filas con datos y columnas por hoja.

### script_02_inconsistencias.py
- Analiza `PUNTO_DE_ENTREGA.xlsx`, hoja `entregas viejas`.
- Detecta:
  - campos vacios por columna,
  - codigos cortos en `descripcion`,
  - posibles inconsistencias de escritura en el campo `estado`.

### script_03_ventas.py
- Analiza `TOTAL_ABRIL_2026.xlsx`, hoja `Hoja 1`.
- Calcula:
  - dias con datos y dias feriados,
  - ventas totales por pyme,
  - resumen de caja (TOTAL REAL, IVA, SUMUP, neto),
  - promedio diario de ventas.

## Errores comunes

### Error: archivo no encontrado
- Asegurate de ejecutar desde la carpeta con los archivos.
- Verifica que existan estos archivos:
  - `PLANTILLA.xlsx`
  - `PUNTO_DE_ENTREGA.xlsx`
  - `TOTAL_ABRIL_2026.xlsx`