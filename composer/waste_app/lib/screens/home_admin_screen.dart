import 'package:flutter/material.dart';

// 4. Home Page (Admin)
class HomeAdminPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("W.A.S.T.E. - Admin"),
        actions: [IconButton(icon: Icon(Icons.settings), onPressed: () {})],
      ),
      body: Column(
        children: [
          Card(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                ElevatedButton(onPressed: () {}, child: Text("Rotas")),
                ElevatedButton(onPressed: () {}, child: Text("Gestão da Rede")),
              ],
            ),
          ),
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
