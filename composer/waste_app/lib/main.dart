import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:waste_app/screens/admin_dashboard.dart';
import 'package:waste_app/screens/splash_screen.dart';
import 'package:waste_app/screens/login_screen.dart';
import 'package:waste_app/screens/user_dashboard.dart';
import 'firebase_options.dart'; // Gerado pelo flutterfire configure

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ✅ Só inicializa se ainda não estiver inicializado
  if (Firebase.apps.isEmpty) {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'W.A.S.T.E.',
      theme: ThemeData(primarySwatch: Colors.green),
      home: const SplashScreen(),
      onGenerateRoute: (settings) {
        final args = settings.arguments as Map<String, dynamic>?;

        switch (settings.name) {
          case '/login':
            return MaterialPageRoute(builder: (_) => const LoginPage());
          case '/home':
            return MaterialPageRoute(
              builder: (_) => UserDashboard(name: args?['name'] ?? 'User'),
            );
          case '/admin':
            return MaterialPageRoute(
              builder: (_) => AdminDashboard(name: args?['name'] ?? 'Admin'),
            );
          default:
            return MaterialPageRoute(builder: (_) => const LoginPage());
        }
      },
    );
  }
}
