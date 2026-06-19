package com.logifresh.pedidos;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Mock del Servicio de Pedidos.
 *
 * Simula intencionalmente dos de los problemas reportados por LogiFresh S.A.:
 *  1. Lentitud al registrar pedidos (Thread.sleep aleatorio, a veces > 8s).
 *  2. Pedidos registrados sin descuento aplicado (bug simulado de forma probabilística).
 *
 * Estos defectos son INTENCIONALES para que el equipo de pruebas de carga
 * y de pruebas funcionales pueda detectarlos durante la Actividad 2 y 4.
 */
@RestController
@RequestMapping("/api/pedidos")
public class PedidosController {

    private final AtomicLong idGenerator = new AtomicLong(1000);

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of("service", "pedidos-service", "status", "UP"));
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> crearPedido(@RequestBody Map<String, Object> body) {
        simularLatenciaVariable();

        long pedidoId = idGenerator.incrementAndGet();
        String cliente = String.valueOf(body.getOrDefault("cliente", "desconocido"));
        double monto = parseMonto(body.get("monto"));
        boolean tienePromocion = body.containsKey("codigoPromocion")
                && body.get("codigoPromocion") != null
                && !String.valueOf(body.get("codigoPromocion")).isBlank();

        // BUG SIMULADO: el descuento solo se aplica ~60% de las veces aunque
        // el cliente sí haya enviado un código de promoción válido.
        boolean descuentoAplicado = tienePromocion && ThreadLocalRandom.current().nextInt(100) < 60;
        double montoFinal = descuentoAplicado ? monto * 0.9 : monto;

        Map<String, Object> respuesta = Map.of(
                "pedidoId", pedidoId,
                "cliente", cliente,
                "montoOriginal", monto,
                "tienePromocion", tienePromocion,
                "descuentoAplicado", descuentoAplicado,
                "montoFinal", montoFinal,
                "estado", "REGISTRADO"
        );
        return ResponseEntity.ok(respuesta);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> obtenerPedido(@PathVariable long id) {
        simularLatenciaVariable();
        return ResponseEntity.ok(Map.of(
                "pedidoId", id,
                "estado", "REGISTRADO"
        ));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> cancelarPedido(@PathVariable long id) {
        simularLatenciaVariable();
        return ResponseEntity.ok(Map.of(
                "pedidoId", id,
                "estado", "CANCELADO"
        ));
    }

    /**
     * Simula la lentitud reportada por los clientes. La mayoría de las
     * solicitudes responden rápido (100-600 ms), pero un porcentaje de ellas
     * (simulando saturación en campañas de alta demanda) supera los 8000 ms,
     * que es exactamente el umbral mencionado en el caso de estudio.
     */
    private void simularLatenciaVariable() {
        int delayMs;
        int dado = ThreadLocalRandom.current().nextInt(100);

        if (dado < 70) {
            // 70% de las solicitudes: respuesta normal
            delayMs = ThreadLocalRandom.current().nextInt(100, 600);
        } else if (dado < 90) {
            // 20% de las solicitudes: degradación moderada
            delayMs = ThreadLocalRandom.current().nextInt(600, 4000);
        } else {
            // 10% de las solicitudes: lentitud crítica (> 8 segundos), tal
            // como lo reportan los clientes de LogiFresh en campañas de alta demanda.
            delayMs = ThreadLocalRandom.current().nextInt(8000, 12000);
        }

        try {
            Thread.sleep(delayMs);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
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
