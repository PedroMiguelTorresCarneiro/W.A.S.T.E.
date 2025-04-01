# COMPOSER API



````
lib/
│── main.dart          → Define a navegação entre ecrãs
│── composer.dart      → Coordena a lógica e gere os dados
│── services/
│    ├── api_service.dart  → Liga-se à API e busca dados
│    ├── db_service.dart   → Se necessário, lida com base de dados local
│    ├── kafka_service.dart  → (Opcional) Recebe dados do Kafka
│── models/
│    ├── route_model.dart  → Define estrutura de dados da rota
│── widgets/
│    ├── map_widget.dart  → Separa o mapa como widget reutilizável
│── screens/
│    ├── home_screen.dart       → Ecrã principal
│    ├── admin_screen.dart      → Ecrã do administrador
│    ├── user_screen.dart       → Ecrã do utilizador normal
│    ├── settings_screen.dart   → Ecrã de definições
│    ├── login_screen.dart      → Ecrã de login (se necessário)
````

Possivel estrutura:
- `main.dart` → Só trata da UI.
    - Recebe os dados do composer.dart e mostra-os.
    - Exemplo: Um botão chama uma função do composer.dart.

- `composer.dart` → Camada intermediária que:
    - Recolhe dados da API, Kafka, BD e junta tudo.
    - Decide como os dados devem ser manipulados.
    - Informa o main.dart quando os dados mudam.

- `services/api_service.dart` → Liga-se à API e extrai os dados.

- `services/kafka_service.dart` → Kafka, este ficheiro processaria as mensagens dos tópicos.

- `services/db_service.dart` → Se precisar de uma base de dados local, este ficheiro geriria isso.

- `models/route_model.dart` → Define a estrutura do que é uma rota (evita manipular JSON "cru" diretamente).

- `widgets/map_widget.dart` → Se quiser dividir a UI em componentes menores, podes criar widgets reaproveitáveis, como um mapa.



---

<br>
<br>
<br>
<br>

---
---
# 🗑️ W.A.S.T.E. – API de Gestão de Contentores

Este projeto fornece uma API REST simples para gerir contentores de lixo com os campos:

`id | sensor_serial | lat | lon | nfc_token | topic`

---

## 📦 Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Python 3.10+](https://www.python.org/)
- `pip install -r requirements.txt` com:
  - `fastapi`
  - `uvicorn`
  - `pymysql`

---

## 🚀 Como correr localmente

### 1. 🐳 Criar o MariaDB com Docker

```bash
docker run --name waste-mariadb -e MYSQL_ROOT_PASSWORD=wastepass \
  -e MYSQL_DATABASE=waste_db -e MYSQL_USER=waste_user -e MYSQL_PASSWORD=wastepass \
  -p 3307:3306 -d mariadb:11
```

> ⚠️ Se a porta 3306 estiver ocupada, usamos a **3307** no host.


#### 1.1 🐳 Correr o MariaDB com Docker
```bash
docker start waste-mariadb
```

---

### 2. 🗂️ Criar a tabela `bins`

Podes entrar no MariaDB com:

```bash
mysql -h 127.0.0.1 -P 3307 -u root -p
# Password: wastepass
```

E executar:

```sql
USE waste_db;

CREATE TABLE bins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sensor_serial VARCHAR(100) NOT NULL,
  lat DOUBLE NOT NULL,
  lon DOUBLE NOT NULL,
  nfc_token VARCHAR(100) NOT NULL,
  topic VARCHAR(100) NOT NULL
);
```

---

### 3. 🧠 Correr a API FastAPI

```bash
uvicorn main:app --reload
```

---

## 🔍 Endpoints disponíveis

Acede a: [http://localhost:8000/docs](http://localhost:8000/docs)

| Método | Rota             | Descrição                      |
|--------|------------------|-------------------------------|
| GET    | `/bins`          | Lista todos os contentores    |
| POST   | `/bins`          | Adiciona um novo contentor     |
| PUT    | `/bins/{id}`     | Atualiza um contentor existente |
| DELETE | `/bins/{id}`     | Remove um contentor            |

---

## 🧼 Limpar ambiente

```bash
docker stop waste-mariadb
docker rm waste-mariadb
```

---

## 📌 Notas

- A API está pronta a ser integrada com Flutter ou outra aplicação.
- O MariaDB corre isolado via Docker na porta `3307`.

---

## 👨‍💻 Autor

Pedro Carneiro — Universidade de Aveiro, 2025


<br>
<br>
<br>
<br>

---
---


# RUN THE TEST

## 1. Ligar o Producer
````
/usr/local/opt/kafka/bin/kafka-console-producer --topic bin-monitoring --bootstrap-server localhost:9092
````
- Stream para simular msg dos sensores e para servir de teste!
---

## 2. Ligar O Kafka_consumer
```bash
# Na pasta s_BinMonitoring
python kafka_consumer.py

## para confirmar se ligou ao websocket
wscat -c ws://127.0.0.1:8888
```
- Basicamente converte as msg de kafka para websockets, porque o FLutter não recebe nativamente msg kafka!
---

## 3. Ligar o serviço de rotas
```bash
# dir: /s_routes
python routesAPI.py
```
- Ativar o endpoint necessário
---

## 4. Correr o Flutter
```bash
## no dir /composer/waste_app/
flutter run

### Escolher a opção 2 (Chrome)
```
- O teste mostra um Mapa e onde podemos pedir uma rota e ela aparece no mapa!
- tem um card que recebe em tempo real as msg envias via kafka e posteriormente enviadas por websockets!
---
