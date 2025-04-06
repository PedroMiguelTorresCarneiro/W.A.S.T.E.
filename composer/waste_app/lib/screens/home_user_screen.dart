import 'package:flutter/material.dart';

// 3. Home Page (Common User)
class HomeUserPage extends StatelessWidget {
  const HomeUserPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("W.A.S.T.E."),
        actions: [IconButton(icon: Icon(Icons.settings), onPressed: () {})],
      ),
      body: Column(
        children: [
          Card(
            child: Container(
              height: 300,
              child: Center(child: Text("Mapa aqui")),
            ),
          ),
          Card(
            child: ListTile(
              title: Text("Lista de caixotes"),
              subtitle: Text("Com nível de enchimento"),
            ),
          ),
        ],
      ),
    );
  }
}
