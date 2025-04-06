import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'dart:async';

class KafkaService {
  static final String wsUrl = "ws://127.0.0.1:8888";
  static WebSocketChannel? _channel;
  static StreamController<String> _messageController =
      StreamController.broadcast();

  static void connect() {
    if (_channel != null) return; // Evita criar múltiplas conexões

    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      print("✅ Conectado ao WebSocket em $wsUrl");

      _channel!.stream.listen(
        (message) {
          print("📩 Mensagem Recebida do WebSocket: $message");
          _messageController.add(message);
        },
        onError: (error) {
          print("❌ Erro no WebSocket: $error");
          _reconnect();
        },
        onDone: () {
          print("⚠️ WebSocket fechado. Tentando reconectar...");
          _reconnect();
        },
      );
    } catch (e) {
      print("❌ Erro ao conectar ao WebSocket: $e");
      _reconnect();
    }
  }

  static void _reconnect() {
    Future.delayed(Duration(seconds: 3), () {
      _channel = null;
      connect();
    });
  }

  // 🔥 Adiciona esta propriedade para resolver o erro
  static Stream<String> get messageStream => _messageController.stream;

  static void disconnect() {
    _channel?.sink.close(status.goingAway);
    _channel = null;
  }
}
