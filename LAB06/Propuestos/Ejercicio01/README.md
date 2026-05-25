# Sistema de Gestión Académica (SGA) - API RESTful y Cliente Web

Este proyecto es una aplicación web SPA (Single Page Application) completa construida en Python con el framework **Flask**. Implementa un servicio de API RESTful para la gestión de datos de estudiantes, además de un cliente consumidor con un diseño moderno, elegante y totalmente adaptivo (responsive) usando CSS Vanilla con efectos de *Glassmorphism* (efecto translúcido) y animaciones de interacción dinámicas.

---

## 📂 Estructura del Proyecto

El proyecto está organizado siguiendo las mejores prácticas de estructuración de Flask:

```text
/proyecto
 ├── app.py                  # Servidor Flask, lógica de negocio de la API y persistencia en memoria
 ├── README.md               # Documentación completa del proyecto (esta guía)
 ├── templates/
 │    └── index.html         # Plantilla HTML5 principal del cliente consumidor
 └── static/
      ├── css/
      │    └── style.css     # Estilos CSS Vanilla premium (Glassmorphism, variables, dark mode)
      └── js/
           └── main.js       # Lógica del cliente: consumo AJAX (Fetch API) y actualización dinámica
```

---

## 🚀 Requisitos e Instalación

### Prerrequisitos
- Python 3.8 o superior instalado en el sistema.
- Gestor de paquetes `pip` disponible.

### Paso 1: Clonar o copiar el proyecto
Ubícate en la carpeta raíz del proyecto donde se encuentran los archivos.

### Paso 2: Instalar dependencias
Instala Flask utilizando `pip`:
```bash
pip install flask
```

### Paso 3: Ejecutar la aplicación
Inicia el servidor Flask ejecutando el archivo `app.py`:
```bash
python app.py
```

El servidor web se levantará localmente en la dirección: **`http://localhost:5000`**

---

## 🌐 Documentación de la API RESTful

La API maneja almacenamiento simple en memoria (`in-memory database`) representado por una lista de diccionarios que se reinicia cuando el servidor se apaga. Utiliza códigos de estado HTTP estándar (200, 201, 400, 404) y devuelve respuestas claras en formato JSON.

### Resumen de Endpoints

| Método | Endpoint | Descripción | Código de Éxito |
| :--- | :--- | :--- | :--- |
| **GET** | `/estudiantes` | Consultar la lista de todos los estudiantes | `200 OK` |
| **GET** | `/estudiantes/<id>` | Consultar detalles de un estudiante por ID | `200 OK` / `404 Not Found` |
| **POST** | `/estudiantes` | Registrar un nuevo estudiante | `201 Created` / `400 Bad Request` |
| **PUT** | `/estudiantes/<id>` | Actualizar los datos de un estudiante existente | `200 OK` / `400 BR` / `404 NF` |
| **DELETE**| `/estudiantes/<id>` | Eliminar un estudiante del sistema | `200 OK` / `404 Not Found` |

---

### 1. Consultar Estudiantes (`GET /estudiantes`)
Retorna la lista de todos los estudiantes.

- **Comando `curl`:**
  ```bash
  curl -X GET http://127.0.0.1:5000/estudiantes
  ```
- **Respuesta JSON de ejemplo (200 OK):**
  ```json
  [
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
    }
  ]
  ```

---

### 2. Registrar Estudiante (`POST /estudiantes`)
Crea un nuevo estudiante y le asigna un ID único de forma automática.

- **Ejemplo de Payload JSON para la Petición:**
  ```json
  {
    "nombre": "Luis Gustavo",
    "apellido": "Apaza Condori",
    "carrera": "Ciencia de la Computación",
    "edad": 23,
    "correo": "lapazac@unsa.edu.pe"
  }
  ```
- **Comando `curl`:**
  ```bash
  curl -X POST http://127.0.0.1:5000/estudiantes \
    -H "Content-Type: application/json" \
    -d "{\"nombre\": \"Luis Gustavo\", \"apellido\": \"Apaza Condori\", \"carrera\": \"Ciencia de la Computación\", \"edad\": 23, \"correo\": \"lapazac@unsa.edu.pe\"}"
  ```
- **Respuesta JSON de ejemplo (201 Created):**
  ```json
  {
    "id": 4,
    "nombre": "Luis Gustavo",
    "apellido": "Apaza Condori",
    "carrera": "Ciencia de la Computación",
    "edad": 23,
    "correo": "lapazac@unsa.edu.pe"
  }
  ```
- **Respuesta de error por datos inválidos o duplicados (400 Bad Request):**
  ```json
  {
    "error": "El correo electrónico 'lapazac@unsa.edu.pe' ya se encuentra registrado."
  }
  ```

---

### 3. Actualizar Estudiante (`PUT /estudiantes/<id>`)
Modifica los datos de un estudiante existente usando su ID numérico.

- **Ejemplo de Payload JSON para la Petición:**
  ```json
  {
    "nombre": "Ana Sofia Modificado",
    "apellido": "García Torres",
    "carrera": "Ciencia de la Computación",
    "edad": 22,
    "correo": "ana.garcia@unsa.edu.pe"
  }
  ```
- **Comando `curl`:**
  ```bash
  curl -X PUT http://127.0.0.1:5000/estudiantes/1 \
    -H "Content-Type: application/json" \
    -d "{\"nombre\": \"Ana Sofia Modificado\", \"apellido\": \"García Torres\", \"carrera\": \"Ciencia de la Computación\", \"edad\": 22, \"correo\": \"ana.garcia@unsa.edu.pe\"}"
  ```
- **Respuesta JSON de ejemplo (200 OK):**
  ```json
  {
    "id": 1,
    "nombre": "Ana Sofia Modificado",
    "apellido": "García Torres",
    "carrera": "Ciencia de la Computación",
    "edad": 22,
    "correo": "ana.garcia@unsa.edu.pe"
  }
  ```
- **Respuesta de error si el estudiante no existe (404 Not Found):**
  ```json
  {
    "error": "Estudiante no encontrado",
    "id": 999
  }
  ```

---

### 4. Eliminar Estudiante (`DELETE /estudiantes/<id>`)
Remueve permanentemente a un estudiante del almacenamiento temporal.

- **Comando `curl`:**
  ```bash
  curl -X DELETE http://127.0.0.1:5000/estudiantes/1
  ```
- **Respuesta JSON de ejemplo (200 OK):**
  ```json
  {
    "success": true,
    "mensaje": "Estudiante con ID 1 eliminado exitosamente."
  }
  ```

---

## 📸 Guía para Capturar Evidencias de Funcionamiento

Para documentar y demostrar la correcta ejecución del sistema, se recomienda realizar y capturar las siguientes pantallas de evidencia:

### 1. Evidencia de la API Funcionando
- **Herramienta:** Postman, Insomnia o terminal.
- **Acción:** Realiza una petición `GET` a `/estudiantes` y una petición `POST` a `/estudiantes`.
- **Qué capturar:** Toda la pantalla de Postman donde se vea la URL (`http://127.0.0.1:5000/estudiantes`), el verbo HTTP correspondiente, el payload JSON enviado (para el POST), el **código de estado** (200 OK o 201 Created) y el JSON devuelto en el panel inferior.

### 2. Evidencia de la Interfaz Web Funcionando (Cliente Consumidor)
- **Herramienta:** Navegador web (Chrome, Edge o Firefox).
- **Acción:** Acceder a `http://localhost:5000/` y ver la interfaz general.
- **Qué capturar:** El diseño responsivo de la página, mostrando la barra de navegación superior (con el contador de alumnos), el formulario en la columna izquierda y las tarjetas de estudiantes representados en la tabla con sus colores de diseño modernos y oscuros.

### 3. Evidencia de la Comunicación Cliente-API
- **Herramienta:** Consola de Desarrollador del Navegador (presionar `F12` y seleccionar la pestaña **Network** o **Red**).
- **Acción:** Registra a un nuevo estudiante en el formulario de la interfaz y presiona el botón "Registrar Estudiante".
- **Qué capturar:** La pantalla del navegador dividida. En un lado se debe ver el **Toast flotante** verde de éxito que dice *"Registrado: Estudiante ha sido ingresado al sistema"*, y en el panel de herramientas de desarrollo (pestaña Network) se debe ver la petición **`POST estudiantes`** con estado **`201`** completada de fondo sin recargar la página.
