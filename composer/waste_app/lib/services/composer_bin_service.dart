import 'dart:convert';
import 'package:http/http.dart' as http;

class Bin {
  final int? id;
  final String sensorSerial;
  final double lat;
  final double lon;
  final String nfcToken;
  final String topic;
  final String? fillLevel;

  Bin({
    this.id,
    required this.sensorSerial,
    required this.lat,
    required this.lon,
    required this.nfcToken,
    required this.topic,
    this.fillLevel,
  });

  factory Bin.fromJson(Map<String, dynamic> json) => Bin(
    id: json['id'],
    sensorSerial: json['sensor_serial'],
    lat: json['lat'],
    lon: json['lon'],
    nfcToken: json['nfc_token'],
    topic: json['topic'],
    fillLevel: json['fill_level'],
  );

  Map<String, dynamic> toJson() => {
    'sensor_serial': sensorSerial,
    'lat': lat,
    'lon': lon,
    'nfc_token': nfcToken,
    'topic': topic,
    'fill_level': fillLevel,
  };
}

class BinService {
  static const String baseUrl = 'http://127.0.0.1:8000';
  static const String externalApi = 'http://127.0.0.1:5004/v2';

  static Future<List<Bin>> getBins() async {
    final response = await http.get(Uri.parse('$baseUrl/bins'));
    if (response.statusCode == 200) {
      List data = json.decode(response.body);
      return data.map((e) => Bin.fromJson(e)).toList();
    } else {
      throw Exception('Erro ao obter sensores');
    }
  }

  static Future<void> addBin(Bin bin) async {
    final response = await http.post(
      Uri.parse('$baseUrl/bins'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(bin.toJson()),
    );
    if (response.statusCode != 200) {
      throw Exception('Erro ao adicionar sensor');
    }

    // Sync with external service
    await http.post(
      Uri.parse('$externalApi/topic'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'topic': bin.topic}),
    );

    await http.post(
      Uri.parse('$externalApi/sensors'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'sensor_id': bin.sensorSerial, 'topic': bin.topic}),
    );
  }

  static Future<void> updateBin(int id, Bin bin) async {
    final response = await http.put(
      Uri.parse('$baseUrl/bins/$id'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(bin.toJson()),
    );
    if (response.statusCode != 200) {
      throw Exception('Erro ao atualizar sensor');
    }

    await http.post(
      Uri.parse('$externalApi/sensors'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'sensor_id': bin.sensorSerial, 'topic': bin.topic}),
    );
  }

  static Future<void> deleteBin(int id, String sensorSerial) async {
    final response = await http.delete(Uri.parse('$baseUrl/bins/$id'));
    if (response.statusCode != 200) {
      throw Exception('Erro ao remover sensor');
    }

    await http.delete(
      Uri.parse('$externalApi/sensors'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'sensor_ids': [sensorSerial],
      }),
    );
  }

  static Future<void> updateFillLevel(String serial, String level) async {
    final response = await http.put(
      Uri.parse('$baseUrl/bins/fill/$serial'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'fill_level': level}),
    );
    if (response.statusCode != 200) {
      throw Exception("Failed to update fill level");
    }
  }
}
