import 'dart:convert';
//import 'dart:io' show Platform;
//import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import '../config/config.dart';

class ApiService {
  /// Faz um GET na API e retorna a lista de coordenadas
  static Future<List<LatLng>> fetchRoute() async {
    final String url = AppConfig.routeUrl;

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {"Accept": "application/json"},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print("API Response: $data");

        if (data == null || !data.containsKey("coordinates")) {
          throw Exception(
            "Formato de resposta inválido. 'coordinates' não encontrado.",
          );
        }

        return data["coordinates"]
            .map<LatLng>((coord) => LatLng(coord[0], coord[1]))
            .toList();
      } else {
        throw Exception(
          "Falha ao buscar rota. Código HTTP: ${response.statusCode}",
        );
      }
    } catch (error) {
      print("Erro ao buscar rota: $error");
      return [];
    }
  }
}
