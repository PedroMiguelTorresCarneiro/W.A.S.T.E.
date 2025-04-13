import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:waste_app/composer.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "W.A.S.T.E.",
                style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 60),

              // Icons side by side
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Google login button
                  IconButton(
                    icon: const FaIcon(FontAwesomeIcons.google),
                    color: Colors.redAccent,
                    iconSize: 48,
                    tooltip: "Login com Google",
                    onPressed: () async {
                      await Composer.loginWithGoogle(context);
                    },
                  ),
                  const SizedBox(width: 40),
                  // GitHub login button
                  IconButton(
                    icon: const FaIcon(FontAwesomeIcons.github),
                    color: Colors.black,
                    iconSize: 48,
                    tooltip: "Login com GitHub",
                    onPressed: () async {
                      await Composer.loginWithGitHub(context);
                    },
                  ),
                ],
              ),

              const SizedBox(height: 20),
              const Text(
                "Escolhe um método de login",
                style: TextStyle(fontSize: 16),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
