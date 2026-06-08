package soap;
 
import jakarta.jws.WebMethod;
import jakarta.jws.WebService;
 
@WebService
public class VentasSOAP {
 
    @WebMethod
    public String obtenerProducto(int id) {
        if (id == 1)
            return "Laptop - S/2500";
        else if (id == 2)
            return "Mouse - S/50";
        else if (id == 3)
            return "Teclado - S/120";
        else
            return "Producto no encontrado";
    }
 
    @WebMethod
    public double calcularTotal(double precio, int cantidad) {
        return precio * cantidad;
    }
 
    @WebMethod
    public double aplicarDescuento(double total) {
        if (total > 1000)
            return total * 0.90;
        return total;
    }
}