import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';
import '../services/route_service.dart';
import '../services/composer_bin_service.dart';
import '../widgets/map_widget.dart';

class RouteManagementScreen extends StatefulWidget {
  const RouteManagementScreen({super.key});

  @override
  State<RouteManagementScreen> createState() => _RouteManagementScreenState();
}

class _RouteManagementScreenState extends State<RouteManagementScreen> {
  List<RouteData> _routes = [];
  List<LatLng> _currentRoute = [];
  String? _selectedTruckId;
  int _selectedThreshold = 50;
  final Set<String> _truckIds = {};
  final TextEditingController _truckInputController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchRoutes();
  }

  @override
  void dispose() {
    _truckInputController.dispose();
    super.dispose();
  }

  Future<void> _fetchRoutes() async {
    try {
      final routes = await RouteService.getRoutes();

      // Ordena por ano, depois mês, depois dia (decrescente)
      routes.sort((a, b) {
        final dateA = DateTime(a.year, a.month, a.day);
        final dateB = DateTime(b.year, b.month, b.day);
        return dateB.compareTo(dateA); // decrescente
      });

      setState(() {
        _routes = routes;
        _truckIds
          ..clear()
          ..addAll(routes.map((e) => e.truckId).where((id) => id.isNotEmpty));
      });
    } catch (e) {
      _showError("Erro ao carregar rotas: $e");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  void _showOnMap(List<LatLng> coordinates) {
    setState(() {
      _currentRoute = coordinates;
    });
  }

  void _confirmDeleteRoute(String routeId) async {
    final shouldDelete = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text("Confirmar eliminação"),
            content: const Text(
              "Tens a certeza que queres eliminar esta rota?",
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text("Cancelar"),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(true),
                style: TextButton.styleFrom(foregroundColor: Colors.red),
                child: const Text("Eliminar"),
              ),
            ],
          ),
    );

    if (shouldDelete == true) {
      try {
        await RouteService.deleteRoute(routeId);
        await _fetchRoutes();
      } catch (e) {
        _showError("Erro ao eliminar rota: $e");
      }
    }
  }

  List<RouteData> get _filteredRoutes {
    if (_selectedTruckId == null || _selectedTruckId!.isEmpty) return _routes;
    return _routes.where((route) => route.truckId == _selectedTruckId).toList();
  }

  Future<void> _generateFilteredRoute() async {
    final truckId = _truckInputController.text.trim();
    if (truckId.isEmpty) {
      _showError("Por favor, introduz um Truck ID válido.");
      return;
    }

    try {
      final bins = await BinService.getBins();
      final selectedBins =
          bins
              .where((b) => b.fillLevel != null)
              .where((b) => int.tryParse(b.fillLevel!) != null)
              .where((b) => int.parse(b.fillLevel!) < _selectedThreshold)
              .toList();

      if (selectedBins.isEmpty) {
        _showError("Nenhum caixote abaixo do nível selecionado.");
        return;
      }

      final coordinates =
          selectedBins.map((b) => LatLng(b.lat, b.lon)).toList();
      await RouteService.addRoute(coordinates: coordinates, truckId: truckId);

      _truckInputController.clear();
      await _fetchRoutes();
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Rota criada com sucesso!")));
    } catch (e) {
      _showError("Erro ao gerar rota: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Gestão de Rotas")),
      body: RefreshIndicator(
        onRefresh: _fetchRoutes,
        child: Column(
          children: [
            Card(
              margin: const EdgeInsets.all(16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: SizedBox(
                height: 300,
                width: double.infinity,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: MapWidget(
                    routeCoordinates: _currentRoute,
                    binLocations: const [],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 3,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        "Gerar nova rota",
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: _truckInputController,
                        decoration: const InputDecoration(
                          labelText: "Truck ID",
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 10),
                      DropdownButtonFormField<int>(
                        value: _selectedThreshold,
                        decoration: const InputDecoration(
                          labelText: "Nível máximo de enchimento (%)",
                          border: OutlineInputBorder(),
                        ),
                        items: List.generate(
                          10,
                          (i) => DropdownMenuItem(
                            value: (i + 1) * 10,
                            child: Text("${(i + 1) * 10}%"),
                          ),
                        ),
                        onChanged: (val) {
                          setState(() => _selectedThreshold = val ?? 50);
                        },
                      ),
                      const SizedBox(height: 10),
                      ElevatedButton.icon(
                        icon: const Icon(Icons.add_road),
                        label: const Text("Gerar Rota"),
                        onPressed: _generateFilteredRoute,
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  const Text("Filtrar por Truck ID:"),
                  const SizedBox(width: 12),
                  DropdownButton<String>(
                    value: _selectedTruckId,
                    hint: const Text("Todos"),
                    items: [
                      const DropdownMenuItem(value: null, child: Text("Todos")),
                      ..._truckIds.map(
                        (id) => DropdownMenuItem(value: id, child: Text(id)),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() => _selectedTruckId = value);
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child:
                  _filteredRoutes.isEmpty
                      ? const Center(child: Text("Nenhuma rota encontrada."))
                      : ListView.builder(
                        itemCount: _filteredRoutes.length,
                        itemBuilder: (context, index) {
                          final route = _filteredRoutes[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 6,
                            ),
                            child: ListTile(
                              title: Text(
                                "Truck: ${route.truckId.isEmpty ? 'N/D' : route.truckId} | ID: ${route.routeId}",
                              ),
                              subtitle: Text(
                                "${route.day.toString().padLeft(2, '0')}/${route.month.toString().padLeft(2, '0')}/${route.year} • Paragens: ${route.coordinates.length}",
                              ),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.map),
                                    onPressed:
                                        () => _showOnMap(route.coordinates),
                                  ),
                                  IconButton(
                                    icon: const Icon(
                                      Icons.delete,
                                      color: Colors.red,
                                    ),
                                    onPressed:
                                        () =>
                                            _confirmDeleteRoute(route.routeId),
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
      ),
    );
  }
}
