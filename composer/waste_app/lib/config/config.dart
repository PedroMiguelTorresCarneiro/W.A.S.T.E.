class AppConfig {
  // URL base do serviço de rotas (ajustável consoante o domínio do backend)
  static const String routesApiBase = "http://localhost:5002";
  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  static const String fastApiBase = "http://localhost:8000";
  // URL base do serviço de sensores (ajustável consoante o domínio do backend)
  static const String sensorApiBase = "http://localhost:5004/v2";
  // URL base do serviço de rotas (ajustável consoante o domínio do backend)
  static const String routesApiV2 = "http://localhost:5002/v2/routes";
  // URL base do serviço de sensores (ajustável consoante o domínio do backend)
  static const String kafkaWebSocketUrl = "http://localhost:5006";

  // ID da rota (pode ser parametrizado no futuro)
  static const String defaultRouteId = "r1741451296";

  // URL completo do endpoint de rota
  static String get routeUrl => "$routesApiBase/v1/routes?id=$defaultRouteId";

  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  static String userExistsUrl(String uid) => "$fastApiBase/users/exists/$uid";
  static String get createUserUrl => "$fastApiBase/users";

  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  static String get binsUrl => "$fastApiBase/bins";
  static String fillLevelUrl(String serial) => "$fastApiBase/bins/fill/$serial";

  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  static String get topicUrl => "$sensorApiBase/topic";
  static String get sensorUrl => "$sensorApiBase/sensors";

  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  static String getRouteQueryUrl({String? truckId}) {
    return truckId != null ? "$routesApiV2?truck_id=$truckId" : routesApiV2;
  }

  // URL base do serviço FastAPI (ajustável consoante o domínio do backend)
  static String deleteRouteUrl(String routeId) => "$routesApiV2?id=$routeId";
}
