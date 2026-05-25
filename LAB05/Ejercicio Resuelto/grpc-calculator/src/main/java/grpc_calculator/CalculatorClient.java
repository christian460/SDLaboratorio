package grpc_calculator;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import grpc_calculator.CalculatorProto.Request;
import grpc_calculator.CalculatorProto.Response;


 //Cliente gRPC para la Calculadora Distribuida.
 //Conecta al servidor en localhost:50051 y realiza una llamada Sum.
 //a=8, b=4 → Resultado esperado: 12
 
public class CalculatorClient {

    public static void main(String[] args) throws InterruptedException {

        

        ManagedChannel channel = ManagedChannelBuilder
                .forAddress("localhost", 50051)
                .usePlaintext()
                .build();

        CalculatorGrpc.CalculatorBlockingStub stub =
                CalculatorGrpc.newBlockingStub(channel);

        Request request = Request.newBuilder()
                .setA(8)
                .setB(4)
                .build();

        Response response = stub.sum(request);

        System.out.println("Resultado: " + response.getResult());

        channel.shutdown();

        
    }
}
