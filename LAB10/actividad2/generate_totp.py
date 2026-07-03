import time
import hmac
import hashlib
import struct

def generate_totp(secret, interval=30):
    # Simulación matemática del estándar RFC 6238 (MFA)
    counter = int(time.time() // interval)
    key = secret.encode('utf-8')
    msg = struct.pack(">Q", counter)
    
    # Generar Hash HMAC-SHA1
    hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0f
    
    # Operación de truncamiento dinámico para obtener 6 dígitos
    code = (struct.unpack(">I", hmac_hash[offset:offset+4])[0] & 0x7fffffff) % 1000000
    return str(code).zfill(6)

# Clave secreta compartida simulada para Logi Market
SECRET_KEY = "LOGIMARKETSECRET"

print("--- DEMOSTRACIÓN COMPLEMENTARIA ACTIVIDAD 2 ---")
print(f"Código MFA actual para el empleado: {generate_totp(SECRET_KEY)}")
print("Este código cambiará automáticamente en los próximos 30 segundos.")
