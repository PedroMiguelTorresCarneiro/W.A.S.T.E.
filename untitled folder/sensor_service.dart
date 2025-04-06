import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:waste_app/services/mqtt_manager.dart';

class SensorService {
  static const String _baseUrl = 'http://127.0.0.1:5004/v2';

  static Future<void> createTopic(String topic) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/topic'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic': topic}),
    );

    if (response.statusCode == 201) {
      print('Tópico "$topic" criado com sucesso.');
    } else if (response.statusCode == 409) {
      print('Tópico "$topic" já existe.');
    } else {
      throw Exception('Erro ao criar tópico: ${response.body}');
    }
  }

  static Future<void> registerSensor({
    required String sensorId,
    required String topic,
  }) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/sensors'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'sensor_id': sensorId, 'topic': topic}),
    );

    if (response.statusCode == 201) {
      print('Sensor "$sensorId" registado com sucesso.');

      final String fullMqttTopic = 'waste/$topic';

      // Criação correta da instância do MqttManager
      await MqttManager.subscribeToTopic(fullMqttTopic); // só isto!
    } else if (response.statusCode == 409) {
      print('Sensor "$sensorId" já está registado.');
    } else {
      throw Exception('Erro ao registar sensor: ${response.body}');
    }
  }

  static Future<void> removeSensor(String sensorId) async {
    final response = await http.delete(
      Uri.parse('$_baseUrl/sensors'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'sensor_ids': [sensorId],
      }),
    );

    if (response.statusCode == 200) {
      print('Sensor "$sensorId" removido com sucesso.');
      // Opcional: remover subscrição MQTT
      // await MqttManager.unsubscribeFromTopic('waste/<topic_from_lookup>');
    } else if (response.statusCode == 404) {
      print('Sensor "$sensorId" não encontrado.');
    } else {
      throw Exception('Erro ao remover sensor: ${response.body}');
    }
  }
}
