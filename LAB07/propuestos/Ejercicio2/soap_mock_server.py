from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
TNS = "http://tempuri.org/"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def build_wsdl(base_url: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<wsdl:definitions xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:tns="{TNS}"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  targetNamespace="{TNS}">
  <wsdl:types>
    <xsd:schema targetNamespace="{TNS}" elementFormDefault="qualified">
      <xsd:element name="Add">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="intA" type="xsd:int" />
            <xsd:element name="intB" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="AddResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="AddResult" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="Subtract">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="intA" type="xsd:int" />
            <xsd:element name="intB" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="SubtractResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="SubtractResult" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="Multiply">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="intA" type="xsd:int" />
            <xsd:element name="intB" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="MultiplyResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="MultiplyResult" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="Divide">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="intA" type="xsd:int" />
            <xsd:element name="intB" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
      <xsd:element name="DivideResponse">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="DivideResult" type="xsd:int" />
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
  </wsdl:types>
  <wsdl:message name="AddSoapIn">
    <wsdl:part name="parameters" element="tns:Add" />
  </wsdl:message>
  <wsdl:message name="AddSoapOut">
    <wsdl:part name="parameters" element="tns:AddResponse" />
  </wsdl:message>
  <wsdl:message name="SubtractSoapIn">
    <wsdl:part name="parameters" element="tns:Subtract" />
  </wsdl:message>
  <wsdl:message name="SubtractSoapOut">
    <wsdl:part name="parameters" element="tns:SubtractResponse" />
  </wsdl:message>
  <wsdl:message name="MultiplySoapIn">
    <wsdl:part name="parameters" element="tns:Multiply" />
  </wsdl:message>
  <wsdl:message name="MultiplySoapOut">
    <wsdl:part name="parameters" element="tns:MultiplyResponse" />
  </wsdl:message>
  <wsdl:message name="DivideSoapIn">
    <wsdl:part name="parameters" element="tns:Divide" />
  </wsdl:message>
  <wsdl:message name="DivideSoapOut">
    <wsdl:part name="parameters" element="tns:DivideResponse" />
  </wsdl:message>
  <wsdl:portType name="CalculatorSoap">
    <wsdl:operation name="Add">
      <wsdl:input message="tns:AddSoapIn" />
      <wsdl:output message="tns:AddSoapOut" />
    </wsdl:operation>
    <wsdl:operation name="Subtract">
      <wsdl:input message="tns:SubtractSoapIn" />
      <wsdl:output message="tns:SubtractSoapOut" />
    </wsdl:operation>
    <wsdl:operation name="Multiply">
      <wsdl:input message="tns:MultiplySoapIn" />
      <wsdl:output message="tns:MultiplySoapOut" />
    </wsdl:operation>
    <wsdl:operation name="Divide">
      <wsdl:input message="tns:DivideSoapIn" />
      <wsdl:output message="tns:DivideSoapOut" />
    </wsdl:operation>
  </wsdl:portType>
  <wsdl:binding name="CalculatorSoap" type="tns:CalculatorSoap">
    <soap:binding transport="http://schemas.xmlsoap.org/soap/http" style="document" />
    <wsdl:operation name="Add">
      <soap:operation soapAction="{TNS}Add" style="document" />
      <wsdl:input>
        <soap:body use="literal" />
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal" />
      </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="Subtract">
      <soap:operation soapAction="{TNS}Subtract" style="document" />
      <wsdl:input>
        <soap:body use="literal" />
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal" />
      </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="Multiply">
      <soap:operation soapAction="{TNS}Multiply" style="document" />
      <wsdl:input>
        <soap:body use="literal" />
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal" />
      </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="Divide">
      <soap:operation soapAction="{TNS}Divide" style="document" />
      <wsdl:input>
        <soap:body use="literal" />
      </wsdl:input>
      <wsdl:output>
        <soap:body use="literal" />
      </wsdl:output>
    </wsdl:operation>
  </wsdl:binding>
  <wsdl:service name="Calculator">
    <wsdl:port name="CalculatorSoap" binding="tns:CalculatorSoap">
      <soap:address location="{base_url}" />
    </wsdl:port>
  </wsdl:service>
</wsdl:definitions>
"""


def build_response(operation: str, result: int) -> bytes:
    response_name = f"{operation}Response"
    result_name = f"{operation}Result"
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="{SOAP_NS}">
  <soap:Body>
    <{response_name} xmlns="{TNS}">
      <{result_name}>{result}</{result_name}>
    </{response_name}>
  </soap:Body>
</soap:Envelope>
"""
    return xml.encode("utf-8")


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.query.lower() == "wsdl":
            base_url = f"http://{self.headers.get('Host', '127.0.0.1:8000')}/"
            wsdl = build_wsdl(base_url)
            data = wsdl.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_error(404, "Use /?wsdl to get the contract")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        root = ET.fromstring(payload)
        body = root.find(f"{{{SOAP_NS}}}Body")
        if body is None or not list(body):
            self.send_error(400, "Invalid SOAP body")
            return

        request = list(body)[0]
        operation = local_name(request.tag)
        values = {local_name(child.tag): int(child.text) for child in list(request)}
        a = values["intA"]
        b = values["intB"]

        if operation == "Add":
            result = a + b
        elif operation == "Subtract":
            result = a - b
        elif operation == "Multiply":
            result = a * b
        elif operation == "Divide":
            result = a // b
        else:
            self.send_error(400, f"Unsupported operation: {operation}")
            return

        response = build_response(operation, result)
        self.send_response(200)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        # Se mantiene la salida limpia para enfocarse en la respuesta SOAP.
        return


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), CalculatorHandler)
    print("SOAP mock disponible en http://127.0.0.1:8000/?wsdl")
    print("Detén el proceso con Ctrl+C cuando termines de probarlo.")
    server.serve_forever()

