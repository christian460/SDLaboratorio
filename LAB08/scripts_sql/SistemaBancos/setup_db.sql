-- Nodo Arequipa
CREATE DATABASE banco_arequipa;
\c banco_arequipa
CREATE TABLE cuentas(id SERIAL PRIMARY KEY, titular VARCHAR(100), saldo NUMERIC);
INSERT INTO cuentas(titular, saldo) VALUES('Cuenta Cooperativa Arequipa', 1000);

-- Nodo Cusco
CREATE DATABASE banco_cusco;
\c banco_cusco
CREATE TABLE cuentas(id SERIAL PRIMARY KEY, titular VARCHAR(100), saldo NUMERIC);
INSERT INTO cuentas(titular, saldo) VALUES('Cuenta Cooperativa Cusco', 800);

-- Nodo Trujillo
CREATE DATABASE banco_trujillo;
\c banco_trujillo
CREATE TABLE cuentas(id SERIAL PRIMARY KEY, titular VARCHAR(100), saldo NUMERIC);
INSERT INTO cuentas(titular, saldo) VALUES('Cuenta Cooperativa Trujillo', 600);
