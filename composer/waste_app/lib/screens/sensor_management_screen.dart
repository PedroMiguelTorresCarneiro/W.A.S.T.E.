import 'package:flutter/material.dart';
import 'package:waste_app/services/composer_bin_service.dart';

class SensorManagementScreen extends StatefulWidget {
  const SensorManagementScreen({super.key});

  @override
  State<SensorManagementScreen> createState() => _SensorManagementScreenState();
}

class _SensorManagementScreenState extends State<SensorManagementScreen> {
  List<Bin> bins = [];

  Future<void> _fetchBins() async {
    try {
      final data = await BinService.getBins();
      setState(() {
        bins = data; // Atualiza a lista com a resposta da API
      });
    } catch (e) {
      print("Erro ao obter bins: $e");
      setState(() => bins = []); // Limpa a lista em caso de erro
    }
  }

  Future<void> _showAddBinDialog() async {
    final controller = _BinFormController();
    await showDialog(
      context: context,
      builder:
          (_) => AlertDialog(
            title: const Text("Adicionar Sensor"),
            content: _BinForm(controller: controller),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("Cancelar"),
              ),
              TextButton(
                onPressed: () async {
                  try {
                    // Adiciona o bin
                    await BinService.addBin(controller.toBin());

                    // Fecha o diálogo
                    Navigator.pop(context);
                    await _fetchBins(); // ← ADICIONA ISTO AQUI
                  } catch (e) {
                    // Exibe erro corretamente na SnackBar
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Erro ao adicionar sensor: $e')),
                    );
                  }
                },
                child: const Text("Adicionar"),
              ),
            ],
          ),
    );
  }

  Future<void> _showEditDialog(Bin bin) async {
    final controller = _BinFormController.fromBin(bin);
    await showDialog(
      context: context,
      builder:
          (_) => AlertDialog(
            title: const Text("Editar Sensor"),
            content: _BinForm(controller: controller),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("Cancelar"),
              ),
              TextButton(
                onPressed: () async {
                  await BinService.updateBin(bin.id!, controller.toBin());
                  Navigator.pop(context);
                  _fetchBins();
                },
                child: const Text("Atualizar"),
              ),
            ],
          ),
    );
  }

  Future<void> _confirmDelete(Bin bin) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder:
          (_) => AlertDialog(
            title: const Text("Confirmar Remoção"),
            content: const Text(
              "Tens a certeza que queres remover este sensor?",
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text("Cancelar"),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text("Remover"),
              ),
            ],
          ),
    );
    if (confirm == true) {
      await BinService.deleteBin(bin.id!, bin.sensorSerial);
      _fetchBins();
    }
  }

  @override
  void initState() {
    super.initState();
    _fetchBins();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Gestão de Sensores")),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ElevatedButton(
              onPressed: _showAddBinDialog,
              child: const Text("Adicionar Sensor"),
            ),
          ),
          const SizedBox(height: 10),
          Expanded(
            child: ListView.builder(
              itemCount: bins.length,
              itemBuilder: (context, index) {
                final bin = bins[index];
                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  child: ListTile(
                    title: Text("Sensor: ${bin.sensorSerial}"),
                    subtitle: Text(
                      "Lat: ${bin.lat}, Lon: ${bin.lon}\nToken: ${bin.nfcToken}\n",
                    ),
                    trailing: Wrap(
                      spacing: 8,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.edit),
                          onPressed: () => _showEditDialog(bin),
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete),
                          onPressed: () => _confirmDelete(bin),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _BinFormController {
  final TextEditingController serial = TextEditingController();
  final TextEditingController lat = TextEditingController();
  final TextEditingController lon = TextEditingController();
  final TextEditingController token = TextEditingController();
  final TextEditingController topic = TextEditingController();

  _BinFormController();

  factory _BinFormController.fromBin(Bin bin) {
    final c = _BinFormController();
    c.serial.text = bin.sensorSerial;
    c.lat.text = bin.lat.toString();
    c.lon.text = bin.lon.toString();
    c.token.text = bin.nfcToken;
    c.topic.text = bin.topic;
    return c;
  }

  Bin toBin() {
    // Verificar se os campos não são vazios
    if (serial.text.isEmpty ||
        lat.text.isEmpty ||
        lon.text.isEmpty ||
        token.text.isEmpty ||
        topic.text.isEmpty) {
      throw Exception("Todos os campos são obrigatórios.");
    }

    // Garantir que lat e lon sejam números válidos, se não, usar valores padrão
    double latValue = double.tryParse(lat.text) ?? 0.0;
    double lonValue = double.tryParse(lon.text) ?? 0.0;

    String fillLevelValue = "0";

    print(
      "Campos do formulário inicializados: ${serial.text}, ${lat.text}, ${lon.text}, ${token.text}, ${topic.text}, fill_level: $fillLevelValue",
    );

    return Bin(
      sensorSerial: serial.text,
      lat: latValue,
      lon: lonValue,
      nfcToken: token.text,
      topic: topic.text,
      fillLevel: fillLevelValue,
    );
  }
}

class _BinForm extends StatelessWidget {
  final _BinFormController controller;

  const _BinForm({required this.controller});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: controller.serial,
            decoration: const InputDecoration(labelText: "Número de Série"),
          ),
          TextField(
            controller: controller.lat,
            decoration: const InputDecoration(labelText: "Latitude"),
            keyboardType: TextInputType.number,
          ),
          TextField(
            controller: controller.lon,
            decoration: const InputDecoration(labelText: "Longitude"),
            keyboardType: TextInputType.number,
          ),
          TextField(
            controller: controller.token,
            decoration: const InputDecoration(labelText: "NFC Token"),
          ),
          TextField(
            controller: controller.topic,
            decoration: const InputDecoration(labelText: "Categoria"),
          ),
        ],
      ),
    );
  }
}
