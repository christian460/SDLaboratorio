package com.logifresh.transporte;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Mock del Servicio de Transporte.
 *
 * Incluye una probabilidad de fallo (simulando caída momentánea o
 * indisponibilidad del servicio externo de logística) útil para la
 * Actividad 3 (pruebas de integración Pedido <-> Transporte) y para
 * ejercitar mecanismos de recuperación / circuit breaker.
 */
@RestController
@RequestMapping("/api/transporte")
public class TransporteController {

    private final AtomicLong idGenerator = new AtomicLong(7000);

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of("service", "transporte-service", "status", "UP"));
    }

    @PostMapping("/asignar")
    public ResponseEntity<Map<String, Object>> asignarTransporte(@RequestBody Map<String, Object> body) {
        // ~15% de las solicitudes simulan una falla de disponibilidad del servicio,
        // útil para probar reintentos, timeouts y circuit breaker.
        if (ThreadLocalRandom.current().nextInt(100) < 15) {
            return ResponseEntity.status(503).body(Map.of(
                    "error", "Servicio de transporte temporalmente no disponible",
                    "pedidoId", body.getOrDefault("pedidoId", "desconocido")
            ));
        }

        long transporteId = idGenerator.incrementAndGet();
        Map<String, Object> respuesta = Map.of(
                "transporteId", transporteId,
                "pedidoId", body.getOrDefault("pedidoId", "desconocido"),
                "estado", "ASIGNADO",
                "vehiculoAsignado", "REFR-" + ThreadLocalRandom.current().nextInt(100, 999)
        );
        return ResponseEntity.ok(respuesta);
    }

    @GetMapping("/{transporteId}")
    public ResponseEntity<Map<String, Object>> obtenerTransporte(@PathVariable long transporteId) {
        return ResponseEntity.ok(Map.of("transporteId", transporteId, "estado", "ASIGNADO"));
    }
}
