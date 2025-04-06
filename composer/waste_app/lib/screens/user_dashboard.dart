import 'package:flutter/material.dart';
import 'package:waste_app/widgets/map_widget.dart';
import 'package:latlong2/latlong.dart';
import 'package:waste_app/services/auth_service.dart';
import 'package:waste_app/services/composer_bin_service.dart';
import 'package:waste_app/services/kafka_socket_service.dart';
import 'package:waste_app/widgets/binlist_widget.dart';

class UserDashboard extends StatefulWidget {
  final String name;

  const UserDashboard({super.key, required this.name});

  @override
  State<UserDashboard> createState() => _UserDashboardState();
}

class _UserDashboardState extends State<UserDashboard> {
  List<Bin> _bins = [];
  final Set<String> _subscribedTopics = {};

  @override
  void initState() {
    super.initState();
    KafkaSocketService.connect();
    _loadBins();
  }

  Future<void> _loadBins() async {
    try {
      final data = await BinService.getBins();
      setState(() => _bins = data);

      for (final bin in data) {
        final topic = bin.topic;

        if (!_subscribedTopics.contains(topic)) {
          _subscribedTopics.add(topic);
          KafkaSocketService.listenToTopic(topic, (data) async {
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

              try {
                await BinService.updateFillLevel(serial, fillLevel.toString());
              } catch (e) {
                print('❌ Erro ao atualizar fill_level na base de dados: $e');
              }

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
        title: const Text("Dashboard"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => AuthService().signOut(context),
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
        height: 300,
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
            const Text("Aveiro", style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            BinListWidget(bins: _bins),
          ],
        ),
      ),
    );
  }
}
