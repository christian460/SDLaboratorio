import psycopg2
import time

conn_arequipa = psycopg2.connect(
    dbname="almacen_arequipa",
    user="postgres",
    password="913397",
    host="127.0.0.1",
    port="5432"
)

conn_lima = psycopg2.connect(
    dbname="almacen_lima",
    user="postgres",
    password="913397",
    host="127.0.0.1",
    port="5432"
)

def estado(cur_a, cur_l, msg):
    cur_a.execute("SELECT stock FROM inventario WHERE producto='Paracetamol'")
    a = cur_a.fetchone()[0]

    cur_l.execute("SELECT stock FROM inventario WHERE producto='Paracetamol'")
    l = cur_l.fetchone()[0]

    print(f"\n{msg}")
    print(f"Arequipa: {a} | Lima: {l}")

cur_a = conn_arequipa.cursor()
cur_l = conn_lima.cursor()

conn_arequipa.autocommit = False
conn_lima.autocommit = False

# estado inicial del sistema
print("Inicializando sistema...")
time.sleep(1)

cur_a.execute("UPDATE inventario SET stock=80 WHERE producto='Paracetamol'")
cur_l.execute("UPDATE inventario SET stock=70 WHERE producto='Paracetamol'")
conn_arequipa.commit()
conn_lima.commit()

estado(cur_a, cur_l, "ESTADO INICIAL")
time.sleep(1)

# transaccion 1 fallida
print("\nTRANSACCION 1 (FALLIDA)")
time.sleep(1)

try:
    cur_l.execute("UPDATE inventario SET stock = stock - 20 WHERE producto='Paracetamol'")
    estado(cur_a, cur_l, "INTERMEDIO (SIN CONFIRMAR)")
    time.sleep(1)

    raise Exception("Fallo de comunicación con Arequipa")

    cur_a.execute("UPDATE inventario SET stock = stock + 20 WHERE producto='Paracetamol'")

    conn_arequipa.commit()
    conn_lima.commit()

except Exception as e:
    print("\nERROR:", e)

    conn_arequipa.rollback()
    conn_lima.rollback()

    estado(cur_a, cur_l, "DESPUES DEL ROLLBACK")

# transaccion 2 exitosa
print("\nTRANSACCION 2 (EXITOSA)")
time.sleep(1)

cur_l.execute("UPDATE inventario SET stock = stock - 20 WHERE producto='Paracetamol'")
cur_a.execute("UPDATE inventario SET stock = stock + 20 WHERE producto='Paracetamol'")

conn_arequipa.commit()
conn_lima.commit()

estado(cur_a, cur_l, "ESTADO FINAL")

cur_a.close()
cur_l.close()
conn_arequipa.close()
conn_lima.close()

print("\nFIN DEL PROCESO")