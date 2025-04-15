import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/config.dart';

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
    this.fillLevel = "0",
  });

  factory Bin.fromJson(Map<String, dynamic> json) => Bin(
    id: json['id'],
    sensorSerial: json['sensor_serial'],
    lat: json['lat'],
    lon: json['lon'],
    nfcToken: json['nfc_token'],
    topic: json['topic'],
    fillLevel: json['fill_level'] ?? "0",
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
  static final String baseUrl = AppConfig.binsUrl;
  static final String externalTopicUrl = AppConfig.topicUrl;
  static final String externalSensorUrl = AppConfig.sensorUrl;

  static Future<List<Bin>> getBins() async {
    final response = await http.get(Uri.parse(baseUrl));
    if (response.statusCode == 200) {
      List data = json.decode(response.body);
      return data.map((e) => Bin.fromJson(e)).toList();
    } else {
      throw Exception('Erro ao obter sensores');
    }
  }

  static Future<Bin> addBin(Bin bin) async {
    // 1. Verifica se o sensor já existe
    final sensorExistsResponse = await http.get(
      Uri.parse('$externalSensorUrl/${bin.sensorSerial}'),
      headers: {'Content-Type': 'application/json'},
    );

    if (sensorExistsResponse.statusCode == 200) {
      // Se o sensor já existe, lança erro
      throw Exception('Sensor ${bin.sensorSerial} já existe!');
    }

    // 2. Tenta criar o sensor no serviço de sensores
    final sensorResponse = await http.post(
      Uri.parse(externalSensorUrl),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'sensor_id': bin.sensorSerial, 'topic': bin.topic}),
    );

    print(
      'Sensor Response: ${sensorResponse.statusCode}, Body: ${sensorResponse.body}',
    );

    if (sensorResponse.statusCode != 200 && sensorResponse.statusCode != 201) {
      throw Exception('Erro ao criar sensor no serviço de monitorização');
    }

    // 3. Tenta criar o tópico, e se já existir (409), considera como sucesso
    final topicResponse = await http.post(
      Uri.parse(externalTopicUrl),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'topic': bin.topic}),
    );

    print(
      'Topic Response: ${topicResponse.statusCode}, Body: ${topicResponse.body}',
    );

    if (topicResponse.statusCode != 200 &&
        topicResponse.statusCode != 201 &&
        topicResponse.statusCode != 409) {
      throw Exception('Erro ao criar ou verificar tópico');
    } else if (topicResponse.statusCode == 409) {
      // Se o tópico já existir, não faz nada
      print("✅ O tópico ${bin.topic} já existe!");
    }

    // 4. Cria o Bin no serviço principal
    final binResponse = await http.post(
      Uri.parse(baseUrl),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(bin.toJson()),
    );

    print('Bin Response: ${binResponse.statusCode}, Body: ${binResponse.body}');

    if (binResponse.statusCode != 200 && binResponse.statusCode != 201) {
      throw Exception('Erro ao adicionar Bin à base de dados');
    }

    final jsonResponse = json.decode(binResponse.body);
    return Bin.fromJson(jsonResponse);
  }

  static Future<void> updateBin(int id, Bin bin) async {
    final response = await http.put(
      Uri.parse('$baseUrl/$id'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(bin.toJson()),
    );
    if (response.statusCode != 200) {
      throw Exception('Erro ao atualizar sensor');
    }

    await http.post(
      Uri.parse(externalSensorUrl),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'sensor_id': bin.sensorSerial, 'topic': bin.topic}),
    );
  }

  static Future<void> deleteBin(int id, String sensorSerial) async {
    final response = await http.delete(Uri.parse('$baseUrl/$id'));
    if (response.statusCode != 200) {
      throw Exception('Erro ao remover sensor');
    }

    await http.delete(
      Uri.parse(externalSensorUrl),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'sensor_ids': [sensorSerial],
      }),
    );
  }

  static Future<void> updateFillLevel(String serial, String level) async {
    final response = await http.put(
      Uri.parse(AppConfig.fillLevelUrl(serial)),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'fill_level': level}),
    );
    if (response.statusCode != 200) {
      throw Exception("Failed to update fill level");
    }
  }
}
