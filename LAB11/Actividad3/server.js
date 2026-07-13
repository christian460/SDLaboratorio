const fs = require("fs");
const https = require("https");
const express = require("express");

const app = express();

app.get("/", (req, res) => {
    res.send(`
        <h1>LogiMarket Perú S.A.C.</h1>
        <h2>Servicio de Autenticación</h2>
        <p>Conexión HTTPS establecida correctamente.</p>
    `);
});

const options = {
    key: fs.readFileSync("./certs/private.key"),
    cert: fs.readFileSync("./certs/certificate.crt")
};

https.createServer(options, app).listen(3000, () => {
    console.log("=====================================");
    console.log("Servidor HTTPS iniciado correctamente");
    console.log("https://localhost:3000");
    console.log("=====================================");
});