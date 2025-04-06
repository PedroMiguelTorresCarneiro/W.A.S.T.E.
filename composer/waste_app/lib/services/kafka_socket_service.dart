import 'package:socket_io_client/socket_io_client.dart' as IO;

class KafkaSocketService {
  static final IO.Socket socket = IO.io(
    'http://localhost:5006',
    IO.OptionBuilder()
        .setTransports(['websocket'])
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
    socket.disconnect();
    _listeningTopics.clear();
  }
}
