package es.unsa.ventas.client;

// NOTA: Este cliente se genera DESPUÉS de correr wsimport contra el WSDL.
// Ver README.txt para instrucciones completas.
// Las clases del stub (VentaSOAPIService, VentaSOAPI, Producto)
// se generan automáticamente por wsimport.

// Ejemplo de uso tras generar el stub con wsimport:
/*
import es.unsa.ventas.soap.*;
import java.util.Arrays;

public class VentaClient {
    public static void main(String[] args) throws Exception {
        VentaSOAPIService service = new VentaSOAPIService();
        VentaSOAPI port = service.getVentaSOAPIPort();

        // Listar productos
        System.out.println("=== LISTA DE PRODUCTOS ===");
        for (Producto p : port.listarProductos()) {
            System.out.println(p);
        }

        // Agregar nuevo producto
        Producto nuevo = new Producto();
        nuevo.setId(5);
        nuevo.setNombre("Webcam HD");
        nuevo.setCategoria("Accesorios");
        nuevo.setPrecio(150.00);
        nuevo.setStock(20);
        port.agregarProducto(nuevo);
        System.out.println("\nProducto agregado: " + nuevo.getNombre());

        // Buscar producto por ID
        Producto encontrado = port.buscarProducto(1);
        System.out.println("\nProducto encontrado: " + encontrado.getNombre());

        // Actualizar stock
        boolean actualizado = port.actualizarStock(1, 8);
        System.out.println("\nStock actualizado: " + actualizado);

        // Listar después de cambios
        System.out.println("\n=== LISTA ACTUALIZADA ===");
        for (Producto p : port.listarProductos()) {
            System.out.println(p);
        }
    }
}
*/

public class VentaClient {
    public static void main(String[] args) {
        System.out.println("Genera el stub con wsimport y descomenta el código de arriba.");
        System.out.println("Comando: wsimport -keep -s src http://localhost:1617/WS/Ventas?wsdl");
    }
}
