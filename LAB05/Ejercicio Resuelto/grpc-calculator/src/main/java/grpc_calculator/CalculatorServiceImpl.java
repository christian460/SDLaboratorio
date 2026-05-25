package grpc_calculator;

import io.grpc.stub.StreamObserver;
import grpc_calculator.CalculatorProto.Request;
import grpc_calculator.CalculatorProto.Response;


 //Implementación del servicio Calculator definido en calculator.proto.
 //Extiende la clase base generada por el compilador de Protocol Buffers.

public class CalculatorServiceImpl extends CalculatorGrpc.CalculatorImplBase {

     //Método Sum: recibe dos enteros (a, b) y retorna su suma.

    
    @Override
    public void sum(Request req, StreamObserver<Response> responseObserver) {
        System.out.println("[Servidor] Solicitud recibida: a=" + req.getA() + ", b=" + req.getB());

        int result = req.getA() + req.getB();

        Response response = Response.newBuilder()
                .setResult(result)
                .build();

        // Envía la respuesta al cliente
        responseObserver.onNext(response);

        // Indica que la llamada RPC ha finalizado
        responseObserver.onCompleted();

        System.out.println("[Servidor] Respuesta enviada: resultado=" + result);
    }
}
