            /*Libraries*/
#include "FirebaseESP8266.h"
#include <ESP8266WiFi.h>

#include <FirebaseESP8266.h>
#include <WiFiClient.h> 
#include <WiFiManager.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h> //ESP Web Server Library to host a web page

/*---------------Firebase Setup---------------*/
#define WIFI_SSID "Z-techX"
#define WIFI_PASSWORD "00000000"
#define FIREBASE_HOST "ztechxroofgarden-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "KyHHzAPSY0T0vn7k40uUeOqAIDo3hIOsuWDnV5Tq"
#define WifiPB D1

FirebaseData fbdo;
ESP8266WebServer server(80);


// Soil Moisture Pins (Digital)
const int soilMoisturePin1 = D5;  // Update with your actual pin number
const int soilMoisturePin2 = D6;  // Update with your actual pin number

// Actuator Pins
const int irrigationPin = D1;
const int drainagePin = D2;

void setup() {
  Serial.begin(115200);

  // Setup pins
  pinMode(soilMoisturePin1, INPUT);
  pinMode(soilMoisturePin2, INPUT);
  pinMode(irrigationPin, OUTPUT);
  pinMode(drainagePin, OUTPUT);

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected!");

  // Connect to Firebase
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
}

void loop() {
  // Read soil moisture levels (Digital 0 or 1)
  int soilMoisture1 = digitalRead(soilMoisturePin1);
  int soilMoisture2 = digitalRead(soilMoisturePin2);

  // Print readings for debugging
  Serial.print("Soil Moisture 1: "); Serial.println(soilMoisture1);
  Serial.print("Soil Moisture 2: "); Serial.println(soilMoisture2);

  // Send sensor data to Firebase
  Firebase.setInt(fbdo,"sensors/soilMoisture1", soilMoisture1);
  Firebase.setInt(fbdo,"sensors/soilMoisture2", soilMoisture2);

  // Read irrigation and drainage commands from Firebase
  bool irrigationCommand = Firebase.getBool(fbdo,"commands/irrigation");
  bool drainageCommand = Firebase.getBool(fbdo,"commands/drainage");

  // Actuate based on commands
  if (irrigationCommand) {
    digitalWrite(irrigationPin, HIGH);  // Turn on irrigation
    Serial.println("Irrigation ON");
  } else {
    digitalWrite(irrigationPin, LOW);   // Turn off irrigation
    Serial.println("Irrigation OFF");
  }

  if (drainageCommand) {
    digitalWrite(drainagePin, HIGH);    // Turn on drainage
    Serial.println("Drainage ON");
  } else {
    digitalWrite(drainagePin, LOW);     // Turn off drainage
    Serial.println("Drainage OFF");
  }

  // Wait before next loop
  delay(1000);
}
