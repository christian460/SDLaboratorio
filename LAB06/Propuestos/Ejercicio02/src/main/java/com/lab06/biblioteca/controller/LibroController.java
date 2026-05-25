package com.lab06.biblioteca.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/libros")
@CrossOrigin(origins = "*")
public class LibroController {

    // Almacenamiento en memoria (lista de mapas) con datos de prueba iniciales
    private final List<Map<String, Object>> libros = new ArrayList<>();
    private int idCounter = 4;

    public LibroController() {
        Map<String, Object> l1 = new HashMap<>();
        l1.put("id", 1); l1.put("titulo", "El Quijote");
        l1.put("autor", "Miguel de Cervantes"); l1.put("anio", 1605);
        libros.add(l1);

        Map<String, Object> l2 = new HashMap<>();
        l2.put("id", 2); l2.put("titulo", "Cien anos de soledad");
        l2.put("autor", "Gabriel Garcia Marquez"); l2.put("anio", 1967);
        libros.add(l2);

        Map<String, Object> l3 = new HashMap<>();
        l3.put("id", 3); l3.put("titulo", "La ciudad y los perros");
        l3.put("autor", "Mario Vargas Llosa"); l3.put("anio", 1963);
        libros.add(l3);
    }

    // GET /libros - Consultar todos los libros
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> listar() {
        return ResponseEntity.ok(libros);
    }

    // POST /libros - Registrar un libro
    @PostMapping
    public ResponseEntity<Map<String, Object>> agregar(@RequestBody Map<String, Object> datos) {
        // Validar campos requeridos
        if (datos.get("titulo") == null || datos.get("titulo").toString().isBlank()) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "El campo 'titulo' es requerido.");
            return ResponseEntity.badRequest().body(error);
        }
        if (datos.get("autor") == null || datos.get("autor").toString().isBlank()) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "El campo 'autor' es requerido.");
            return ResponseEntity.badRequest().body(error);
        }

        // Crear nuevo libro con ID autoincremental
        Map<String, Object> nuevoLibro = new HashMap<>();
        nuevoLibro.put("id", idCounter++);
        nuevoLibro.put("titulo", datos.get("titulo").toString().trim());
        nuevoLibro.put("autor",  datos.get("autor").toString().trim());
        nuevoLibro.put("anio",   datos.getOrDefault("anio", 0));
        libros.add(nuevoLibro);

        Map<String, Object> respuesta = new HashMap<>();
        respuesta.put("ok", true);
        respuesta.put("mensaje", "Libro registrado correctamente.");
        respuesta.put("libro", nuevoLibro);
        return ResponseEntity.status(HttpStatus.CREATED).body(respuesta);
    }

    // GET /libros/{id} - Buscar libro por ID
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> buscar(@PathVariable int id) {
        Map<String, Object> libro = libros.stream()
                .filter(l -> ((int) l.get("id")) == id)
                .findFirst()
                .orElse(null);

        if (libro == null) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Libro no encontrado.");
            error.put("id", id);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        }
        return ResponseEntity.ok(libro);
    }

    // DELETE /libros/{id} - Eliminar libro
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> eliminar(@PathVariable int id) {
        boolean eliminado = libros.removeIf(l -> ((int) l.get("id")) == id);

        Map<String, Object> respuesta = new HashMap<>();
        if (!eliminado) {
            respuesta.put("error", "Libro no encontrado.");
            respuesta.put("id", id);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(respuesta);
        }
        respuesta.put("eliminado", true);
        respuesta.put("mensaje", "Libro con ID " + id + " eliminado correctamente.");
        return ResponseEntity.ok(respuesta);
    }
}
