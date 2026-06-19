package com.logifresh.inventario;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Mock del Servicio de Inventario.
 *
 * Simula intencionalmente el problema de "inventario inconsistente" reportado
 * por LogiFresh: al reservar stock concurrentemente (sin bloqueo correcto),
 * el contador puede quedar desincronizado, lo que permite condiciones de
 * carrera detectables en pruebas de integración / concurrencia.
 */
@RestController
@RequestMapping("/api/inventario")
public class InventarioController {

    // Stock inicial simulado por producto
    private final ConcurrentHashMap<String, Integer> stock = new ConcurrentHashMap<>();

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of("service", "inventario-service", "status", "UP"));
    }

    @GetMapping("/{producto}")
    public ResponseEntity<Map<String, Object>> consultarStock(@PathVariable String producto) {
        int actual = stock.computeIfAbsent(producto, p -> ThreadLocalRandom.current().nextInt(20, 100));
        return ResponseEntity.ok(Map.of("producto", producto, "stockDisponible", actual));
    }

    /**
     * Reserva unidades de un producto. BUG SIMULADO: la lectura y la escritura
     * del stock no son atómicas (se simula una pequeña ventana de tiempo entre
     * leer y escribir), lo que reproduce el escenario de inventario inconsistente
     * bajo solicitudes concurrentes durante campañas de alta demanda.
     */
    @PostMapping("/{producto}/reservar")
    public ResponseEntity<Map<String, Object>> reservarStock(@PathVariable String producto,
                                                               @RequestBody Map<String, Object> body) {
        int cantidad = parseCantidad(body.get("cantidad"));

        int actual = stock.computeIfAbsent(producto, p -> ThreadLocalRandom.current().nextInt(20, 100));

        // Ventana de inconsistencia simulada (no atómica a propósito)
        try {
            Thread.sleep(ThreadLocalRandom.current().nextInt(10, 80));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        boolean haySuficiente = actual >= cantidad;
        int nuevoStock = haySuficiente ? actual - cantidad : actual;
        stock.put(producto, nuevoStock);

        Map<String, Object> respuesta = Map.of(
                "producto", producto,
                "cantidadSolicitada", cantidad,
                "stockAntes", actual,
                "stockDespues", nuevoStock,
                "reservaExitosa", haySuficiente
        );
        return ResponseEntity.ok(respuesta);
    }

    private int parseCantidad(Object raw) {
        if (raw == null) return 0;
        try {
            return Integer.parseInt(String.valueOf(raw));
        } catch (NumberFormatException e) {
            return 0;
        }
    }
}
