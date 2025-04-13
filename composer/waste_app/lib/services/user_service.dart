import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/config.dart';

class UserService {
  // 🔹 Obter utilizador completo
  static Future<Map<String, dynamic>> fetchFullUser(String uid) async {
    final url = Uri.parse("${AppConfig.fastApiBase}/users/$uid");
    final res = await http.get(url);

    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception("Erro ao buscar o utilizador: ${res.body}");
    }
  }

  // 🔹 Incrementar usage_count
  static Future<void> incrementUsage(String uid) async {
    final url = Uri.parse(
      "${AppConfig.fastApiBase}/users/$uid/increment_usage",
    );
    final response = await http.post(url);

    if (response.statusCode != 200) {
      throw Exception("Erro ao incrementar o uso: ${response.body}");
    }
  }

  // 🔹 Buscar utilizador por IMEI
  // 🔹 Buscar utilizador por IMEI
  static Future<Map<String, dynamic>> fetchUserByImei(String imei) async {
    final url = Uri.parse("${AppConfig.fastApiBase}/users/by_imei/$imei");
    final res = await http.get(url);

    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception("Utilizador não encontrado com o IMEI: $imei");
    }
  }

  static Future<void> resetUsage(String uid) async {
    final url = Uri.parse("${AppConfig.fastApiBase}/users/$uid/reset_usage");
    final response = await http.post(url);

    if (response.statusCode != 200) {
      throw Exception("Erro ao resetar usage_count: ${response.body}");
    }
  }
}
