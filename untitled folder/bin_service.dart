import 'package:cloud_firestore/cloud_firestore.dart';

class BinService {
  static final CollectionReference binsCollection = FirebaseFirestore.instance
      .collection('bins');

  // 🔹 Adicionar novo caixote
  static Future<void> addBin({
    required String binId,
    required double latitude,
    required double longitude,
    required String nfcTag,
    required int fullness,
  }) async {
    try {
      await binsCollection.doc(binId).set({
        'bin_id': binId,
        'latitude': latitude,
        'longitude': longitude,
        'nfcTag': nfcTag,
        'fullness': fullness,
        'timestamp': FieldValue.serverTimestamp(),
      });
    } catch (e) {
      print('❌ Erro ao adicionar caixote: $e');
      rethrow;
    }
  }

  // 🔹 Obter lista de caixotes
  static Future<List<Map<String, dynamic>>> fetchBins() async {
    try {
      final snapshot = await binsCollection.get();
      return snapshot.docs
          .map((doc) => doc.data() as Map<String, dynamic>)
          .toList();
    } catch (e) {
      print('❌ Erro ao buscar caixotes: $e');
      return [];
    }
  }

  // 🔹 Atualizar caixote existente
  static Future<void> updateBinFullness(String binId, int newFullness) async {
    try {
      await binsCollection.doc(binId).update({'fullness': newFullness});
    } catch (e) {
      print('❌ Erro ao atualizar fullness: $e');
      rethrow;
    }
  }

  // 🔹 Apagar caixote
  static Future<void> deleteBin(String binId) async {
    try {
      await binsCollection.doc(binId).delete();
    } catch (e) {
      print('❌ Erro ao apagar caixote: $e');
      rethrow;
    }
  }
}
