-- =============================================================
-- SEED: Ventas ficticias — Badtrip (pyme_id = 1)
-- Fechas RELATIVAS a hoy: se calculan con date('now','localtime')
-- al cargar el seed, así siempre hay ventas recientes para mostrar
-- sin importar cuándo se cree la base.
-- 20 registros repartidos en los últimos ~2 meses (2 caen hoy).
-- Requisitos previos: que exista una fila en pymes con id = 1
-- y nombre = 'Badtrip'. Ajusta pyme_id si es distinto.
-- IVA  = ROUND(total / 1.19 * 0.19)
-- Comisión SumUp = ROUND(total * 0.0175)  — solo si metodo='sumup'
-- =============================================================

-- ──────────────────────────────────────────────
-- HOY y días recientes
-- ──────────────────────────────────────────────

-- 01  Polera estampada negra x1  $18.000  efectivo  (hoy)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime'), 1, 'Polera estampada negra', 18000, 1, 'efectivo', 2874, NULL, 18000, NULL);

-- 02  Tote bag serigrafía x2  $12.000c/u  sumup  (hoy)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime'), 1, 'Tote bag serigrafía', 12000, 2, 'sumup', 3832, 420, 24000, NULL);

-- 03  Pin metálico x3  $4.500c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-2 day'), 1, 'Pin metálico', 4500, 3, 'efectivo', 2155, NULL, 13500, NULL);

-- 04  Poster A3 x1  $8.000  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-4 day'), 1, 'Poster A3', 8000, 1, 'sumup', 1277, 140, 8000, NULL);

-- 05  Parche bordado x4  $3.500c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-7 day'), 1, 'Parche bordado', 3500, 4, 'efectivo', 2235, NULL, 14000, NULL);

-- 06  Polera estampada blanca x1  $18.000  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-9 day'), 1, 'Polera estampada blanca', 18000, 1, 'sumup', 2874, 315, 18000, NULL);

-- 07  Tote bag serigrafía x1  $12.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-12 day'), 1, 'Tote bag serigrafía', 12000, 1, 'efectivo', 1916, NULL, 12000, NULL);

-- 08  Pin metálico x5  $4.500c/u  sumup  (descuento aplicado)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-15 day'), 1, 'Pin metálico', 4500, 5, 'sumup', 3592, 394, 22500, 'Descuento aplicado');

-- 09  Poster A3 x2  $8.000c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-19 day'), 1, 'Poster A3', 8000, 2, 'efectivo', 2555, NULL, 16000, NULL);

-- 10  Parche bordado x3  $3.500c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-23 day'), 1, 'Parche bordado', 3500, 3, 'sumup', 1677, 184, 10500, NULL);


-- ──────────────────────────────────────────────
-- Mes anterior
-- ──────────────────────────────────────────────

-- 11  Polera estampada negra x2  $18.000c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-27 day'), 1, 'Polera estampada negra', 18000, 2, 'sumup', 5748, 630, 36000, NULL);

-- 12  Tote bag serigrafía x1  $12.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-30 day'), 1, 'Tote bag serigrafía', 12000, 1, 'efectivo', 1916, NULL, 12000, NULL);

-- 13  Pin metálico x3  $4.500c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-33 day'), 1, 'Pin metálico', 4500, 3, 'efectivo', 2155, NULL, 13500, NULL);

-- 14  Polera estampada blanca x1  $18.000  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-37 day'), 1, 'Polera estampada blanca', 18000, 1, 'sumup', 2874, 315, 18000, NULL);

-- 15  Parche bordado x5  $3.500c/u  sumup  (descuento aplicado)
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-40 day'), 1, 'Parche bordado', 3500, 5, 'sumup', 2793, 306, 17500, 'Descuento aplicado');

-- 16  Tote bag serigrafía x2  $12.000c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-44 day'), 1, 'Tote bag serigrafía', 12000, 2, 'efectivo', 3832, NULL, 24000, NULL);

-- 17  Polera estampada negra x1  $18.000  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-48 day'), 1, 'Polera estampada negra', 18000, 1, 'efectivo', 2874, NULL, 18000, NULL);

-- 18  Pin metálico x2  $4.500c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-51 day'), 1, 'Pin metálico', 4500, 2, 'sumup', 1437, 158, 9000, NULL);

-- 19  Poster A3 x2  $8.000c/u  efectivo
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-55 day'), 1, 'Poster A3', 8000, 2, 'efectivo', 2555, NULL, 16000, NULL);

-- 20  Parche bordado x4  $3.500c/u  sumup
INSERT INTO ventas (fecha, pyme_id, articulo, valor, cantidad, metodo, iva, comision_sumup, total, comentario)
VALUES (date('now','localtime','-58 day'), 1, 'Parche bordado', 3500, 4, 'sumup', 2235, 245, 14000, NULL);


-- ──────────────────────────────────────────────
-- Cierre de caja de HOY (derivado de TODAS las ventas del día)
-- Debe ir al final: este seed carga después de seed.sql, así ya están
-- insertadas tanto las ventas demo como las de Badtrip de hoy.
-- Misma fórmula que CajaModule.cerrar_dia:
--   esperado = caja_inicial + total_efectivo
--   caja_final_real = esperado  → diferencia 0 (cierre limpio de demo)
-- ──────────────────────────────────────────────
INSERT INTO caja_diaria (
    fecha, caja_inicial, total_efectivo, total_sumup, total_iva,
    comision_sumup_total, caja_final_esperada, caja_final_real, diferencia,
    cerrada, comentario
)
SELECT
    date('now','localtime'),
    5000,
    COALESCE(SUM(CASE WHEN metodo = 'efectivo' THEN total END), 0),
    COALESCE(SUM(CASE WHEN metodo = 'sumup'    THEN total END), 0),
    COALESCE(SUM(iva), 0),
    COALESCE(SUM(CASE WHEN metodo = 'sumup' THEN comision_sumup END), 0),
    5000 + COALESCE(SUM(CASE WHEN metodo = 'efectivo' THEN total END), 0),
    5000 + COALESCE(SUM(CASE WHEN metodo = 'efectivo' THEN total END), 0),
    0,
    1,
    'Cierre demo'
FROM ventas
WHERE fecha = date('now','localtime');
