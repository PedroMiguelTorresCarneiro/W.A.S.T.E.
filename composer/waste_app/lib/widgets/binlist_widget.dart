import 'package:flutter/material.dart';
import 'package:waste_app/services/composer_bin_service.dart';

class BinListWidget extends StatelessWidget {
  final List<Bin> bins;

  const BinListWidget({super.key, required this.bins});

  @override
  Widget build(BuildContext context) {
    if (bins.isEmpty) {
      return const Text("Nenhum contentor disponível.");
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          bins.map((bin) {
            final coords =
                "Lat: ${bin.lat.toStringAsFixed(4)}, Lon: ${bin.lon.toStringAsFixed(4)}";
            final fill = bin.fillLevel != null ? "${bin.fillLevel}%" : "N/D";

            return Container(
              margin: const EdgeInsets.symmetric(vertical: 4),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        bin.sensorSerial,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(coords),
                    ],
                  ),
                  Text(
                    fill,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            );
          }).toList(),
    );
  }
}
