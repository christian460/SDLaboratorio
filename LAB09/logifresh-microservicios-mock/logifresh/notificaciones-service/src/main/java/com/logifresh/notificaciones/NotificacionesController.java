package com.logifresh.notificaciones;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Mock del Servicio de Notificaciones.
 *
 * Simula intencionalmente los "retrasos en las confirmaciones por correo
 * electrónico" reportados por LogiFresh, asumiendo que el envío de correos
 * pasa por un proveedor externo cuya latencia es variable y, en algunos
 * casos, ocasiona el encolamiento tardío del mensaje.
 */
@RestController
@RequestMapping("/api/notificaciones")
public class NotificacionesController {

    private final AtomicLong idGenerator = new AtomicLong(9000);

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of("service", "notificaciones-service", "status", "UP"));
    }

    @PostMapping("/enviar")
    public ResponseEntity<Map<String, Object>> enviarNotificacion(@RequestBody Map<String, Object> body) {
        int dado = ThreadLocalRandom.current().nextInt(100);
        int delayMs;
        String canal = String.valueOf(body.getOrDefault("canal", "email"));

        if (dado < 75) {
            delayMs = ThreadLocalRandom.current().nextInt(50, 300); // envío normal
        } else {
            // 25% de las notificaciones (sobre todo por correo) sufren retraso
            // significativo, simulando saturación del proveedor de email durante
            // campañas de alta demanda.
            delayMs = ThreadLocalRandom.current().nextInt(3000, 10000);
        }

        try {
            Thread.sleep(delayMs);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        long notificacionId = idGenerator.incrementAndGet();
        Map<String, Object> respuesta = Map.of(
                "notificacionId", notificacionId,
                "destinatario", body.getOrDefault("destinatario", "desconocido"),
                "canal", canal,
                "latenciaMs", delayMs,
                "estado", "ENVIADA"
        );
        return ResponseEntity.ok(respuesta);
    }
}
