package es.unsa.ventas.model;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Producto implements Serializable {

    private static final long serialVersionUID = 1L;

    public static List<Producto> productos = new ArrayList<>(Arrays.asList(
            new Producto(1, "Laptop HP 15", "Electrónica", 2500.00, 10),
            new Producto(2, "Mouse Logitech", "Accesorios", 85.00, 50),
            new Producto(3, "Teclado Mecánico", "Accesorios", 199.99, 30),
            new Producto(4, "Monitor Samsung 24\"", "Electrónica", 899.00, 15)
    ));

    public int id;
    public String nombre;
    public String categoria;
    public double precio;
    public int stock;

    public Producto() {
        super();
    }

    public Producto(int id, String nombre, String categoria, double precio, int stock) {
        super();
        this.id = id;
        this.nombre = nombre;
        this.categoria = categoria;
        this.precio = precio;
        this.stock = stock;
    }

    public static List<Producto> getProductos() {
        return productos;
    }

    public void setId(int id) { this.id = id; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public void setCategoria(String categoria) { this.categoria = categoria; }
    public void setPrecio(double precio) { this.precio = precio; }
    public void setStock(int stock) { this.stock = stock; }

    @Override
    public String toString() {
        return "Producto [id=" + id + ", nombre=" + nombre +
               ", categoria=" + categoria + ", precio=" + precio +
               ", stock=" + stock + "]";
    }
}
