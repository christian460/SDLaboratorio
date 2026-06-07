package soap;

import jakarta.xml.ws.Endpoint;

public class Publisher {

    public static void main(String[] args) {

        Endpoint.publish(
            "http://localhost:8080/conversor",
            new ConversorSOAP()
        );

        System.out.println("Servicio SOAP iniciado");
        System.out.println("WSDL:");
        System.out.println("http://localhost:8080/conversor?wsdl");
    }
}