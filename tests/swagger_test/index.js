const express = require("express");
const swaggerUi = require("swagger-ui-express");
const fs = require("fs");

const app = express();
const PORT = 3000;

// Carregar o ficheiro swagger.json
const swaggerDocument = JSON.parse(fs.readFileSync("./swagger.json", "utf8"));

// Middleware para Swagger UI
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Iniciar o servidor do Swagger UI
app.listen(PORT, () => {
  console.log(`Swagger UI disponível em http://localhost:${PORT}/api-docs`);
});
