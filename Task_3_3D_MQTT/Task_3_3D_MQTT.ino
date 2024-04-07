#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>

const char* ssid = "TP-Link_7722";
const char* password = "38118753";

const int trigPin = 2;
const int echoPin = 3;
const int ledPin = 4;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "mqtt-dashboard.com";
const int port = 1883;
const char topic[] = "SIT210/test";

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(ledPin, OUTPUT);

  while (!Serial) {}

  Serial.print("Attempting to connect to SSID: ");
  Serial.println(ssid);

  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print(".");
    delay(5000);
  }

  Serial.println("You're connected to the network");
  Serial.println();

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  mqttClient.onMessage(onMqttMessage);

  Serial.print("Subscribing to topic: ");
  Serial.println(topic);
  Serial.println();

  mqttClient.subscribe(topic);
}

void loop() {
  mqttClient.poll();

  unsigned long currentMillis = millis();

  if (currentMillis % 2000 == 0) {
    publishMessage();
  }
}

//Writing Message for HiveMQ
//Defining the difference between Pat/Wave signals
void publishMessage() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  float duration = pulseIn(echoPin, HIGH);
  float distance = (duration * 0.0343) / 2; //cm

  Serial.print("Distance: ");
  Serial.println(distance);
  Serial.print("cm");

  if (distance < 10) { 
    publish("Pat signal recorded!");
  } else if (distance >= 10 && distance <= 30) { 
    publish("Wave signal recorded!");
  }
}

//Sending message on HiveMQ
void publish(const char* message) {
  Serial.print("Sending message to topic: ");
  Serial.println(topic);

  mqttClient.beginMessage(topic);
  mqttClient.print(message);
  mqttClient.endMessage();
  delay(1000);
}


//for output on Serial Monitor + blinking mechanism
void onMqttMessage(int messageSize) {
  Serial.print("Received a message with topic '");
  Serial.print(mqttClient.messageTopic());
  Serial.print("', length ");
  Serial.print(messageSize);
  Serial.println(" bytes:");

  String message = mqttClient.readString();
  Serial.print("Message: ");
  Serial.println(message);
  Serial.println();

  if (message == "Wave signal recorded!") {
    flashLED(3, 300); //"Wave" signals flashes 3 times at a slower rate
  } else if (message == "Pat signal recorded!") {
    flashLED(5, 200); //"Pat" signals flashes 5 times at a faster rate
  }
}

//Loop function for flashing LED
void flashLED(int flashes, int delayTime) {
  for (int i = 0; i < flashes; i++) {
    digitalWrite(ledPin, HIGH);
    delay(delayTime);
    digitalWrite(ledPin, LOW);
    delay(delayTime);
  }
}
