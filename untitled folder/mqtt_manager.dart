import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:waste_app/services/composer_bin_service.dart';

class MqttManager {
  static final MqttServerClient _client =
      MqttServerClient.withPort('localhost', 'flutter_web_client', 9001)
        ..useWebSocket = true
        ..logging(on: true)
        ..keepAlivePeriod = 20
        ..onDisconnected = _onDisconnected
        ..onConnected = _onConnected;

  static Function()? onBinUpdate; // 🔔 Callback para atualizar UI

  static Future<void> connect() async {
    if (_client.connectionStatus?.state == MqttConnectionState.connected) {
      return; // Já conectado
    }

    final connMessage = MqttConnectMessage()
        .withClientIdentifier('flutter_web_client')
        .startClean()
        .withWillQos(MqttQos.atMostOnce);

    _client.connectionMessage = connMessage;

    try {
      await _client.connect();
    } catch (e) {
      print('🚫 Falha na conexão MQTT: $e');
      _client.disconnect();
    }
  }

  static Future<void> subscribeToTopic(String topic) async {
    await connect();
    final mqttTopic = 'waste/$topic';

    _client.subscribe(mqttTopic, MqttQos.atMostOnce);

    _client.updates?.listen((
      List<MqttReceivedMessage<MqttMessage>> messages,
    ) async {
      final recMessage = messages.first.payload as MqttPublishMessage;
      final payload = MqttPublishPayload.bytesToStringAsString(
        recMessage.payload.message,
      );

      print('📥 [MQTT] Mensagem recebida em $mqttTopic: $payload');

      // Decodificação segura do JSON
      try {
        final decoded = jsonDecode(payload);
        final serial = decoded['serial'];
        final level = decoded['fill_level'].toString();

        await BinService.updateFillLevel(serial, level);
        print('✅ Fill level atualizado via MQTT!');

        if (onBinUpdate != null) {
          onBinUpdate!(); // Notifica UI
        }
      } catch (e) {
        print('⚠️ Erro ao decodificar JSON MQTT: $e');
      }
    });
  }

  static void _onDisconnected() {
    print('🔌 MQTT desconectado');
  }

  static void _onConnected() {
    print('✅ MQTT conectado');
  }
}
