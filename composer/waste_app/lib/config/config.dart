class AppConfig {
  // URL base do serviço de rotas (ajustável consoante o domínio do backend)
  //tatic const String routesApiBase = "http://localhost:5002";
  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  //static const String fastApiBase = "http://localhost:5008";
  // URL base do serviço de sensores (ajustável consoante o domínio do backend)
  //static const String sensorApiBase = "http://localhost:5004/v2";
  // URL base do serviço de rotas (ajustável consoante o domínio do backend)
  //static const String routesApiV2 = "http://localhost:5002/v2/routes";
  // URL base do serviço de sensores (ajustável consoante o domínio do backend)
  //static const String kafkaWebSocketUrl = "http://localhost:5006";

  // // Kong faz o routing para os serviços certos com base nos paths
  // static const String fastApiBase =
  //     "http://localhost:8000/api"; // FastAPI: users, bins
  // static const String routesApiBase =
  //     "http://localhost:8000/routes"; // Serviço de rotas
  // static const String sensorApiBase =
  //     "http://localhost:8000/monitoring"; // Serviço de sensores
  // static const String kafkaWebSocketUrl =
  //     "http://localhost:8000"; // ✅ Sem /socket.io

  // Base URL dos serviços via Kong (domínio público)
  static const String fastApiBase =
      "https://grupo2-egs-deti.ua.pt/v2/api"; // FastAPI: users, bins
  static const String routesApiBase =
      "https://grupo2-egs-deti.ua.pt/v2/routes"; // Serviço de rotas
  static const String sensorApiBase =
      "https://grupo2-egs-deti.ua.pt/v2/binmonitoring"; // Serviço de sensores
  static const String kafkaWebSocketUrl =
      "ws://grupo2-egs-deti.ua.pt/ws"; // WebSocket via Kong

  // Rota por omissão
  static const String defaultRouteId = "r1741451296";

  // Rotas
  static String get routeUrl => "$routesApiBase?id=$defaultRouteId";
  static String getRouteQueryUrl({String? truckId}) {
    final base = routesApiBase;
    return truckId != null ? "$base?truck_id=$truckId" : base;
  }

  static String deleteRouteUrl(String routeId) => "$routesApiBase?id=$routeId";

  // Users
  static String userExistsUrl(String uid) => "$fastApiBase/v2/api/users/$uid";
  static String get createUserUrl => "$fastApiBase/v2/api/users";
  static String get binsUrl => "$fastApiBase/v2/api/bins";
  static String fillLevelUrl(String serial) =>
      "$fastApiBase/v2/api/bins/fill/$serial";

  // Sensores
  static String get topicUrl => "$sensorApiBase/topic";
  static String get sensorUrl => "$sensorApiBase/sensors";
}
