import unittest
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# =====================================================================
# 1. IMPLEMENTACIÓN DE PATRONES DE RECUPERACIÓN (CLIENTE/ORQUESTADOR)
# =====================================================================

# --- PATRÓN SAGA (Pedido <-> Inventario) ---
def crear_pedido_con_saga(cliente, producto, cantidad, monto, max_retries=3, timeout=1.5):
    """
    Orquestador Saga para crear un pedido y reservar stock en inventario.
    Implementa reintentos con timeouts. Si la reserva falla (por inconsistencia o falta de stock),
    ejecuta la transacción de compensación cancelando el pedido creado.
    """
    PEDIDOS_URL = "http://localhost:8081/api/pedidos"
    INVENTARIO_URL = "http://localhost:8082/api/inventario"
    
    pedido_id = None
    ultimo_error = None
    
    # Paso 1: Registrar el Pedido con reintentos
    for intento in range(1, max_retries + 1):
        try:
            print(f"[Saga] Intentando registrar pedido para '{cliente}' (Intento {intento}/{max_retries})...")
            res = requests.post(
                PEDIDOS_URL,
                json={"cliente": cliente, "monto": monto},
                timeout=timeout
            )
            if res.status_code == 200:
                pedido_id = res.json()["pedidoId"]
                print(f"[Saga] Pedido registrado exitosamente con ID: {pedido_id}")
                break
            else:
                ultimo_error = f"HTTP {res.status_code}: {res.text}"
        except requests.exceptions.RequestException as e:
            ultimo_error = str(e)
            print(f"[Saga] Fallo de red/timeout en intento {intento}: {ultimo_error}")
            time.sleep(0.3)
            
    if not pedido_id:
        return {
            "exito": False,
            "estado": "FALLIDO",
            "pedidoId": None,
            "error": f"No se pudo registrar el pedido tras reintentos. Detalle: {ultimo_error}"
        }
        
    # Paso 2: Reservar stock en Inventario
    reserva_exitosa = False
    for intento in range(1, max_retries + 1):
        try:
            print(f"[Saga] Intentando reservar {cantidad} unidades de '{producto}' para pedido {pedido_id} (Intento {intento}/{max_retries})...")
            res_stock = requests.post(
                f"{INVENTARIO_URL}/{producto}/reservar",
                json={"cantidad": cantidad},
                timeout=timeout
            )
            if res_stock.status_code == 200:
                data = res_stock.json()
                if data.get("reservaExitosa"):
                    reserva_exitosa = True
                    print(f"[Saga] Reserva exitosa para '{producto}' en pedido {pedido_id}.")
                    break
                else:
                    ultimo_error = "Reserva rechazada por stock insuficiente o inconsistencia."
                    print(f"[Saga] Reserva rechazada en Inventario: {ultimo_error}")
                    # Al ser un fallo de negocio (stock insuficiente), no reintentamos
                    break
            else:
                ultimo_error = f"HTTP {res_stock.status_code}: {res_stock.text}"
        except requests.exceptions.RequestException as e:
            ultimo_error = str(e)
            print(f"[Saga] Fallo de red/timeout en reserva, intento {intento}: {ultimo_error}")
            time.sleep(0.3)
            
    # Paso 3: Transacción de compensación en caso de fallo
    if not reserva_exitosa:
        print(f"[Saga] [COMPENSACIÓN] Iniciando cancelación de pedido {pedido_id}...")
        compensacion_exitosa = False
        for intento in range(1, max_retries + 1):
            try:
                res_cancel = requests.delete(f"{PEDIDOS_URL}/{pedido_id}", timeout=2.0)
                if res_cancel.status_code == 200:
                    print(f"[Saga] [COMPENSACIÓN] Pedido {pedido_id} cancelado con éxito.")
                    compensacion_exitosa = True
                    break
                else:
                    print(f"[Saga] [COMPENSACIÓN] Error al cancelar, HTTP {res_cancel.status_code}")
            except Exception as e:
                print(f"[Saga] [COMPENSACIÓN] Intento {intento} fallido por error de red: {e}")
                time.sleep(0.5)
                
        return {
            "exito": False,
            "estado": "CANCELADO" if compensacion_exitosa else "REGISTRADO_PENDIENTE_CORRECCION",
            "pedidoId": pedido_id,
            "error": f"Fallo al reservar stock. Compensación {'ejecutada' if compensacion_exitosa else 'FALLIDA'}. Detalle: {ultimo_error}"
        }
        
    return {
        "exito": True,
        "estado": "REGISTRADO",
        "pedidoId": pedido_id
    }


# --- IDEMPOTENCIA Y REINTENTOS CONTROLADOS (Pedido <-> Facturación) ---
class FacturacionIdempotenteClient:
    """
    Cliente de facturación que controla los reintentos ante fallos temporales
    y realiza de-duplicación a nivel cliente si el servidor reporta duplicidad.
    """
    def __init__(self):
        self.cache_facturas = {} # pedido_id -> factura_id

    def generar_factura_idempotente(self, pedido_id, monto, max_retries=3, timeout=1.5):
        FACTURACION_URL = "http://localhost:8083/api/facturas"
        
        # 1. Si ya sabemos localmente que este pedido fue facturado con éxito, retornamos directamente
        if pedido_id in self.cache_facturas:
            print(f"[Idempotencia] [CACHE CLIENTE] Factura ya existente para pedido {pedido_id}: {self.cache_facturas[pedido_id]}")
            return {
                "facturaId": self.cache_facturas[pedido_id],
                "pedidoId": pedido_id,
                "monto": monto,
                "duplicada": False,
                "origen": "cache_cliente"
            }
            
        ultimo_error = None
        for intento in range(1, max_retries + 1):
            try:
                print(f"[Idempotencia] Enviando solicitud de facturación para pedido {pedido_id} (Intento {intento})...")
                res = requests.post(
                    FACTURACION_URL,
                    json={"pedidoId": pedido_id, "monto": monto},
                    timeout=timeout
                )
                if res.status_code == 200:
                    data = res.json()
                    factura_id = data["facturaId"]
                    posible_duplicidad = data.get("posibleDuplicidad", False)
                    
                    if posible_duplicidad:
                        print(f"[Idempotencia] [AVISO] Se detectó posible duplicidad en servidor para pedido {pedido_id}.")
                        # De-duplicación: Si ya guardamos una factura previamente, usamos esa.
                        if pedido_id in self.cache_facturas:
                            factura_id = self.cache_facturas[pedido_id]
                            print(f"[Idempotencia] [RESOLUCIÓN] Usando la primera factura registrada: {factura_id}")
                        else:
                            # Si es la primera vez que escuchamos de este ID, lo registramos
                            self.cache_facturas[pedido_id] = factura_id
                    else:
                        # Registro exitoso sin duplicidad aparente
                        self.cache_facturas[pedido_id] = factura_id
                        
                    return {
                        "facturaId": factura_id,
                        "pedidoId": pedido_id,
                        "monto": monto,
                        "duplicada": posible_duplicidad,
                        "origen": "servidor"
                    }
                else:
                    ultimo_error = f"HTTP {res.status_code}"
            except requests.exceptions.RequestException as e:
                ultimo_error = str(e)
                print(f"[Idempotencia] Intento {intento} fallido: {ultimo_error}")
                # Backoff exponencial controlado
                time.sleep(0.3 * (2 ** (intento - 1)))
                
        raise RuntimeError(f"Error de facturación tras {max_retries} intentos: {ultimo_error}")


# --- CIRCUIT BREAKER + COLA DE PENDIENTES (Pedido <-> Transporte) ---
class CircuitBreakerOpenException(Exception):
    pass

class TransporteClientWithCircuitBreaker:
    """
    Cliente de asignación de transporte que utiliza Circuit Breaker y una cola
    de solicitudes pendientes para manejar caídas o errores 503 del servicio.
    """
    def __init__(self, failure_threshold=3, recovery_time=2.0):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.last_failure_time = None
        self.pending_queue = [] # Cola de solicitudes pendientes (pedido_id)

    def _update_state(self):
        if self.state == "OPEN":
            # Si pasó el tiempo de recuperación, cambia a HALF-OPEN
            if time.time() - self.last_failure_time >= self.recovery_time:
                self.state = "HALF-OPEN"
                print("[Circuit Breaker] Tránsito a HALF-OPEN. Probando salud del canal...")

    def registrar_falla(self):
        self.failure_count += 1
        print(f"[Circuit Breaker] Registro de fallo #{self.failure_count}.")
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_failure_time = time.time()
            print(f"[Circuit Breaker] !!! CIRCUITO ABIERTO !!! Umbral alcanzado. Last failure time: {self.last_failure_time}")

    def registrar_exito(self):
        self.failure_count = 0
        if self.state != "CLOSED":
            self.state = "CLOSED"
            print("[Circuit Breaker] !!! CIRCUITO CERRADO !!! Servicio recuperado.")

    def asignar_transporte(self, pedido_id):
        self._update_state()
        
        if self.state == "OPEN":
            print(f"[Circuit Breaker] [OPEN] Solicitud rechazada para pedido {pedido_id}. Encolando en pendientes.")
            self.pending_queue.append(pedido_id)
            raise CircuitBreakerOpenException("Circuito ABIERTO. Solicitud encolada.")
            
        TRANSPORTE_URL = "http://localhost:8084/api/transporte/asignar"
        
        try:
            res = requests.post(
                TRANSPORTE_URL,
                json={"pedidoId": pedido_id},
                timeout=1.5
            )
            if res.status_code == 200:
                data = res.json()
                self.registrar_exito()
                return data
            elif res.status_code == 503:
                print(f"[Circuit Breaker] Error 503 del servicio de transporte para pedido {pedido_id}.")
                self.registrar_falla()
                self.pending_queue.append(pedido_id)
                raise RuntimeError("Servicio no disponible (503). Solicitud encolada.")
            else:
                print(f"[Circuit Breaker] Error HTTP {res.status_code} para pedido {pedido_id}.")
                self.registrar_falla()
                self.pending_queue.append(pedido_id)
                raise RuntimeError(f"Error inesperado HTTP {res.status_code}. Solicitud encolada.")
        except requests.exceptions.RequestException as e:
            print(f"[Circuit Breaker] Excepción de conexión/timeout para pedido {pedido_id}: {e}")
            self.registrar_falla()
            self.pending_queue.append(pedido_id)
            raise CircuitBreakerOpenException("Fallo de red en transporte. Solicitud encolada.")

    def procesar_cola(self):
        """
        Intenta enviar las solicitudes encoladas si el circuito está CLOSED o HALF-OPEN.
        """
        self._update_state()
        if self.state == "OPEN":
            print("[Circuit Breaker] Cola no procesada: el circuito sigue ABIERTO.")
            return 0
            
        if not self.pending_queue:
            return 0
            
        print(f"[Circuit Breaker] Procesando cola de pendientes: {len(self.pending_queue)} elementos...")
        exitosos = []
        
        for pid in list(self.pending_queue):
            try:
                res = requests.post(
                    "http://localhost:8084/api/transporte/asignar",
                    json={"pedidoId": pid},
                    timeout=1.5
                )
                if res.status_code == 200:
                    print(f"[Circuit Breaker] Asignación en cola exitosa para pedido {pid}.")
                    self.registrar_exito()
                    exitosos.append(pid)
                else:
                    print(f"[Circuit Breaker] Fallo en cola para pedido {pid}: HTTP {res.status_code}")
                    self.registrar_falla()
                    break # Detener procesamiento si vuelve a fallar
            except Exception as e:
                print(f"[Circuit Breaker] Fallo de conexión en cola para pedido {pid}: {e}")
                self.registrar_falla()
                break
                
        for pid in exitosos:
            self.pending_queue.remove(pid)
            
        return len(exitosos)


# =====================================================================
# 2. SUITE DE PRUEBAS DE INTEGRACIÓN (UNITTEST)
# =====================================================================

class TestLogiFreshIntegracion(unittest.TestCase):
    
    PEDIDOS_URL = "http://localhost:8081/api/pedidos"
    INVENTARIO_URL = "http://localhost:8082/api/inventario"
    FACTURACION_URL = "http://localhost:8083/api/facturas"
    TRANSPORTE_URL = "http://localhost:8084/api/transporte"

    @classmethod
    def setUpClass(cls):
        # Asegurar de que los servicios estén listos (esperar hasta 10 segundos)
        servicios = {
            "Pedidos": cls.PEDIDOS_URL,
            "Inventario": cls.INVENTARIO_URL,
            "Facturación": cls.FACTURACION_URL,
            "Transporte": cls.TRANSPORTE_URL
        }
        print("\n=== Preparando ambiente de pruebas ===")
        for nombre, url in servicios.items():
            conectado = False
            for _ in range(10):
                try:
                    resp = requests.get(f"{url}/health", timeout=1.5)
                    if resp.status_code == 200:
                        conectado = True
                        break
                except Exception:
                    pass
                time.sleep(1.0)
            if not conectado:
                raise RuntimeError(f"El microservicio '{nombre}' no levantó a tiempo en {url}")
        print("=== Servicios listos para la ejecución ===\n")

    # -----------------------------------------------------------------
    # PRUEBA 1: Pedido ↔ Inventario (Saga + Compensación)
    # -----------------------------------------------------------------
    def test_saga_pedido_inventario_exitoso(self):
        print("\n--- Ejecutando Prueba: Saga Pedido-Inventario Exitoso ---")
        # Flujo exitoso con un producto y cantidad razonable
        resultado = crear_pedido_con_saga(
            cliente="Tienda Orgánica S.A.",
            producto="yogurt-natural-1L",
            cantidad=3,
            monto=150.0
        )
        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["estado"], "REGISTRADO")
        self.assertIsNotNone(resultado["pedidoId"])
        
        # Verificar que el pedido realmente exista y esté REGISTRADO
        resp = requests.get(f"{self.PEDIDOS_URL}/{resultado['pedidoId']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["estado"], "REGISTRADO")

    def test_saga_pedido_inventario_compensacion(self):
        print("\n--- Ejecutando Prueba: Saga Pedido-Inventario con Compensación ---")
        # Forzar un stock insuficiente pidiendo una cantidad desmesurada (99999)
        resultado = crear_pedido_con_saga(
            cliente="Tienda Orgánica S.A.",
            producto="yogurt-natural-1L",
            cantidad=99999,
            monto=150.0
        )
        self.assertFalse(resultado["exito"])
        self.assertEqual(resultado["estado"], "CANCELADO")
        self.assertIsNotNone(resultado["pedidoId"])
        
        # Verificar que el pedido haya sido CANCELADO por la transacción de compensación
        resp = requests.get(f"{self.PEDIDOS_URL}/{resultado['pedidoId']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["estado"], "CANCELADO")

    # -----------------------------------------------------------------
    # PRUEBA 2: Pedido ↔ Facturación (Idempotencia y Reintentos)
    # -----------------------------------------------------------------
    def test_idempotencia_facturacion(self):
        print("\n--- Ejecutando Prueba: Idempotencia Facturas Duplicadas ---")
        client = FacturacionIdempotenteClient()
        pedido_id = 8888
        monto = 320.0
        
        # Hacemos 15 llamadas de facturación consecutivas para el mismo pedido.
        # El servidor mock tiene un 50% de probabilidad de generar duplicados,
        # pero el cliente resiliente debe detectarlo y devolver el mismo facturaId original.
        facturas = []
        for i in range(15):
            res = client.generar_factura_idempotente(pedido_id, monto)
            facturas.append(res["facturaId"])
            
        print(f"Facturas obtenidas por el cliente: {facturas}")
        # Verificar que todas las llamadas devolvieron exactamente el mismo ID de factura
        primera_factura = facturas[0]
        for f_id in facturas:
            self.assertEqual(f_id, primera_factura, "El cliente no de-duplicó correctamente la factura")
            
        # Comprobar que en la caché local del cliente solo hay 1 factura para este pedido
        self.assertIn(pedido_id, client.cache_facturas)
        self.assertEqual(client.cache_facturas[pedido_id], primera_factura)
        print("-> De-duplicación e idempotencia verificadas exitosamente.")

    # -----------------------------------------------------------------
    # PRUEBA 3: Pedido ↔ Transporte (Circuit Breaker y Cola)
    # -----------------------------------------------------------------
    def test_circuit_breaker_transporte(self):
        print("\n--- Ejecutando Prueba: Circuit Breaker Transporte ---")
        # Instanciamos el cliente con un umbral de 3 fallas y tiempo de recuperación de 2 segundos
        client = TransporteClientWithCircuitBreaker(failure_threshold=3, recovery_time=2.0)
        
        # 1. Haremos llamadas repetidas. Dado que el servicio tiene un 15% de fallos 503,
        # forzamos fallos simulando llamadas fallidas o simplemente llamándolo múltiples veces.
        # Para garantizar que el circuito se abra en el test, mockeamos localmente el comportamiento
        # o forzamos llamadas consecutivas que fallen.
        # Vamos a inyectar directamente llamadas fallidas en el cliente para abrir el circuito
        # simulando fallos reales sin depender de la aleatoriedad del 15% del mock de transporte.
        
        # Simulamos 3 fallos consecutivos
        print("Simulando fallos en el servicio de transporte...")
        for i in range(3):
            client.registrar_falla()
            
        self.assertEqual(client.state, "OPEN")
        print(f"Estado del circuito esperado: OPEN. Estado real: {client.state}")
        
        # Con el circuito abierto, intentamos asignar transporte a 2 pedidos.
        # Deben encolarse en pendientes y lanzar CircuitBreakerOpenException.
        pedido_a = 9001
        pedido_b = 9002
        
        with self.assertRaises(CircuitBreakerOpenException):
            client.asignar_transporte(pedido_a)
            
        with self.assertRaises(CircuitBreakerOpenException):
            client.asignar_transporte(pedido_b)
            
        self.assertEqual(len(client.pending_queue), 2)
        self.assertIn(pedido_a, client.pending_queue)
        self.assertIn(pedido_b, client.pending_queue)
        print(f"Pedidos correctamente encolados en cola de pendientes: {client.pending_queue}")
        
        # Esperamos el tiempo de recuperación (2 segundos) para permitir el cambio a HALF-OPEN
        print("Esperando 2.2 segundos para el tiempo de recuperación...")
        time.sleep(2.2)
        
        # Intentamos procesar la cola. Como pasó el tiempo de recuperación,
        # al procesar la cola se pasará a HALF-OPEN y si las llamadas al microservicio mock
        # son exitosas (que tienen 85% de probabilidad de éxito), el circuito volverá a CLOSED.
        # Para estar seguros, reintentamos el procesamiento de cola en caso de que ocurra
        # el 15% de fallo aleatorio durante el test.
        exito = False
        for intento in range(5):
            print(f"Intento {intento+1} de procesar la cola después de la recuperación...")
            procesados = client.procesar_cola()
            if procesados > 0:
                exito = True
                break
            time.sleep(0.5)
            
        # Si el servicio real está online y responde 200, la cola debe haberse procesado
        # y el circuito debe haber vuelto a CLOSED.
        self.assertEqual(client.state, "CLOSED")
        self.assertEqual(len(client.pending_queue), 0)
        print("-> Circuit Breaker e integración con cola validados con éxito.")

if __name__ == "__main__":
    unittest.main()
