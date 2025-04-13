import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../config/config.dart';

class KafkaSocketService {
  static final IO.Socket socket = IO.io(
    AppConfig.kafkaWebSocketUrl, // ✅ Usar URL centralizada
    IO.OptionBuilder()
        .setTransports(['polling', 'websocket'])
        .setPath("/socket.io") // ✅ Aqui sim
        .disableAutoConnect()
        .build(),
  );

  static final Set<String> _listeningTopics = {};

  /// Inicia a conexão WebSocket
  static void connect() {
    socket.connect();
    socket.onConnect((_) {
      print('✅ Conectado ao WebSocket');
    });
    socket.onDisconnect((_) => print('❌ Desconectado do WebSocket'));
    socket.onConnectError((e) => print('⚠️ Erro na conexão: $e'));
    socket.onError((e) => print('🔥 Erro: $e'));
  }

  /// Escuta dinamicamente um tópico emitido pelo servidor
  static void listenToTopic(
    String topic,
    Function(Map<String, dynamic>) callback,
  ) {
    if (_listeningTopics.contains(topic)) return;

    socket.on(topic, (data) {
      print('📥 [$topic] $data');
      callback(Map<String, dynamic>.from(data));
    });

    _listeningTopics.add(topic);
  }

  /// Para de escutar um tópico
  static void removeTopicListener(String topic) {
    socket.off(topic);
    _listeningTopics.remove(topic);
    print('🔇 Parou de escutar o tópico: $topic');
  }

  /// Fecha a conexão WebSocket
  static void disconnect() {
    if (socket.connected) socket.disconnect();
    for (final topic in _listeningTopics) {
      socket.off(topic);
    }
    _listeningTopics.clear();
  }
}
