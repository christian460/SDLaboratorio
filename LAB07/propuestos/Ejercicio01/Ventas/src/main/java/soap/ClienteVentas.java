package soap;
 
import soap.client.VentasSOAP;
import soap.client.VentasSOAPService;
 
public class ClienteVentas {
 
    public static void main(String[] args) {
 
        VentasSOAPService service = new VentasSOAPService();
        VentasSOAP ventas = service.getVentasSOAPPort();
 
        // Consultar productos
        System.out.println(ventas.obtenerProducto(1));
        System.out.println(ventas.obtenerProducto(2));
        System.out.println(ventas.obtenerProducto(3));
 
        // Calcular total: 2 Laptops a S/2500
        double total = ventas.calcularTotal(2500, 2);
        System.out.println("Total: S/" + total);
 
        // Aplicar descuento (aplica porque total > 1000)
        double conDescuento = ventas.aplicarDescuento(total);
        System.out.println("Total con descuento: S/" + conDescuento);
    }
}