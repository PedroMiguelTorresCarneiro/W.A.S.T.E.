import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import '../composer.dart';
import '../widgets/map_widget.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<LatLng> _routeCoordinates = [];
  List<String> _kafkaMessages = []; // Lista para armazenar mensagens Kafka

  @override
  void initState() {
    super.initState();

    // Inicia conexão Kafka
    Composer.startKafka();

    // Escuta mensagens Kafka e atualiza a UI
    Composer.getKafkaMessages().listen((message) {
      print("📝 Mensagem recebida na UI: $message");
      setState(() {
        _kafkaMessages.insert(0, message); // Adiciona mensagem no topo da lista
      });
    });
  }

  Future<void> _fetchRoute() async {
    List<LatLng> route = await Composer.getRouteData();

    if (route.isNotEmpty) {
      setState(() {
        _routeCoordinates = route;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Rota carregada com sucesso!")),
      );
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Erro ao carregar a rota.")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('W.A.S.T.E.'), centerTitle: true),
      body: Column(
        children: [
          // Card com o mapa
          Card(
            margin: const EdgeInsets.all(16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: SizedBox(
              height: MediaQuery.of(context).size.height * 0.5,
              width: double.infinity,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: MapWidget(
                  routeCoordinates: [], // ou uma rota real
                  binLocations: [
                    LatLng(40.623, -8.629),
                    LatLng(40.624, -8.627),
                  ],
                ),
              ),
            ),
          ),

          // Card para mensagens Kafka
          Card(
            margin: const EdgeInsets.all(16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Container(
              padding: const EdgeInsets.all(16),
              width: double.infinity,
              child: Column(
                children: [
                  const Text(
                    "Mensagens Kafka",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  _kafkaMessages.isEmpty
                      ? const Text("Aguardando mensagens...")
                      : Column(
                        children:
                            _kafkaMessages
                                .map((msg) => Text("📩 $msg"))
                                .toList(),
                      ),
                ],
              ),
            ),
          ),

          // 🔥 Botão para carregar a rota (voltou!)
          Padding(
            padding: const EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _fetchRoute,
              child: const Text("Mostrar Rota"),
            ),
          ),
        ],
      ),
    );
  }
}
