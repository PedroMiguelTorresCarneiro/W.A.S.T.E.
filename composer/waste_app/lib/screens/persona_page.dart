import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/user_service.dart';

class PersonaPage extends StatefulWidget {
  const PersonaPage({super.key});

  @override
  State<PersonaPage> createState() => _PersonaPageState();
}

class _PersonaPageState extends State<PersonaPage> {
  late Future<Map<String, dynamic>> _userFuture;

  @override
  void initState() {
    super.initState();
    final uid = FirebaseAuth.instance.currentUser?.uid;
    if (uid != null) {
      _userFuture = UserService.fetchFullUser(uid); // método correto
    } else {
      _userFuture = Future.error("Utilizador não autenticado");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(
        255,
        247,
        247,
        247,
      ), // 🔹 Fundo preto
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

          return Container(
            color: Colors.white,
            child: Center(
              child: FractionallySizedBox(
                widthFactor: 0.5,
                heightFactor: 0.6,
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
                        Flexible(
                          flex: 3,
                          child: CircleAvatar(
                            radius: 48,
                            backgroundColor: Colors.grey[400],
                            backgroundImage: NetworkImage(
                              photoUrl ??
                                  "https://ui-avatars.com/api/?name=${Uri.encodeComponent(displayName)}&background=0D8ABC&color=fff",
                            ),
                            onBackgroundImageError: (_, __) {
                              setState(() {}); // força rebuild se falhar
                            },
                          ),
                        ),
                        const SizedBox(height: 16),
                        Flexible(
                          flex: 2,
                          child: Column(
                            children: [
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
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
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
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
