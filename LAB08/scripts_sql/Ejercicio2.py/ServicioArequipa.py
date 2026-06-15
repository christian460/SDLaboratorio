import psycopg2
from fastapi import FastAPI

app = FastAPI()

def get_db_conn():
    return psycopg2.connect(
        dbname="almacen_arequipa",
        user="postgres",
        password="913397",
        host="127.0.0.1",
        port="5432"
    )

@app.get("/stock")
def get_stock():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT stock FROM inventario WHERE producto='Paracetamol'")
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"stock": val}

@app.post("/increase")
def increase():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET stock = stock + 20 WHERE producto='Paracetamol'")
    conn.commit()
    cur.execute("SELECT stock FROM inventario WHERE producto='Paracetamol'")
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"status": "ok", "stock": val}

@app.post("/rollback")
def rollback():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET stock = stock - 20 WHERE producto='Paracetamol'")
    conn.commit()
    cur.execute("SELECT stock FROM inventario WHERE producto='Paracetamol'")
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"status": "rollback", "stock": val}

@app.post("/set")
def set_stock(data: dict):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE inventario SET stock = %s WHERE producto='Paracetamol'", (data["stock"],))
    conn.commit()
    cur.execute("SELECT stock FROM inventario WHERE producto='Paracetamol'")
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"status": "ok", "stock": val}