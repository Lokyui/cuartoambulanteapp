# Sistema de Gestión Cuarto Ambulante

## Descripción General
Este software es una solución de escritorio diseñada para centralizar la operación comercial de Cuarto Ambulante. El sistema permite la transición de registros manuales en Excel a una base de datos relacional, facilitando el control de ventas, el seguimiento de paquetes y la generación de informes financieros para las distintas pymes que integran el espacio.

## Arquitectura del Sistema
La aplicación sigue un patrón de diseño modular basado en capas para asegurar la escalabilidad:
1. Presentación: Interfaces desarrolladas en PyQt5 (archivos .ui) y lógica de vista en Python.
2. Capa de Datos (DAL): Objeto de Acceso a Datos que centraliza las consultas SQL hacia SQLite.
3. Lógica de negocio: Cálculo de IVA, comisión SumUp, cuadratura de caja, generación de reportes. Independiente de UI y BD

## Estructura Completa del Repositorio
A continuación se detalla la organización de archivos prevista para el cierre del proyecto:

```
PROYECTO_CUARTO_AMBULANTE/
├── db/
│   ├── dal.py                 # Lógica de persistencia y consultas SQL
│   ├── database.db            # Base de datos SQLite
│   └── queries.sql            # Scripts de creación de tablas e índices
├── src/
│   ├── ui/
│   │   ├── views/             # Archivos de diseño de Qt Designer
│   │   │   ├── main_window.ui
│   │   │   ├── dashboard.ui
│   │   │   ├── ventas.ui
│   │   │   └── reportes.ui
│   │   └── resources_rc.py    # Binarios de iconos y elementos visuales
│   ├── views/                 # Controladores de la interfaz
│   │   ├── main_window.py     # Ventana principal y gestión del menú
│   │   ├── dashboard.py       # Panel de métricas diarias
│   │   ├── ventas.py          # Registro de transacciones
│   │   └── reportes.py        # Generación de reportes mensuales
│   └── utils/
│       ├── formatters.py      # Formateo de moneda y fechas en español
│       └── validators.py      # Lógica de validación de RUT y campos
├── main.py                    # Punto de entrada de la aplicación
└── requirements.txt           # Dependencias del proyecto
``` 

## Requisitos e Instalación
El sistema está optimizado para funcionar en entornos Linux (Ubuntu). 

Dependencias necesarias:
1. Python 3.9 o superior
2. PyQt5
3. SQLite3

Para configurar el entorno de desarrollo:

1. Clonar el repositorio.

2. Crear un entorno virtual. Aísla las dependencias del proyecto y evita
   instalarlas en el Python del sistema:

   ```bash
   python -m venv .venv
   ```

3. Activar el entorno virtual:

   - En Windows (PowerShell):

     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```

   - En Linux / macOS:

     ```bash
     source .venv/bin/activate
     ```

   Una vez activado, la consola muestra `(.venv)` al inicio de la línea.

4. Instalar las dependencias dentro del entorno virtual:

   ```bash
   pip install -r requirements.txt
   ```

5. Ejecutar la aplicación:

   ```bash
   python main.py
   ```

## Funcionalidades Implementadas
1. Dashboard: Resumen automatizado de ventas totales y transacciones por pyme.
2. Registro de Ventas: Formulario con soporte para múltiples métodos de pago (Efectivo y SumUp).
3. Localización: Sistema de fechas y moneda adaptado al contexto de Chile.
4. Reportes: Vista consolidada de movimientos mensuales para auditoría interna.

## Notas de Desarrollo
La base de datos utiliza integridad referencial para asegurar que cada venta esté correctamente vinculada a una pyme existente. Los nombres de los objetos en la interfaz (UI) mantienen una nomenclatura estandarizada para facilitar la vinculación con los métodos del controlador en Python.
