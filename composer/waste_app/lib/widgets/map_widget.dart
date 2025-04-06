import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapWidget extends StatelessWidget {
  final List<LatLng> routeCoordinates;
  final List<LatLng> binLocations;

  const MapWidget({
    super.key,
    required this.routeCoordinates,
    required this.binLocations,
  });

  LatLng _calculateCenter(List<LatLng> allPoints) {
    double avgLat =
        allPoints.map((p) => p.latitude).reduce((a, b) => a + b) /
        allPoints.length;
    double avgLon =
        allPoints.map((p) => p.longitude).reduce((a, b) => a + b) /
        allPoints.length;
    return LatLng(avgLat, avgLon);
  }

  double _calculateZoom(List<LatLng> points) {
    if (points.length <= 1) return 15.0;
    final lats = points.map((p) => p.latitude);
    final lons = points.map((p) => p.longitude);

    final latSpread =
        (lats.reduce((a, b) => a > b ? a : b) -
                lats.reduce((a, b) => a < b ? a : b))
            .abs();
    final lonSpread =
        (lons.reduce((a, b) => a > b ? a : b) -
                lons.reduce((a, b) => a < b ? a : b))
            .abs();

    final maxSpread = latSpread > lonSpread ? latSpread : lonSpread;

    if (maxSpread < 0.005) return 17.0;
    if (maxSpread < 0.01) return 16.0;
    if (maxSpread < 0.02) return 15.0;
    if (maxSpread < 0.05) return 14.0;
    if (maxSpread < 0.1) return 13.0;
    if (maxSpread < 0.2) return 12.0;
    return 11.0;
  }

  @override
  Widget build(BuildContext context) {
    final allPoints = [...binLocations, ...routeCoordinates];

    final center =
        allPoints.isNotEmpty
            ? _calculateCenter(allPoints)
            : LatLng(40.6221, -8.628); // fallback Aveiro

    final zoom = _calculateZoom(allPoints);

    return FlutterMap(
      options: MapOptions(center: center, zoom: zoom),
      children: [
        TileLayer(
          urlTemplate: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
          subdomains: ['a', 'b', 'c'],
        ),
        if (routeCoordinates.isNotEmpty)
          PolylineLayer(
            polylines: [
              Polyline(
                points: routeCoordinates,
                color: Colors.blue,
                strokeWidth: 4.0,
              ),
            ],
          ),
        if (binLocations.isNotEmpty)
          MarkerLayer(
            markers:
                binLocations
                    .map<Marker>(
                      (coord) => Marker(
                        width: 40.0,
                        height: 40.0,
                        point: coord,
                        child: const Icon(
                          Icons.delete,
                          color: Colors.red,
                          size: 30,
                        ),
                      ),
                    )
                    .toList(),
          ),
      ],
    );
  }
}
