import 'package:flutter/material.dart';
import 'package:flutter_nfc_kit/flutter_nfc_kit.dart';
import 'dart:convert';
import 'package:http/http.dart' as http; // <-- Import HTTP package
//import 'package:android_id/android_id.dart';
import 'package:flutter/services.dart';
import 'package:flutter_device_imei/flutter_device_imei.dart';


class NFCReaderScreen extends StatefulWidget {
  @override
  _NFCReaderScreenState createState() => _NFCReaderScreenState();
}

class _NFCReaderScreenState extends State<NFCReaderScreen> {
  String _nfcData = "Press the button to scan an NFC tag.";
  //final _androidIdPlugin = DeviceImei();
  var _androidId = 'Unknown';
  String tagID2 = "7f3a9b2c4d5e6f1a";

  Future<void> readNFC() async {
    String androidId;
    try {
      setState(() => _nfcData = "Scanning for NFC tag...");

      // Check NFC availability
      var availability = await FlutterNfcKit.nfcAvailability;
      if (availability != NFCAvailability.available) {
        setState(() => _nfcData = "NFC is not available.");
        return;
      }

      // Poll for an NFC tag
      var tag = await FlutterNfcKit.poll(
        timeout: Duration(seconds: 10),
        iosMultipleTagMessage: "Multiple tags found!",
        iosAlertMessage: "Scan your tag"
      );

      String tagID = tag.id; // Extract tag ID

      try {
      androidId = await FlutterDeviceImei.instance.getIMEI() ?? 'Unknown ID';
      print('Retrieved Android ID: $androidId'); // Output to console
      } on PlatformException {
      androidId = 'Failed to get Android ID.';
      print('Error retrieving Android ID');
      }
      setState(() => _androidId = androidId);


      // Check if the tag supports NDEF
      if (tag.ndefAvailable == true) {
        String ndefContent = "";
        for (var record in await FlutterNfcKit.readNDEFRecords(cached: false)) {
          ndefContent += "Record Type: ${record.type}\n";
          if (record.payload != null) {
            ndefContent += "Payload: ${utf8.decode(record.payload!)}\n";
          } else {
            ndefContent += "Payload: (null)\n";
          }
        }
        setState(() => _nfcData = ndefContent);
      } else {
        setState(() => _nfcData = "Tag ID: $tagID2\n(No NDEF data available)");
      }

      //  Send the NFC tag ID to the Node.js server
      await sendNfcDataToServer(tagID2,androidId);

    } catch (e) {
      setState(() => _nfcData = "Error reading NFC: $e");
    }
  }




  // 🔵 Function to send NFC tag data to Node.js server
  Future<void> sendNfcDataToServer(String tagID2,String androidId) async {
    const String serverUrl = 'http://grupo2-egs-deti.ua.pt/v1/posting/nfc'; // Update with your server IP
    
    try {
      var response = await http.post(
        Uri.parse(serverUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"imei": androidId,"serial": tagID2,"timestamp": "2025-05-11T16:37:36.293Z"}),
      );

      if (response.statusCode == 200) {
        print(" NFC data sent successfully: ${response.body}");
      } else {
        print(" Failed to send NFC data. Status code: ${response.statusCode}");
      }
    } catch (e) {
      print(" Error sending NFC data: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("NFC Reader")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _nfcData,
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: readNFC,
                child: Text("Scan NFC Tag"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

