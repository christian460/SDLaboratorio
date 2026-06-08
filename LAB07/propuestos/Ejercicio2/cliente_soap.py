from zeep import Client


# WSDL del servicio SOAP de calculadora pública.
# Zeep lee el contrato del servicio desde esta URL y expone sus operaciones.
WSDL_URL = "http://www.dneonline.com/calculator.asmx?WSDL"


client = Client(WSDL_URL)

# Operación principal solicitada en el ejercicio.
resultado = client.service.Add(5, 8)

print("Add(5, 8) =", resultado)

# Pruebas adicionales para verificar las demás operaciones del servicio.
print("Subtract(10, 3) =", client.service.Subtract(10, 3))
print("Multiply(4, 6) =", client.service.Multiply(4, 6))
print("Divide(20, 4) =", client.service.Divide(20, 4))

