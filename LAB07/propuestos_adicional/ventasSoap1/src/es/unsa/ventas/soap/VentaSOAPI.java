package es.unsa.ventas.soap;

import java.util.List;
import javax.jws.WebMethod;
import javax.jws.WebService;
import es.unsa.ventas.model.Producto;

@WebService
public interface VentaSOAPI {

    @WebMethod
    public List<Producto> listarProductos();

    @WebMethod
    public Producto buscarProducto(int id);

    @WebMethod
    public void agregarProducto(Producto producto);

    @WebMethod
    public boolean actualizarStock(int id, int nuevoStock);

    @WebMethod
    public boolean eliminarProducto(int id);
}
