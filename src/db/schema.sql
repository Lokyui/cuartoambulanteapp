PRAGMA foreign_keys = ON; -- Habilitar claves foraneas para asegurar la integridad referencial, usar en cada conexion a la base de datos

-- Tabla que contiene nombres de PYMES que trabajan en el local
CREATE TABLE IF NOT EXISTS pymes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL COLLATE NOCASE UNIQUE,
    activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0,1))
);

-- Tabla que tiene la informacion del personal del local
CREATE TABLE IF NOT EXISTS personal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_display TEXT NOT NULL COLLATE NOCASE UNIQUE,
    rol TEXT NOT NULL CHECK (rol IN ('socio','cajero')),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

-- Tabla que registra las ventas diarias (cabecera de transaccion)
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    pyme_id INTEGER NOT NULL REFERENCES pymes(id),
    articulo TEXT,
    valor INTEGER NOT NULL CHECK (valor > 0),
    cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad >= 1),
    metodo TEXT NOT NULL CHECK (metodo IN ('efectivo','sumup')),
    iva INTEGER NOT NULL CHECK (iva >= 0),
    comision_sumup INTEGER CHECK (comision_sumup >= 0),
    total INTEGER NOT NULL CHECK (total >= 0),
    comentario TEXT CHECK (LENGTH(comentario) <= 200),
    CHECK (
      (metodo = 'sumup' AND comision_sumup IS NOT NULL) OR
      (metodo = 'efectivo' AND comision_sumup IS NULL)
    )
);

-- Tabla de detalle de items por venta
CREATE TABLE IF NOT EXISTS venta_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto TEXT NOT NULL,
    precio INTEGER NOT NULL CHECK (precio > 0),
    cantidad INTEGER NOT NULL CHECK (cantidad >= 1),
    subtotal INTEGER NOT NULL CHECK (subtotal = precio * cantidad)
);

-- Tabla que registra el estado de la caja diaria, con detalles de ingresos, egresos y diferencias al cierre del dia
CREATE TABLE IF NOT EXISTS caja_diaria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL UNIQUE,
    caja_inicial INTEGER NOT NULL DEFAULT 0 CHECK (caja_inicial >= 0),
    total_efectivo INTEGER NOT NULL DEFAULT 0 CHECK (total_efectivo >= 0),
    total_sumup INTEGER NOT NULL DEFAULT 0 CHECK (total_sumup >= 0),
    total_iva INTEGER NOT NULL DEFAULT 0 CHECK (total_iva >= 0),
    comision_sumup_total INTEGER NOT NULL DEFAULT 0 CHECK (comision_sumup_total >= 0),
    caja_final_esperada INTEGER NOT NULL DEFAULT 0,
    caja_final_real INTEGER CHECK (caja_final_real >= 0),
    diferencia INTEGER NOT NULL DEFAULT 0,
    cerrada INTEGER NOT NULL DEFAULT 0 CHECK (cerrada IN (0,1)),
    comentario TEXT CHECK (LENGTH(comentario) <= 200)
);

-- Tabla que registra la informacion de los paquetes que llegan al local, con detalles de su estado, ubicacion y destinatarios
CREATE TABLE IF NOT EXISTS paquetes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_llegada DATE NOT NULL,
    pyme_remitente_id INTEGER NOT NULL REFERENCES pymes(id),
    nombre_destinatario TEXT NOT NULL,
    ubicacion_bodega TEXT NOT NULL CHECK (
        ubicacion_bodega IN ('A1','A2','A3','B1','B2','B3','C1','C2','C3')
    ),
    estado_pago TEXT NOT NULL CHECK (estado_pago IN ('por_cobrar','pagado')),
    recibido_por INTEGER NOT NULL REFERENCES personal(id),
    entregado_por TEXT,
    fecha_entrega DATETIME,
    estado TEXT NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo','entregado','devuelto')),
    descripcion TEXT CHECK (LENGTH(descripcion) <= 150)
);

-- Tabla de respaldo de filas legacy rechazadas durante migracion
CREATE TABLE IF NOT EXISTS historico_legacy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fuente TEXT NOT NULL,
    payload TEXT NOT NULL,
    motivo TEXT,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Creacion de indices para mayor velocidad
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_pyme ON ventas(pyme_id);
CREATE INDEX IF NOT EXISTS idx_venta_items_venta ON venta_items(venta_id);
CREATE INDEX IF NOT EXISTS idx_paquetes_estado ON paquetes(estado);
CREATE INDEX IF NOT EXISTS idx_paquetes_destinatario ON paquetes(nombre_destinatario);
CREATE INDEX IF NOT EXISTS idx_historico_legacy_creado_en ON historico_legacy(creado_en);
