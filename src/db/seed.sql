PRAGMA foreign_keys = ON;

-- Pymes
INSERT INTO pymes (nombre, activa) VALUES
('BADTRIP', 1),
('NIXAMALA', 1),
('SAIHOU', 1),
('TERNUROIDES', 1),
('STICKYCLAU', 1),
('CUARTO', 1),
('MILEN', 1),
('ZERODOS', 1),
('TITEREMANIA', 1),
('TENSHI', 1),
('CHILL', 1),
('LOSTO', 1),
('DULCE', 1);

-- Personal
INSERT INTO personal (nombre_display, rol, activo) VALUES
('Dario Less', 'socio', 1),
('Juan Perez', 'cajero', 1),
('Carolina Silva', 'cajero', 1);

-- Ventas (cabecera)
-- IVA: precio al público incluye IVA. iva = int(total / 1.19 * 0.19). 2000 -> 319.
-- Comisión SumUp: int(total * 0.0175). 2000 -> 35.
-- Ventas (cabecera)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario) VALUES
(date('now','localtime'), 1, 'Sticker holográfico', 2000, 1, 'efectivo', 319, NULL, 2000, 'Producto exclusivo'),
(date('now','localtime'), 2, 'Llavero acrílico', 1000, 2, 'sumup', 319, 35, 2000, 'Edición limitada');

-- Items de ventas
INSERT INTO venta_items (venta_id, producto, precio, cantidad, subtotal) VALUES
(1, 'Sticker holográfico', 2000, 1, 2000),
(2, 'Llavero acrílico', 1000, 2, 2000);

-- Caja diaria
-- El cierre de hoy se inserta al final de seed_ventas.sql (que carga DESPUÉS de
-- este archivo), derivado por SQL de TODAS las ventas del día. Así los totales
-- siempre cuadran con las ventas reales, sin números hardcodeados.

-- Paquetes
INSERT INTO paquetes (fecha_llegada, pyme_remitente_id, nombre_destinatario, ubicacion_bodega, estado_pago, recibido_por, entregado_por, fecha_entrega, estado, descripcion) VALUES
(date('now','localtime','-7 day'), 1, 'Alejandro Jara', 'A1', 'pagado', 2, NULL, NULL, 'activo', 'Encomienda de mercadería'),
(date('now','localtime','-17 day'), 2, 'Carolina Silva', 'B3', 'por_cobrar', 3, 'Juan Perez', datetime('now','localtime','-12 day'), 'entregado', 'Encomienda de mercadería'),
(date('now','localtime','-3 day'), 4, 'Martín Rojas', 'A2', 'pagado', 2, NULL, NULL, 'activo', 'Encomienda de mercadería'),
(date('now','localtime','-1 day'), 5, 'Valentina Soto', 'C1', 'por_cobrar', 3, NULL, NULL, 'activo', 'Encomienda de mercadería');
