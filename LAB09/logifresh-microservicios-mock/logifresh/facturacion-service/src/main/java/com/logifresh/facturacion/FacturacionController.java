package com.logifresh.facturacion;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Mock del Servicio de Facturación.
 *
 * Simula intencionalmente el problema de "facturas duplicadas" reportado por
 * LogiFresh: el endpoint NO valida correctamente la idempotencia cuando se
 * reciben reintentos para el mismo pedido (algo común cuando el servicio de
 * Pedidos responde con timeout y el cliente reintenta la solicitud).
 */
@RestController
@RequestMapping("/api/facturas")
public class FacturacionController {

    private final AtomicLong idGenerator = new AtomicLong(5000);

    // Mapa pedidoId -> facturaId, usado solo de forma incompleta a propósito.
    private final ConcurrentHashMap<Long, Long> facturasPorPedido = new ConcurrentHashMap<>();

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of("service", "facturacion-service", "status", "UP"));
    }

    /**
     * BUG SIMULADO: si la misma solicitud de facturación para un pedidoId
     * llega más de una vez en un intervalo corto (reintento de cliente o de
     * un servicio upstream), existe ~50% de probabilidad de que NO se
     * detecte la duplicidad y se genere una segunda factura para el mismo pedido.
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> generarFactura(@RequestBody Map<String, Object> body) {
        long pedidoId = parseLong(body.get("pedidoId"));
        double monto = parseMonto(body.get("monto"));

        boolean yaExisteFactura = facturasPorPedido.containsKey(pedidoId);
        boolean fallaValidacionIdempotencia = ThreadLocalRandom.current().nextInt(100) < 50;

        long facturaId;
        boolean duplicada;

        if (yaExisteFactura && !fallaValidacionIdempotencia) {
            // Caso correcto: se detecta la duplicidad y se reutiliza la factura existente
            facturaId = facturasPorPedido.get(pedidoId);
            duplicada = false;
        } else {
            // Caso con bug: se genera una nueva factura aunque ya exista una para el pedido
            facturaId = idGenerator.incrementAndGet();
            facturasPorPedido.put(pedidoId, facturaId);
            duplicada = yaExisteFactura;
        }

        Map<String, Object> respuesta = Map.of(
                "facturaId", facturaId,
                "pedidoId", pedidoId,
                "monto", monto,
                "posibleDuplicidad", duplicada,
                "estado", "EMITIDA"
        );
        return ResponseEntity.ok(respuesta);
    }

    @GetMapping("/{facturaId}")
    public ResponseEntity<Map<String, Object>> obtenerFactura(@PathVariable long facturaId) {
        return ResponseEntity.ok(Map.of("facturaId", facturaId, "estado", "EMITIDA"));
    }

    private long parseLong(Object raw) {
        if (raw == null) return 0L;
        try {
            return Long.parseLong(String.valueOf(raw));
        } catch (NumberFormatException e) {
            return 0L;
        }
    }

    private double parseMonto(Object raw) {
        if (raw == null) return 0.0;
        try {
            return Double.parseDouble(String.valueOf(raw));
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }
}
