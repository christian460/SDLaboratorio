# LogiFresh S.A. — Entorno Mock de Microservicios

Entorno base para el Laboratorio 9 (Sistemas Distribuidos) que simula la
arquitectura de microservicios de LogiFresh S.A. Incluye 5 servicios REST
mock (sin lógica de negocio real) pensados para que el equipo de QA pueda
ejecutar pruebas funcionales, de integración y de carga.

## Servicios y puertos

| Servicio        | Puerto | Endpoint principal                          |
|-----------------|--------|----------------------------------------------|
| Pedidos         | 8081   | POST /api/pedidos                            |
| Inventario      | 8082   | GET/POST /api/inventario/{producto}          |
| Facturación     | 8083   | POST /api/facturas                           |
| Transporte      | 8084   | POST /api/transporte/asignar                 |
| Notificaciones  | 8085   | POST /api/notificaciones/enviar              |

Todos los servicios expuestos un endpoint `/api/<recurso>/health`.

## Defectos simulados intencionalmente (para que las pruebas los detecten)

- **Pedidos**: latencia variable; ~10% de las solicitudes superan los 8000 ms
  (reproduce la lentitud reportada). Además, el descuento solo se aplica
  ~60% de las veces aunque exista código de promoción (reproduce "pedidos
  sin descuento aplicado").
- **Inventario**: ventana de inconsistencia simulada entre lectura y
  escritura del stock al reservar (reproduce "inventario inconsistente").
- **Facturación**: ~50% de probabilidad de no detectar idempotencia en
  reintentos para el mismo pedido (reproduce "facturas duplicadas").
- **Transporte**: ~15% de las solicitudes devuelven 503 (simula
  indisponibilidad, útil para Circuit Breaker / reintentos).
- **Notificaciones**: ~25% de los envíos sufren retraso de 3 a 10 segundos
  (reproduce "retrasos en confirmaciones por correo").

## Cómo levantar el entorno

Requisitos: Docker Desktop y Docker Compose.

```bash
docker compose build
docker compose up -d
docker compose ps
```

Para detener y limpiar:

```bash
docker compose down
```

## Ejemplos rápidos de prueba (curl)

```bash
# Crear un pedido con promoción
curl -X POST http://localhost:8081/api/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Supermercado Central","monto":250.0,"codigoPromocion":"VERANO10"}'

# Consultar stock
curl http://localhost:8082/api/inventario/yogurt-natural-1L

# Reservar stock
curl -X POST http://localhost:8082/api/inventario/yogurt-natural-1L/reservar \
  -H "Content-Type: application/json" \
  -d '{"cantidad":5}'

# Generar factura
curl -X POST http://localhost:8083/api/facturas \
  -H "Content-Type: application/json" \
  -d '{"pedidoId":1001,"monto":250.0}'

# Asignar transporte
curl -X POST http://localhost:8084/api/transporte/asignar \
  -H "Content-Type: application/json" \
  -d '{"pedidoId":1001}'

# Enviar notificación
curl -X POST http://localhost:8085/api/notificaciones/enviar \
  -H "Content-Type: application/json" \
  -d '{"destinatario":"cliente@correo.com","canal":"email"}'
```

## Uso recomendado para JMeter / k6

Apuntar las pruebas de carga (Actividad 4 del laboratorio) principalmente al
endpoint `POST http://localhost:8081/api/pedidos`, ya que es el que reproduce
la lentitud reportada por los clientes (registros que tardan más de 8
segundos durante campañas de alta demanda).
