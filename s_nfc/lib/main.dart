import 'package:flutter/material.dart';
import 'nfc_page.dart';  // Import NFC page

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NFC Reader',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: NFCReaderScreen(),  // Load the NFC page
    );
  }
}
