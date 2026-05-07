-- =============================================================
-- SEED: Ventas ficticias — Badtrip (pyme_id = 1)
-- Marzo 2026 (10 registros) + Abril 2026 (10 registros)
-- Requisitos previos: que exista una fila en pymes con id = 1
-- y nombre = 'Badtrip'. Ajusta pyme_id si es distinto.
-- IVA  = ROUND(total / 1.19 * 0.19)
-- Comisión SumUp = ROUND(total * 0.0175)  — solo si metodo='sumup'
-- =============================================================
 
-- ──────────────────────────────────────────────
-- MARZO 2026
-- ──────────────────────────────────────────────
 
-- 01  Polera estampada negra x1  $18.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-03', 1, 'Polera estampada negra', 18000, 1, 'efectivo', 2874, NULL, 18000, NULL);
 
-- 02  Tote bag serigrafía x2  $12.000c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-06', 1, 'Tote bag serigrafía', 12000, 2, 'sumup', 3832, 420, 24000, NULL);
 
-- 03  Pin metálico x3  $4.500c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-08', 1, 'Pin metálico', 4500, 3, 'efectivo', 2155, NULL, 13500, NULL);
 
-- 04  Poster A3 x1  $8.000  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-11', 1, 'Poster A3', 8000, 1, 'sumup', 1277, 140, 8000, NULL);
 
-- 05  Parche bordado x4  $3.500c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-13', 1, 'Parche bordado', 3500, 4, 'efectivo', 2235, NULL, 14000, NULL);
 
-- 06  Polera estampada blanca x1  $18.000  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-15', 1, 'Polera estampada blanca', 18000, 1, 'sumup', 2874, 315, 18000, NULL);
 
-- 07  Tote bag serigrafía x1  $12.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-18', 1, 'Tote bag serigrafía', 12000, 1, 'efectivo', 1916, NULL, 12000, NULL);
 
-- 08  Pin metálico x5  $4.500c/u  sumup  (descuento aplicado)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-21', 1, 'Pin metálico', 4500, 5, 'sumup', 3592, 394, 22500, 'Descuento aplicado');
 
-- 09  Poster A3 x2  $8.000c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-25', 1, 'Poster A3', 8000, 2, 'efectivo', 2555, NULL, 16000, NULL);
 
-- 10  Parche bordado x3  $3.500c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-03-28', 1, 'Parche bordado', 3500, 3, 'sumup', 1677, 184, 10500, NULL);
 
 
-- ──────────────────────────────────────────────
-- ABRIL 2026
-- ──────────────────────────────────────────────
 
-- 11  Polera estampada negra x2  $18.000c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-02', 1, 'Polera estampada negra', 18000, 2, 'sumup', 5748, 630, 36000, NULL);
 
-- 12  Tote bag serigrafía x1  $12.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-05', 1, 'Tote bag serigrafía', 12000, 1, 'efectivo', 1916, NULL, 12000, NULL);
 
-- 13  Pin metálico x3  $4.500c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-07', 1, 'Pin metálico', 4500, 3, 'efectivo', 2155, NULL, 13500, NULL);
 
-- 14  Polera estampada blanca x1  $18.000  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-10', 1, 'Polera estampada blanca', 18000, 1, 'sumup', 2874, 315, 18000, NULL);
 
-- 15  Parche bordado x5  $3.500c/u  sumup  (descuento aplicado)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-12', 1, 'Parche bordado', 3500, 5, 'sumup', 2793, 306, 17500, 'Descuento aplicado');
 
-- 16  Tote bag serigrafía x2  $12.000c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-16', 1, 'Tote bag serigrafía', 12000, 2, 'efectivo', 3832, NULL, 24000, NULL);
 
-- 17  Polera estampada negra x1  $18.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-19', 1, 'Polera estampada negra', 18000, 1, 'efectivo', 2874, NULL, 18000, NULL);
 
-- 18  Pin metálico x2  $4.500c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-22', 1, 'Pin metálico', 4500, 2, 'sumup', 1437, 158, 9000, NULL);
 
-- 19  Poster A3 x2  $8.000c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-25', 1, 'Poster A3', 8000, 2, 'efectivo', 2555, NULL, 16000, NULL);
 
-- 20  Parche bordado x4  $3.500c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES ('2026-04-29', 1, 'Parche bordado', 3500, 4, 'sumup', 2235, 245, 14000, NULL);
 

