// import 'package:socket_io_client/socket_io_client.dart' as IO;
// import 'package:web_socket_channel/web_socket_channel.dart';
// import '../config/config.dart';

// class KafkaSocketService {
//   // static final IO.Socket socket = IO.io(
//   //   AppConfig.kafkaWebSocketUrl, // ✅ Usar URL centralizada
//   //   IO.OptionBuilder()
//   //       .setTransports(['polling', 'websocket'])
//   //       .setPath("/ws") // ✅ Aqui sim
//   //       .disableAutoConnect()
//   //       .build(),
//   // );
//   // static final IO.Socket socket = IO.io(
//   //   AppConfig.kafkaWebSocketUrl,
//   //   IO.OptionBuilder()
//   //       .setTransports(['websocket']) // Forçar só WebSocket
//   //       .setPath("/ws") // Ou o path que usares no Kong
//   //       .disableAutoConnect()
//   //       .build(),
//   // );
//   final channel = WebSocketChannel.connect(
//     Uri.parse(
//       AppConfig.kafkaWebSocketUrl,
//     ), // ex: "ws://grupo2-egs-deti.ua.pt/ws"
//   );

//   void listen() {
//     channel.stream.listen(
//       (message) {
//         print('Received: $message');
//       },
//       onError: (error) {
//         print('Error: $error');
//       },
//     );
//   }

//   // Para enviar mensagens (se precisares)
//   void sendMessage(String msg) {
//     channel.sink.add(msg);
//   }

//   static final Set<String> _listeningTopics = {};

//   /// Inicia a conexão WebSocket
//   static void connect() {
//     socket.connect();
//     socket.onConnect((_) {
//       print('✅ Conectado ao WebSocket');
//     });
//     socket.onDisconnect((_) => print('❌ Desconectado do WebSocket'));
//     socket.onConnectError((e) => print('⚠️ Erro na conexão: $e'));
//     socket.onError((e) => print('🔥 Erro: $e'));
//   }

//   /// Escuta dinamicamente um tópico emitido pelo servidor
//   static void listenToTopic(
//     String topic,
//     Function(Map<String, dynamic>) callback,
//   ) {
//     if (_listeningTopics.contains(topic)) return;

//     socket.on(topic, (data) {
//       print('📥 [$topic] $data');
//       callback(Map<String, dynamic>.from(data));
//     });

//     _listeningTopics.add(topic);
//   }

//   /// Para de escutar um tópico
//   static void removeTopicListener(String topic) {
//     socket.off(topic);
//     _listeningTopics.remove(topic);
//     print('🔇 Parou de escutar o tópico: $topic');
//   }

//   /// Fecha a conexão WebSocket
//   static void disconnect() {
//     if (socket.connected) socket.disconnect();
//     for (final topic in _listeningTopics) {
//       socket.off(topic);
//     }
//     _listeningTopics.clear();
//   }
// }

import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

typedef TopicCallback = void Function(Map<String, dynamic> data);

class KafkaWebSocketService {
  final WebSocketChannel _channel;
  final Map<String, List<TopicCallback>> _topicListeners = {};

  KafkaWebSocketService(String url)
    : _channel = WebSocketChannel.connect(Uri.parse(url));

  void listen() {
    _channel.stream.listen(
      (message) {
        print('Received raw message: $message');
        try {
          final Map<String, dynamic> jsonMsg = json.decode(message);
          final topic = jsonMsg['topic'] as String?;
          final data = jsonMsg['data'];

          if (topic != null &&
              data != null &&
              _topicListeners.containsKey(topic)) {
            for (final callback in _topicListeners[topic]!) {
              callback(Map<String, dynamic>.from(data));
            }
          }
        } catch (e) {
          print('Error decoding or handling message: $e');
        }
      },
      onError: (error) {
        print('WebSocket error: $error');
      },
      onDone: () {
        print('WebSocket connection closed');
      },
    );
  }

  void sendMessage(String message) {
    _channel.sink.add(message);
  }

  /// Adiciona um callback para um tópico específico
  void addTopicListener(String topic, TopicCallback callback) {
    _topicListeners.putIfAbsent(topic, () => []).add(callback);
  }

  /// Remove um callback para um tópico
  void removeTopicListener(String topic, TopicCallback callback) {
    final listeners = _topicListeners[topic];
    if (listeners == null) return;
    listeners.remove(callback);
    if (listeners.isEmpty) {
      _topicListeners.remove(topic);
    }
  }

  void close() {
    _channel.sink.close();
  }
}
