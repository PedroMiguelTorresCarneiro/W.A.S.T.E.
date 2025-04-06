import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/kafka_service.dart';
import '../services/api_service.dart';
import 'package:latlong2/latlong.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class Composer {
  static Future<List<LatLng>> getRouteData() async {
    return await ApiService.fetchRoute();
  }

  // 🔹 Google Sign-In
  static Future<void> loginWithGoogle(BuildContext context) async {
    await AuthService().loginWithGoogle(context);
  }

  // 🔹 Github Sign-In
  static Future<void> loginWithGitHub(BuildContext context) async {
    await AuthService().loginWithGitHub(context);
  }

  // 🔹 Log Out
  static Future<void> logout(BuildContext context) async {
    await AuthService().signOut(context);
  }

  // 🔹 Listen to Kafka Messages
  static Stream<String> getKafkaMessages() {
    return KafkaService.messageStream;
  }

  static void startKafka() {
    KafkaService.connect();
  }

  // Start Collection no Firestone para os Bins
  static Future<void> addBin({
    required String binId,
    required double latitude,
    required double longitude,
    required String nfcTag,
    required int fullness,
  }) async {
    try {
      await FirebaseFirestore.instance.collection('bins').add({
        'bin_id': binId,
        'latitude': latitude,
        'longitude': longitude,
        'nfcTag': nfcTag,
        'fullness': fullness,
        'created_at': FieldValue.serverTimestamp(),
      });
      print("✅ Bin added successfully.");
    } catch (e) {
      print("❌ Failed to add bin: $e");
    }
  }
}
