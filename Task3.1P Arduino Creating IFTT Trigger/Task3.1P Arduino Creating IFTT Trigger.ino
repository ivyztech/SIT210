#include <Wire.h>
#include <WiFiNINA.h>

const int SENSOR_ADDRESS = 0x23; // I2C address of the BH1750FVI sensor

// WiFi credentials
char ssid[] = "TP-Link_7722";
char pass[] = "38118753";

// IFTTT Maker Webhooks URL and event name
const char *DETECTED_SUNLIGHT_URL = "https://maker.ifttt.com/trigger/sunlight_detected/with/key/le0rzI13QTQtD0TTi6ErhS05xMaQqYWS4Gcop8hZAwD";

void setup() {
  Serial.begin(9600); 
  Wire.begin(); 
  delay(1000); 
  connectWiFi(); 
}

void loop() {
  //Facilitating I2C bus from light sensor
  Wire.beginTransmission(SENSOR_ADDRESS);
  Wire.write(0x10); 
  Wire.endTransmission();
  delay(200); 
  Wire.requestFrom(SENSOR_ADDRESS, 2);

  // Converting received data into lux value
  if (Wire.available() >= 2) {
    int sensorData = Wire.read() << 8 | Wire.read(); 
    float lux = sensorData / 1.2; 
    
    // Print the sensor data to the serial monitor
    Serial.print("Light Intensity: ");
    Serial.print(lux);
    Serial.println(" lux");

    //Triggering Webhook
    sendWebhook(DETECTED_SUNLIGHT_URL, lux);

    // Add a delay before the next reading
    delay(600000); // EVERY 10 MINUTES
  }
}

//Connecting to WiFi
void connectWiFi() {
  Serial.print("Connecting to Wi-Fi...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println("Failed to connect to Wi-Fi. Retrying...");
    delay(5000);
  }
  Serial.println("Connected to Wi-Fi!");
}

//This is the MESSAGE written in the email depending on the predefined thresholds for sunlight
String getOpeningMessage(float lux) {
  const char *messages[] = {
    "There's barely any sun in your terrarium! It is advisable to keep the terrarium in sunlight for an average of 2 hours a day.", // 0-100 lux
    "How lovely! Your terrarium has lots of sunlight. Keep the sun shining for an average of two hours a day for the best results!", // 100-800
    "Cover your terrarium! That's too much sun for two hours straight!" // 800-1000 up
  };
  if (lux <= 100) return messages[0];
  else if (lux <= 800) return messages[1];
  else return messages[2];
}


//This is the SUBJECT written in the email depending on the predefined thresholds for sunlight
String getSubject(float lux) {
  const char *subject[] = {
    "No Sunlight!", // 0-100 lux
    "Sunlight Detected!", // 100-800
    "TOO MUCH SUNLIGHT!!!!" // 800-1000 up
  };
  if (lux <= 100) return subject[0];
  else if (lux <= 800) return subject[1];
  else return subject[2];
}

void sendWebhook(const char *webhookURL, float luxValue) {
  // Create HTTP client object
  WiFiClient client;

  // Create JSON payload so that the values can be replaced in the predefined action
  String payload = "{\"value1\":\"" + String(luxValue) + "\",\"value2\":\"" + getSubject(luxValue) + "\",\"value3\":\"" + getOpeningMessage(luxValue) + "\"}";

  // Send HTTP POST request to IFTTT Maker Webhooks
  if (client.connect("maker.ifttt.com", 80)) {
    client.print("POST ");
    client.print(webhookURL);
    client.println(" HTTP/1.1");
    client.println("Host: maker.ifttt.com");
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(payload.length());
    client.println("Connection: close");
    client.println();
    client.println(payload);
    client.stop();
    Serial.println("Webhook sent: " + String(webhookURL));
  } else {
    Serial.println("Failed to send webhook!");
  }
}
