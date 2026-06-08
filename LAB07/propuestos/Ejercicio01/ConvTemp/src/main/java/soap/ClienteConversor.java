package soap;

import soap.client.ConversorSOAP;
import soap.client.ConversorSOAPService;

public class ClienteConversor {

    public static void main(String[] args) {

        ConversorSOAPService service = new ConversorSOAPService();

        ConversorSOAP port = service.getConversorSOAPPort();

        System.out.println("30°C = " + port.cToF(30) + "°F");
        System.out.println("86°F = " + port.fToC(86) + "°C");
    }
}