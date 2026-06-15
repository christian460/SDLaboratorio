-- ==========================================
-- EJERCICIO 1: Transferencia Exitosa (20 unidades de Arequipa a Lima)
-- ==========================================

-- ==========================================
-- NODO 1: AREQUIPA (almacen_arequipa)
-- ==========================================
-- 1. Verificar stock disponible
SELECT stock FROM inventario WHERE producto = 'Paracetamol';
-- Resultado esperado: 100

-- 2. Iniciar transacción
BEGIN;

-- 3. Actualizar inventario origen
UPDATE inventario SET stock = stock - 20 WHERE producto = 'Paracetamol';

-- Preparar transacción (Fase 1 de 2PC)
PREPARE TRANSACTION 'transferencia_arequipa_lima';


-- ==========================================
-- NODO 2: LIMA (almacen_lima)
-- ==========================================
-- 1. Verificar stock disponible
SELECT stock FROM inventario WHERE producto = 'Paracetamol';
-- Resultado esperado: 50

-- 2. Iniciar transacción
BEGIN;

-- 4. Actualizar inventario destino
UPDATE inventario SET stock = stock + 20 WHERE producto = 'Paracetamol';

-- Preparar transacción (Fase 1 de 2PC)
PREPARE TRANSACTION 'transferencia_arequipa_lima';


-- ==========================================
-- COORDINADOR: CONFIRMAR CAMBIOS (Fase 2 de 2PC)
-- ==========================================
-- En almacen_arequipa:
COMMIT PREPARED 'transferencia_arequipa_lima';

-- En almacen_lima:
COMMIT PREPARED 'transferencia_arequipa_lima';


-- ==========================================
-- VERIFICACIÓN FINAL DEL STOCK
-- ==========================================
-- En almacen_arequipa:
SELECT stock FROM inventario WHERE producto = 'Paracetamol';
-- Resultado esperado: 80

-- En almacen_lima:
SELECT stock FROM inventario WHERE producto = 'Paracetamol';
-- Resultado esperado: 70
