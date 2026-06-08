package es.unsa.ventas;

import javax.xml.ws.Endpoint;
import es.unsa.ventas.soap.VentaSOAPImpl;

public class PublishServices {

    public static void main(String[] args) {
        /*
         * Se publican los servicios a través de un servidor virtual JAX-WS.
         * El puerto puede ser cualquiera que esté libre en el sistema.
         * Una vez ejecutada la aplicación, se publica el contrato WSDL.
         * Verificar en: http://localhost:1617/WS/Ventas?wsdl
         */
        String url = "http://localhost:1617/WS/Ventas";
        System.out.println("Publicando servicio SOAP en: " + url);
        Endpoint.publish(url, new VentaSOAPImpl());
        System.out.println("Servicio publicado exitosamente.");
        System.out.println("WSDL disponible en: " + url + "?wsdl");
    }
}
