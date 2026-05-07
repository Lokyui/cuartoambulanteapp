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
('2026-04-27', 1, 'Producto A', 2000, 1, 'efectivo', 319, NULL, 2000, 'Venta demo'),
('2026-04-27', 2, 'Producto B', 1000, 2, 'sumup', 319, 35, 2000, 'Venta demo');

-- Items de ventas
INSERT INTO venta_items (venta_id, producto, precio, cantidad, subtotal) VALUES
(1, 'Producto A', 2000, 1, 2000),
(2, 'Producto B', 1000, 2, 2000);

-- Caja diaria
-- total_iva = SUM(iva) de ventas del día = 319 + 319 = 638
-- comision_sumup_total = SUM(comision_sumup) = 35 (solo la venta sumup)
-- caja_final_esperada = caja_inicial + total_efectivo = 5000 + 2000 = 7000
INSERT INTO caja_diaria (fecha, caja_inicial, total_efectivo, total_sumup, total_iva, comision_sumup_total, caja_final_esperada, caja_final_real, diferencia, cerrada, comentario) VALUES
('2026-04-27', 5000, 2000, 2000, 638, 35, 7000, 7000, 0, 1, 'Cierre demo');

-- Paquetes
INSERT INTO paquetes (fecha_llegada, pyme_remitente_id, nombre_destinatario, ubicacion_bodega, estado_pago, recibido_por, entregado_por, fecha_entrega, estado, descripcion) VALUES
('2026-04-20', 1, 'Alejandro Jara', 'A1', 'pagado', 2, NULL, NULL, 'activo', 'Demo'),
('2026-04-10', 2, 'Carolina Silva', 'B3', 'por_cobrar', 3, 'Juan Perez', '2026-04-15T10:30:00', 'entregado', 'Demo');
