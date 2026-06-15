import requests, time

AREQUIPA = "http://127.0.0.1:8001"
CUSCO    = "http://127.0.0.1:8002"
TRUJILLO = "http://127.0.0.1:8003"
nodos = {"Arequipa": AREQUIPA, "Cusco": CUSCO, "Trujillo": TRUJILLO}

def estado():
    for nombre, url in nodos.items():
        s = requests.get(f"{url}/saldo").json()["saldo"]
        print(f"  {nombre}: S/ {s}")

def reset():
    requests.post(f"{AREQUIPA}/set", json={"saldo": 1000})
    requests.post(f"{CUSCO}/set",    json={"saldo": 800})
    requests.post(f"{TRUJILLO}/set", json={"saldo": 600})
    time.sleep(0.3)

def transaccion_2pc(origen, destino, monto, simular_fallo=False):
    print(f"\nINICIANDO 2PC: {origen} -> {destino} | S/ {monto}")
    url_origen  = nodos[origen]
    url_destino = nodos[destino]

    # FASE 1: PREPARE
    print("[FASE 1] PREPARE...")
    try:
        v1 = requests.post(f"{url_origen}/prepare",  json={"monto": -monto}).json()
        print(f"  {origen} voto: {v1['vote']}")
        if simular_fallo:
            raise ConnectionError("Fallo simulado en Trujillo")
        v2 = requests.post(f"{url_destino}/prepare", json={"monto":  monto}).json()
        print(f"  {destino} voto: {v2['vote']}")
    except Exception as e:
        print(f"  ERROR en PREPARE: {e}")
        print("[FASE 2] ROLLBACK global")
        requests.post(f"{url_origen}/rollback")
        return False

    if v1["vote"] == "COMMIT" and v2["vote"] == "COMMIT":
        # FASE 2: COMMIT
        print("[FASE 2] COMMIT global")
        requests.post(f"{url_origen}/commit",  json={"monto": -monto})
        requests.post(f"{url_destino}/commit", json={"monto":  monto})
        print("  Transaccion COMMITTED exitosamente.")
        return True
    else:
        print("[FASE 2] ABORT (algun nodo voto ABORT)")
        requests.post(f"{url_origen}/rollback")
        requests.post(f"{url_destino}/rollback")
        return False

# ============ EJECUCION ============
print("=" * 50)
print("SISTEMA NACIONAL DE BANCOS COOPERATIVOS")
print("=" * 50)
reset()
print("\nEstado inicial:")
estado()

# Escenario 1: Transferencia exitosa Arequipa -> Cusco
transaccion_2pc("Arequipa", "Cusco", 200)
print("\nEstado tras transferencia exitosa:")
estado()

# Escenario 2: Fallo durante la transferencia
transaccion_2pc("Cusco", "Trujillo", 300, simular_fallo=True)
print("\nEstado tras fallo (sin cambios):")
estado()

# Escenario 3: Intento con saldo insuficiente
transaccion_2pc("Trujillo", "Arequipa", 9999)
print("\nEstado final:")
estado()
