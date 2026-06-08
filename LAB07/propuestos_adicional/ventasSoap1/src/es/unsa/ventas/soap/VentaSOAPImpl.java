package es.unsa.ventas.soap;

import java.util.List;
import javax.jws.WebService;
import es.unsa.ventas.model.Producto;

@WebService(endpointInterface = "es.unsa.ventas.soap.VentaSOAPI")
public class VentaSOAPImpl implements VentaSOAPI {

    @Override
    public List<Producto> listarProductos() {
        return Producto.getProductos();
    }

    @Override
    public Producto buscarProducto(int id) {
        for (Producto p : Producto.getProductos()) {
            if (p.id == id) return p;
        }
        return null;
    }

    @Override
    public void agregarProducto(Producto producto) {
        Producto.getProductos().add(producto);
    }

    @Override
    public boolean actualizarStock(int id, int nuevoStock) {
        for (Producto p : Producto.getProductos()) {
            if (p.id == id) {
                p.stock = nuevoStock;
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean eliminarProducto(int id) {
        return Producto.getProductos().removeIf(p -> p.id == id);
    }
}
