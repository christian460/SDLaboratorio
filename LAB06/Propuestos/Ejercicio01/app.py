import re
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Almacenamiento en memoria para los estudiantes (lista de diccionarios)
# Iniciamos con algunos datos de prueba para una mejor experiencia de usuario inicial
estudiantes_db = [
    {
        "id": 1,
        "nombre": "Ana Sofia",
        "apellido": "García Torres",
        "carrera": "Ciencia de la Computación",
        "edad": 21,
        "correo": "ana.garcia@unsa.edu.pe"
    },
    {
        "id": 2,
        "nombre": "Carlos Alberto",
        "apellido": "Mendoza Rivas",
        "carrera": "Ingeniería de Sistemas",
        "edad": 22,
        "correo": "carlos.mendoza@unsa.edu.pe"
    },
    {
        "id": 3,
        "nombre": "María Elena",
        "apellido": "Flores Quispe",
        "carrera": "Ingeniería de Software",
        "edad": 20,
        "correo": "mfloresq@unsa.edu.pe"
    }
]

# Contador para generar IDs únicos auto-incrementales
id_counter = 4

# Expresión regular para validar el formato de correo electrónico
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

def validar_datos_estudiante(data, es_actualizacion=False):
    """
    Valida los datos enviados en la petición para crear o actualizar un estudiante.
    Retorna (True, None) si los datos son válidos.
    Retorna (False, mensaje_error) si se encuentra alguna inconsistencia.
    """
    campos_requeridos = ["nombre", "apellido", "carrera", "edad", "correo"]
    
    # Si no es actualización, todos los campos son estrictamente requeridos.
    # En PUT, validamos que todos los campos requeridos estén presentes en la petición.
    for campo in campos_requeridos:
        if campo not in data:
            return False, f"El campo '{campo}' es requerido."
        
        # Validar que los campos de texto no estén vacíos o solo tengan espacios
        if isinstance(data[campo], str) and not data[campo].strip():
            return False, f"El campo '{campo}' no puede estar vacío."

    # Validar tipos de datos
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    carrera = data.get("carrera")
    edad = data.get("edad")
    correo = data.get("correo")

    if not isinstance(nombre, str) or len(nombre.strip()) < 2:
        return False, "El nombre debe ser una cadena de texto de al menos 2 caracteres."

    if not isinstance(apellido, str) or len(apellido.strip()) < 2:
        return False, "El apellido debe ser una cadena de texto de al menos 2 caracteres."

    if not isinstance(carrera, str) or len(carrera.strip()) < 3:
        return False, "La carrera debe ser una cadena de texto de al menos 3 caracteres."

    # Validar edad
    try:
        edad_int = int(edad)
        if edad_int <= 0 or edad_int > 120:
            return False, "La edad debe ser un número entero válido entre 1 y 120 años."
    except (ValueError, TypeError):
        return False, "La edad debe ser un número entero válido."

    # Validar correo electrónico
    if not isinstance(correo, str) or not re.match(EMAIL_REGEX, correo):
        return False, "El correo electrónico provisto no tiene un formato válido."

    return True, None


# ==========================================
# RUTAS DE LA API RESTFUL
# ==========================================

@app.route('/estudiantes', methods=['GET'])
def obtener_estudiantes():
    """
    GET /estudiantes
    Retorna la lista completa de estudiantes en formato JSON.
    """
    return jsonify(estudiantes_db), 200


@app.route('/estudiantes/<int:estudiante_id>', methods=['GET'])
def obtener_estudiante_por_id(estudiante_id):
    """
    GET /estudiantes/<id>
    Retorna los datos de un estudiante específico.
    """
    estudiante = next((e for e in estudiantes_db if e["id"] == estudiante_id), None)
    if estudiante is None:
        return jsonify({"error": "Estudiante no encontrado", "id": estudiante_id}), 404
    return jsonify(estudiante), 200


@app.route('/estudiantes', methods=['POST'])
def registrar_estudiante():
    """
    POST /estudiantes
    Registra un nuevo estudiante a partir del cuerpo JSON recibido.
    """
    global id_counter
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No se recibieron datos JSON válidos."}), 400

    # Validar los datos
    es_valido, error_msg = validar_datos_estudiante(data)
    if not es_valido:
        return jsonify({"error": error_msg}), 400

    # Verificar si el correo ya está registrado por otro estudiante
    correo = data.get("correo").strip().lower()
    correo_duplicado = any(e["correo"].lower() == correo for e in estudiantes_db)
    if correo_duplicado:
        return jsonify({"error": f"El correo electrónico '{correo}' ya se encuentra registrado."}), 400

    # Crear el nuevo estudiante
    nuevo_estudiante = {
        "id": id_counter,
        "nombre": data.get("nombre").strip(),
        "apellido": data.get("apellido").strip(),
        "carrera": data.get("carrera").strip(),
        "edad": int(data.get("edad")),
        "correo": correo
    }
    
    estudiantes_db.append(nuevo_estudiante)
    id_counter += 1
    
    return jsonify(nuevo_estudiante), 201


@app.route('/estudiantes/<int:estudiante_id>', methods=['PUT'])
def actualizar_estudiante(estudiante_id):
    """
    PUT /estudiantes/<id>
    Actualiza los datos de un estudiante existente.
    """
    estudiante = next((e for e in estudiantes_db if e["id"] == estudiante_id), None)
    if estudiante is None:
        return jsonify({"error": "Estudiante no encontrado", "id": estudiante_id}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos JSON válidos."}), 400

    # Validar los datos recibidos
    es_valido, error_msg = validar_datos_estudiante(data, es_actualizacion=True)
    if not es_valido:
        return jsonify({"error": error_msg}), 400

    # Verificar si el correo ya está registrado por otro estudiante diferente al actual
    correo = data.get("correo").strip().lower()
    correo_duplicado = any(e["correo"].lower() == correo and e["id"] != estudiante_id for e in estudiantes_db)
    if correo_duplicado:
        return jsonify({"error": f"El correo electrónico '{correo}' ya está registrado por otro estudiante."}), 400

    # Actualizar los campos del estudiante
    estudiante["nombre"] = data.get("nombre").strip()
    estudiante["apellido"] = data.get("apellido").strip()
    estudiante["carrera"] = data.get("carrera").strip()
    estudiante["edad"] = int(data.get("edad"))
    estudiante["correo"] = correo

    return jsonify(estudiante), 200


@app.route('/estudiantes/<int:estudiante_id>', methods=['DELETE'])
def eliminar_estudiante(estudiante_id):
    """
    DELETE /estudiantes/<id>
    Elimina a un estudiante de la base de datos en memoria.
    """
    global estudiantes_db
    estudiante = next((e for e in estudiantes_db if e["id"] == estudiante_id), None)
    
    if estudiante is None:
        return jsonify({"error": "Estudiante no encontrado", "id": estudiante_id}), 404

    # Eliminar en sitio (in-place) para mantener consistencia de referencias
    estudiantes_db[:] = [e for e in estudiantes_db if e["id"] != estudiante_id]
    
    return jsonify({
        "success": True,
        "mensaje": f"Estudiante con ID {estudiante_id} eliminado exitosamente."
    }), 200


# ==========================================
# RUTA DEL CLIENTE WEB
# ==========================================

@app.route('/')
def index():
    """
    Renderiza la interfaz principal del cliente que consume la API.
    """
    return render_template('index.html')


if __name__ == '__main__':
    # Ejecuta el servidor local en modo debug en el puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
