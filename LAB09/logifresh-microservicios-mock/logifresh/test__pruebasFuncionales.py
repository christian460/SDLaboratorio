import unittest
import requests
import time

class TestLogiFreshFuncionales(unittest.TestCase):
    # URLs de los microservicios
    PEDIDOS_URL = "http://localhost:8081/api/pedidos"
    INVENTARIO_URL = "http://localhost:8082/api/inventario"
    FACTURACION_URL = "http://localhost:8083/api/facturas"
    TRANSPORTE_URL = "http://localhost:8084/api/transporte"
    NOTIFICACIONES_URL = "http://localhost:8085/api/notificaciones"

    @classmethod
    def setUpClass(cls):
        # Verificar que todos los servicios estén encendidos
        servicios = {
            "Pedidos": cls.PEDIDOS_URL,
            "Inventario": cls.INVENTARIO_URL,
            "Facturación": cls.FACTURACION_URL,
            "Transporte": cls.TRANSPORTE_URL,
            "Notificaciones": cls.NOTIFICACIONES_URL
        }
        print("Comprobando conexión con los microservicios...")
        for nombre, url in servicios.items():
            try:
                resp = requests.get(f"{url}/health", timeout=2)
                if resp.status_code != 200:
                    raise Exception()
            except Exception:
                raise RuntimeError(
                    f"\n[ERROR] El servicio '{nombre}' no está respondiendo en {url}.\n"
                    f"Recuerda correr primero: docker compose up -d"
                )
        print("¡Todo listo para empezar!\n")

    def test_cp01_registrar_pedido_exitoso(self):
        # CP-01: Registrar un pedido normal con datos válidos
        print("Corriendo CP-01...")
        datos = {"cliente": "Supermercado Central", "monto": 250.0}
        res = requests.post(self.PEDIDOS_URL, json=datos)
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"Respuesta: {data}")
        self.assertIn("pedidoId", data)
        self.assertEqual(data["estado"], "REGISTRADO")
        print("-> CP-01 completado con éxito.\n")

    def test_cp02_descuento_promocion_defecto(self):
        # CP-02: Verificar descuento con promoción (buscando el bug del 40% de fallo)
        print("Corriendo CP-02...")
        datos = {"cliente": "Supermercado Central", "monto": 100.0, "codigoPromocion": "VERANO10"}
        
        descuentos_aplicados = 0
        descuentos_fallidos = 0
        
        # Hacemos varias peticiones para ver si en alguna falla aplicar el descuento
        for _ in range(15):
            res = requests.post(self.PEDIDOS_URL, json=datos)
            self.assertEqual(res.status_code, 200)
            if res.json()["descuentoAplicado"]:
                descuentos_aplicados += 1
            else:
                descuentos_fallidos += 1
                
        print(f"Resultados: Aplicados={descuentos_aplicados}, Fallidos={descuentos_fallidos}")
        # Validamos que al menos una vez haya fallado el descuento (bug confirmado)
        self.assertTrue(descuentos_fallidos > 0, "El descuento debería fallar algunas veces")
        print("-> CP-02: Bug de descuento confirmado (el descuento a veces no se aplica).\n")

    def test_cp03_rechazar_reserva_stock_insuficiente(self):
        # CP-03: Intentar reservar más stock del disponible
        print("Corriendo CP-03...")
        producto = "yogurt-natural-1L"
        datos = {"cantidad": 9999}
        
        res = requests.post(f"{self.INVENTARIO_URL}/{producto}/reservar", json=datos)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"Respuesta: {data}")
        self.assertFalse(data["reservaExitosa"])
        print("-> CP-03 completado con éxito.\n")

    def test_cp04_cancelar_pedido(self):
        # CP-04: Cancelar un pedido que ya existe
        print("Corriendo CP-04...")
        pedido_id = 1002
        res = requests.delete(f"{self.PEDIDOS_URL}/{pedido_id}")
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"Respuesta: {data}")
        self.assertEqual(data["estado"], "CANCELADO")
        print("-> CP-04 completado con éxito.\n")

    def test_cp05_aceptar_pedido_cantidad_cero_defecto(self):
        # CP-05: Enviar pedido con cantidad 0 (debería fallar, pero el bug hace que pase)
        print("Corriendo CP-05...")
        datos = {"cliente": "Tienda Local", "monto": 150.0, "cantidad": 0}
        res = requests.post(self.PEDIDOS_URL, json=datos)
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"Respuesta: {data}")
        # Pasa erróneamente sin validar la cantidad
        self.assertEqual(data["estado"], "REGISTRADO")
        print("-> CP-05: Bug confirmado (el pedido se registra aunque la cantidad sea 0).\n")

    def test_cp06_facturas_duplicadas_defecto(self):
        # CP-06: Generar facturas duplicadas para el mismo pedido (bug de idempotencia)
        print("Corriendo CP-06...")
        pedido_id = 2002
        datos = {"pedidoId": pedido_id, "monto": 120.0}
        
        facturas = set()
        
        # Mandamos el mismo pedido varias veces para ver si genera facturas duplicadas
        for _ in range(10):
            res = requests.post(self.FACTURACION_URL, json=datos)
            self.assertEqual(res.status_code, 200)
            facturas.add(res.json()["facturaId"])
            
        print(f"Facturas generadas para el pedido {pedido_id}: {facturas}")
        # Si generó más de 1 factura, el bug está confirmado
        self.assertTrue(len(facturas) > 1, "Deberían generarse facturas duplicadas")
        print("-> CP-06: Bug de facturas duplicadas confirmado.\n")

    def test_cp07_notificacion_retraso_defecto(self):
        # CP-07: Medir si el envío de notificaciones tiene retrasos (bug del proveedor de email)
        print("Corriendo CP-07...")
        datos = {"destinatario": "cliente@correo.com", "canal": "email"}
        
        tiempos = []
        for _ in range(10):
            inicio = time.time()
            res = requests.post(f"{self.NOTIFICACIONES_URL}/enviar", json=datos)
            fin = time.time() - inicio
            self.assertEqual(res.status_code, 200)
            tiempos.append(fin)
            
        max_tiempo = max(tiempos)
        print(f"Tiempos de respuesta (segundos): {[round(t, 2) for t in tiempos]}")
        # Si alguna tardó más de 3 segundos, se confirma el retraso
        self.assertTrue(max_tiempo >= 3.0, "Alguna notificación debería retrasarse")
        print(f"-> CP-07: Bug de retraso de notificaciones confirmado ({round(max_tiempo, 2)}s).\n")

    def test_cp08_asignar_transporte_exitoso(self):
        # CP-08: Asignar transporte (tiene un 15% de probabilidad de dar error 503, reintentamos)
        print("Corriendo CP-08...")
        datos = {"pedidoId": 3001}
        
        exito = False
        intentos = 0
        data = {}
        
        while not exito and intentos < 10:
            intentos += 1
            res = requests.post(f"{self.TRANSPORTE_URL}/asignar", json=datos)
            if res.status_code == 200:
                data = res.json()
                exito = True
            elif res.status_code == 503:
                print(f"  Intento {intentos}: error 503 simulado. Reintentando...")
                time.sleep(0.5)
                
        self.assertTrue(exito, "No se pudo asignar transporte por fallos de red 503")
        print(f"Respuesta: {data}")
        self.assertEqual(data["estado"], "ASIGNADO")
        self.assertTrue(str(data["vehiculoAsignado"]).startswith("REFR-"))
        print("-> CP-08 completado con éxito.\n")

    def test_cp09_consultar_pedido_existente(self):
        # CP-09: Consultar el estado de un pedido por su ID
        print("Corriendo CP-09...")
        pedido_id = 1001
        res = requests.get(f"{self.PEDIDOS_URL}/{pedido_id}")
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"Respuesta: {data}")
        self.assertEqual(data["pedidoId"], pedido_id)
        print("-> CP-09 completado con éxito.\n")

    def test_cp10_codigo_promocion_vencido_defecto(self):
        # CP-10: Mandar un código de promoción vencido (no debería pasar, pero el bug hace que sí)
        print("Corriendo CP-10...")
        datos = {"cliente": "Cliente Vip", "monto": 500.0, "codigoPromocion": "PROMO_VENCIDA_2025"}
        res = requests.post(self.PEDIDOS_URL, json=datos)
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        print(f"Respuesta: {data}")
        self.assertEqual(data["estado"], "REGISTRADO")
        print("-> CP-10: Bug confirmado (el sistema acepta códigos vencidos sin validar).\n")

if __name__ == "__main__":
    unittest.main()
