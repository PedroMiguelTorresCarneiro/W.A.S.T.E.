import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import '../config/config.dart';

class RouteData {
  final String routeId;
  final String truckId;
  final int day;
  final int month;
  final int year;
  final List<LatLng> coordinates;
  final double? durationMin;
  final double? distanceKm;

  RouteData({
    required this.routeId,
    required this.truckId,
    required this.day,
    required this.month,
    required this.year,
    required this.coordinates,
    this.durationMin,
    this.distanceKm,
  });

  factory RouteData.fromJson(Map<String, dynamic> json) {
    final List coords = json['coordinates'] ?? [];
    return RouteData(
      routeId: json['route_id'] ?? '',
      truckId: json['truck_id'] ?? '',
      day: json['day'] ?? 0,
      month: json['month'] ?? 0,
      year: json['year'] ?? 0,
      coordinates:
          coords.map<LatLng>((coord) => LatLng(coord[0], coord[1])).toList(),
      durationMin: (json['duration_min'] as num?)?.toDouble(),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
    );
  }
}

class RouteService {
  static Future<List<RouteData>> getRoutes({String? truckId}) async {
    final url = AppConfig.getRouteQueryUrl(truckId: truckId);
    final res = await http.get(Uri.parse(url));
    if (res.statusCode == 200) {
      final List data = json.decode(res.body);
      return data.map((e) => RouteData.fromJson(e)).toList();
    } else {
      throw Exception("Erro ao carregar rotas");
    }
  }

  static Future<void> deleteRoute(String routeId) async {
    final url = Uri.parse(AppConfig.deleteRouteUrl(routeId));
    final res = await http.delete(url);
    if (res.statusCode != 200) {
      throw Exception("Erro ao apagar rota");
    }
  }

  static Future<void> addRoute({
    required List<LatLng> coordinates,
    required String truckId,
    String mode = "car",
  }) async {
    final payload = {
      "coordinates": coordinates.map((e) => [e.latitude, e.longitude]).toList(),
      "mode": mode,
      "truck_id": truckId,
    };

    final res = await http.post(
      Uri.parse("${AppConfig.routesApiBase}/v2/routes"),
      headers: {"Content-Type": "application/json"},
      body: json.encode(payload),
    );
    if (res.statusCode != 200 && res.statusCode != 201) {
      throw Exception("Erro ao criar rota");
    }
  }
}
