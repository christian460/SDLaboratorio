import requests
import time

LIMA = "http://127.0.0.1:8001"
AREQUIPA = "http://127.0.0.1:8002"

def estado():
    l = requests.get(f"{LIMA}/stock").json()["stock"]
    a = requests.get(f"{AREQUIPA}/stock").json()["stock"]
    print(f"ESTADO -> Arequipa:{a} | Lima:{l}")

def reset():
    requests.post(f"{LIMA}/set", json={"stock": 70})
    requests.post(f"{AREQUIPA}/set", json={"stock": 80})
    time.sleep(0.3)

print("INICIALIZANDO SISTEMA DISTRIBUIDO")

reset()
estado()

print("TRANSACCION 1 FALLIDA")

try:
    print("Lima ejecuta descuento")
    r = requests.post(f"{LIMA}/decrease")
    print("Lima:", r.json())
    estado()

    print("Intentando comunicación con Arequipa (Simulando falla de red real)...")
    # Intentamos conectar a un puerto inexistente para forzar un error de conexión real
    requests.post("http://127.0.0.1:8003/increase", timeout=1.5)

except requests.exceptions.RequestException as e:
    print("ERROR DE CONEXIÓN REAL:", type(e).__name__)
    print("ROLLBACK SOLO LIMA (participó)")

    # 🔥 SOLO ROLLBACK LIMA (clave del fix)
    requests.post(f"{LIMA}/rollback")

    estado()

print("TRANSACCION 2 EXITOSA")

requests.post(f"{LIMA}/decrease")
requests.post(f"{AREQUIPA}/increase")

estado()

print("FIN")