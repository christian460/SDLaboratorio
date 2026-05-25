package grpc_calculator;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;

/**
 * Servidor gRPC para la Calculadora Distribuida.
 * Escucha en el puerto 50051 y registra el servicio CalculatorServiceImpl.
 */
public class CalculatorServer {

    private static final int PORT = 50051;

    public static void main(String[] args) throws IOException, InterruptedException {

        // Construye el servidor en el puerto indicado y registra el servicio
        Server server = ServerBuilder
                .forPort(PORT)
                .addService(new CalculatorServiceImpl())
                .build();

        server.start();
        System.out.println("========================================");
        System.out.println(" Servidor gRPC iniciado en puerto " + PORT);
        System.out.println(" Esperando conexiones...");
        System.out.println("========================================");

        // para apagar el servidor limpiamente con Ctrl+C
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("\n[Servidor] Apagando servidor...");
            server.shutdown();
            System.out.println("[Servidor] Servidor detenido.");
        }));

        // Bloquea el hilo principal hasta que el servidor se detenga
        server.awaitTermination();
    }
}
