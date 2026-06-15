import psycopg2
from fastapi import FastAPI

app = FastAPI()

def get_db():
    return psycopg2.connect(
        dbname="banco_trujillo", user="postgres",
        password="admin", host="127.0.0.1", port="5432",
        options="-c client_encoding=WIN1252"
    )

@app.get("/saldo")
def get_saldo():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT saldo FROM cuentas WHERE id=1")
    val = cur.fetchone()[0]; cur.close(); conn.close()
    return {"nodo": "Trujillo", "saldo": val}

@app.post("/prepare")
def prepare(data: dict):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT saldo FROM cuentas WHERE id=1")
    saldo = cur.fetchone()[0]
    monto = data.get("monto", 0)
    if saldo + monto < 0:
        cur.close(); conn.close()
        return {"vote": "ABORT", "razon": "Saldo insuficiente"}
    cur.close(); conn.close()
    return {"vote": "COMMIT"}

@app.post("/commit")
def commit_tx(data: dict):
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE cuentas SET saldo = saldo + %s WHERE id=1", (data["monto"],))
    conn.commit(); cur.close(); conn.close()
    return {"status": "COMMITTED"}

@app.post("/rollback")
def rollback_tx():
    return {"status": "ROLLBACK_OK"}

@app.post("/set")
def set_saldo(data: dict):
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE cuentas SET saldo = %s WHERE id=1", (data["saldo"],))
    conn.commit(); cur.close(); conn.close()
    return {"status": "ok"}
