import 'package:flutter/material.dart';
import 'package:waste_app/config/config.dart';
import 'package:waste_app/services/kafka_socket_service.dart';
import 'package:waste_app/services/user_service.dart';
import 'package:waste_app/widgets/map_widget.dart';
import 'package:latlong2/latlong.dart';
import 'package:waste_app/screens/sensor_management_screen.dart';
import 'package:waste_app/screens/route_management_screen.dart';
import 'package:waste_app/services/auth_service.dart';
import 'package:waste_app/services/composer_bin_service.dart';
import 'package:waste_app/widgets/binlist_widget.dart';
import 'package:waste_app/screens/persona_page.dart';

class AdminDashboard extends StatefulWidget {
  final String name;

  const AdminDashboard({super.key, required this.name});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard>
    with WidgetsBindingObserver {
  List<Bin> _bins = [];
  final Set<String> _subscribedTopics = {};
  bool _firstLoadDone = false;

  late KafkaWebSocketService kafkaWebSocketService;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    kafkaWebSocketService = KafkaWebSocketService(AppConfig.kafkaWebSocketUrl);
    kafkaWebSocketService.listen();

    kafkaWebSocketService.addTopicListener("nfc_logs", (data) async {
      try {
        final imei = data['imei'];
        if (imei == null) return;

        // Verifica se há user com este IMEI
        final user = await UserService.fetchUserByImei(imei);
        if (user['uid'] != null) {
          final uid = user['uid'];
          await UserService.incrementUsage(uid);
          print(
            "✅ usage_count incrementado para o user com UID: $uid (IMEI: $imei)",
          );
        } else {
          print("⚠️ Nenhum utilizador encontrado com o IMEI: $imei");
        }
      } catch (e) {
        print("❌ Erro ao processar mensagem do nfc_logs: $e");
      }
    });

    _loadBins();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_firstLoadDone) {
      print('🔁 Voltei ao AdminDashboard — a recarregar bins...');
      _loadBins(); // ← isto é o refresh automático
    } else {
      _firstLoadDone = true; // ← só para evitar duplo carregamento no arranque
    }
  }

  Future<void> _loadBins() async {
    try {
      final data = await BinService.getBins();
      print('✅ Bins carregados: ${_bins.length}');
      setState(() => _bins = data);

      for (final bin in data) {
        final topic = bin.topic;

        // 🔁 Evita subscrever múltiplas vezes ao mesmo tópico
        if (!_subscribedTopics.contains(topic)) {
          _subscribedTopics.add(topic);
          kafkaWebSocketService.addTopicListener(topic, (data) async {
            final serial = data['serial'];
            final fillLevel = data['fill_level'];

            final index = _bins.indexWhere((b) => b.sensorSerial == serial);
            if (index != -1) {
              setState(() {
                _bins[index] = Bin(
                  id: _bins[index].id,
                  sensorSerial: serial,
                  lat: _bins[index].lat,
                  lon: _bins[index].lon,
                  nfcToken: _bins[index].nfcToken,
                  topic: _bins[index].topic,
                  fillLevel: fillLevel.toString(),
                );
              });

              // 🔁 Atualiza o backend (MariaDB via API)
              try {
                await BinService.updateFillLevel(serial, fillLevel.toString());
              } catch (e) {
                print('❌ Erro ao atualizar fill_level na base de dados: $e');
              }

              // 🧼 Mostra snackbar
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    '🗑️ $serial está a $fillLevel% da capacidade!',
                  ),
                  duration: const Duration(seconds: 3),
                ),
              );
            }
          });
        }
      }
    } catch (e) {
      print("❌ Erro ao carregar bins: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Painel de Administração",
        ), // ou "Painel do Utilizador"
        actions: [
          // Botão de logout
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: "Logout",
            onPressed: () async {
              await AuthService().signOut(context);
            },
          ),

          // Botão de perfil
          IconButton(
            icon: const Icon(Icons.account_circle),
            tooltip: "Perfil",
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const PersonaPage()),
              );
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Center(
            child: Text(
              widget.name,
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 20),
          _adminActionsCard(context),
          const SizedBox(height: 20),
          _locationCard(),
          const SizedBox(height: 20),
          _binsCard(),
        ],
      ),
    );
  }

  Widget _locationCard() {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: SizedBox(
        height: 400,
        child: MapWidget(
          routeCoordinates: [],
          binLocations: _bins.map((b) => LatLng(b.lat, b.lon)).toList(),
        ),
      ),
    );
  }

  Widget _binsCard() {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  "Aveiro",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  tooltip: "Atualizar lista de caixotes",
                  onPressed: () async {
                    await _loadBins();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("🔄 Lista de caixotes atualizada!"),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 10),
            BinListWidget(bins: _bins),
          ],
        ),
      ),
    );
  }

  Widget _adminActionsCard(BuildContext context) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            ElevatedButton(
              onPressed: () async {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const RouteManagementScreen(),
                  ),
                );
                await _loadBins();
              },
              child: const Text("Rotas"),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const SensorManagementScreen(),
                  ),
                );
                await _loadBins();
              },
              child: const Text("Gestão da Rede"),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    kafkaWebSocketService
        .close(); // 🔒 Fecha a ligação WebSocket e limpa listeners
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      print('🔁 A voltar ao AdminDashboard — a recarregar bins...');
      _loadBins();
    }
  }
}
