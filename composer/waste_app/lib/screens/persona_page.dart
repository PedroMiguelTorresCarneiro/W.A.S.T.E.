import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../services/user_service.dart';

class PersonaPage extends StatefulWidget {
  const PersonaPage({super.key});

  @override
  State<PersonaPage> createState() => _PersonaPageState();
}

class _PersonaPageState extends State<PersonaPage> {
  late Future<Map<String, dynamic>> _userFuture;
  String? qrCodeData;
  String? message;

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  void _loadUser() {
    final uid = FirebaseAuth.instance.currentUser?.uid;
    if (uid != null) {
      setState(() {
        _userFuture = UserService.fetchFullUser(uid);
      });
    } else {
      _userFuture = Future.error("Utilizador não autenticado");
    }
  }

  Future<void> _redeemDiscount(String uid, int usageCount) async {
    final int desconto = (usageCount / 10).floor().clamp(0, 6);
    final mensagem =
        "O número de vezes que utilizou os caixotes foi: $usageCount\nO que corresponde a uma dedução de IVA de: ${desconto}%";

    final codificado = base64Encode(utf8.encode("DESCONTO:$desconto%"));

    setState(() {
      qrCodeData = codificado;
      message = mensagem;
    });

    try {
      await UserService.resetUsage(uid);
      _loadUser(); // 🔁 Refresh dos dados
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Erro ao reiniciar contagem: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 247, 247, 247),
      appBar: AppBar(
        title: const Text("Perfil do Utilizador"),
        backgroundColor: const Color.fromARGB(255, 247, 247, 247),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _userFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text("Erro: ${snapshot.error}"));
          } else if (!snapshot.hasData) {
            return const Center(child: Text("Dados não disponíveis."));
          }

          final data = snapshot.data!;
          final role = data['role'] ?? "user";
          final usageCount = data['usage_count'] ?? 0;
          final imei = data['imei'] ?? "Não disponível";
          final displayName =
              FirebaseAuth.instance.currentUser?.displayName ?? "Utilizador";
          final photoUrl = FirebaseAuth.instance.currentUser?.photoURL;
          final uid = FirebaseAuth.instance.currentUser?.uid ?? "";

          return SingleChildScrollView(
            child: Center(
              child: Column(
                children: [
                  const SizedBox(height: 20),
                  SizedBox(
                    width: screenWidth * 0.5,
                    height: screenHeight * 0.6,
                    child: Card(
                      color: Colors.grey[200],
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 6,
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            CircleAvatar(
                              radius: 48,
                              backgroundImage: NetworkImage(
                                photoUrl ??
                                    "https://ui-avatars.com/api/?name=${displayName.replaceAll(' ', '+')}",
                              ),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              displayName,
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Text(
                                  "Função: ",
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                Text(
                                  role == "admin"
                                      ? "Administrador"
                                      : "Utilizador",
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            RichText(
                              text: TextSpan(
                                style: const TextStyle(color: Colors.black),
                                children: [
                                  const TextSpan(
                                    text: "IMEI: ",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  TextSpan(text: imei),
                                ],
                              ),
                            ),
                            const SizedBox(height: 8),
                            RichText(
                              text: TextSpan(
                                style: const TextStyle(color: Colors.black),
                                children: [
                                  const TextSpan(
                                    text: "Utilizações: ",
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  TextSpan(text: usageCount.toString()),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: screenWidth * 0.6,
                    child: Card(
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          children: [
                            ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.black,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 24,
                                  vertical: 12,
                                ),
                              ),
                              onPressed: () => _redeemDiscount(uid, usageCount),
                              child: const Text("Redimir Desconto"),
                            ),
                            if (qrCodeData != null) ...[
                              const SizedBox(height: 20),
                              QrImageView(
                                data: qrCodeData!,
                                version: QrVersions.auto,
                                size: 180,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                message ?? '',
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontSize: 14),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
