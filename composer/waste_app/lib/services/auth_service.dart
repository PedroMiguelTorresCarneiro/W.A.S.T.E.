import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
//import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import '../config/config.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  static const adminCode = 'ADMIN_2025';

  User? get currentUser => _auth.currentUser;
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  // 🔹 Login com Google
  Future<void> loginWithGoogle(BuildContext context) async {
    try {
      final googleUser =
          await GoogleSignIn(
            clientId:
                kIsWeb
                    ? '1014407108227-a3l1iuo845vortnval1133kqmisfaj2c.apps.googleusercontent.com'
                    : null,
          ).signIn();

      if (googleUser == null) return;

      final googleAuth = await googleUser.authentication;
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      final userCredential = await _auth.signInWithCredential(credential);

      //final user = userCredential.user!;
      // 🖨️ Imprimir UID e nome
      //print('✅ UID: ${user.uid}');
      //print('✅ Nome: ${user.displayName}');

      await _handleUserAfterLogin(context, userCredential.user!);
    } catch (e) {
      print("❌ Google login failed: $e");
      _showError(context, "Google login failed: $e");
    }
  }

  // 🔹 Login com GitHub
  Future<void> loginWithGitHub(BuildContext context) async {
    try {
      final githubProvider =
          GithubAuthProvider()
            ..addScope('read:user')
            ..setCustomParameters({'allow_signup': 'false'});

      UserCredential userCredential;

      if (kIsWeb) {
        // 🔹 WEB login com popup
        userCredential = await FirebaseAuth.instance.signInWithPopup(
          githubProvider,
        );
      } else {
        // 🔹 Mobile (não suportado no teu caso web-only)
        userCredential = await FirebaseAuth.instance.signInWithProvider(
          githubProvider,
        );
      }

      await _handleUserAfterLogin(context, userCredential.user!);
    } catch (e) {
      print("❌ GitHub login failed: $e");
      _showError(context, "GitHub login failed: $e");
    }
  }

  // 🔹 Lidar com o utilizador após login
  Future<void> _handleUserAfterLogin(BuildContext context, User user) async {
    //print("✅ UID: ${user.uid}");
    //print("✅ Nome: ${user.displayName}");

    final uri = Uri.parse(AppConfig.userExistsUrl(user.uid));
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      _showError(context, "Erro ao verificar utilizador");
      return;
    }

    final data = jsonDecode(response.body);

    String role;
    if (data["exists"] == false) {
      // ⚠️ Novo utilizador → perguntar se é admin
      role = await _askForAdminCode(context);

      final postUri = Uri.parse(AppConfig.createUserUrl);
      final postResponse = await http.post(
        postUri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'uid': user.uid,
          'role': role,
          'imei': '', // adicionar depois se quiseres
        }),
      );

      if (postResponse.statusCode != 200) {
        _showError(context, "Erro ao criar utilizador: ${postResponse.body}");
        return;
      }
    } else {
      role = data["role"];
    }

    final name = user.displayName ?? "Sem Nome";

    // 🔁 Redirecionar consoante o papel
    if (role == 'admin') {
      Navigator.pushReplacementNamed(
        context,
        '/admin',
        arguments: {'name': name},
      );
    } else {
      Navigator.pushReplacementNamed(
        context,
        '/home',
        arguments: {'name': name},
      );
    }
  }

  // 🔹 Popup para introdução do código de admin
  Future<String> _askForAdminCode(BuildContext context) async {
    final controller = TextEditingController();
    String role = 'user';

    await showDialog(
      context: context,
      barrierDismissible: false,
      builder:
          (_) => AlertDialog(
            title: const Text('Código de administrador'),
            content: TextField(
              controller: controller,
              decoration: const InputDecoration(
                hintText: 'Introduz o código (ou deixa vazio para user)',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  if (controller.text.trim() == adminCode) role = 'admin';
                  Navigator.of(context).pop();
                },
                child: const Text('Confirmar'),
              ),
            ],
          ),
    );

    return role;
  }

  // 🔹 Logout
  Future<void> signOut(BuildContext context) async {
    try {
      await _auth.signOut();
      Navigator.pushReplacementNamed(context, '/login');
    } catch (e) {
      _showError(context, "Sign out failed: $e");
    }
  }

  // 🔹 Erro genérico
  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }
}
