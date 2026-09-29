// ESP32 Serial Test Device
// Listens for newline-terminated text commands over USB serial
// and replies with a single line starting with "OK" or "ERR".

#include <Arduino.h>

const char* FW_VERSION = "1.0.1";

// ---- Change these to match the pins you used ----
const int LED_PIN    = 2;   // LED (through a 220 ohm resistor to GND)
const int BUTTON_PIN = 13;  // Push button (other leg to GND)
const int POT_PIN    = 1;   // Potentiometer middle pin (must be an ADC pin)
// -------------------------------------------------

const size_t MAX_CMD_LEN = 128;

String inputBuffer;
bool overflow = false;
bool ledState = false;

void handleCommand(String cmd) {
  cmd.trim();

  if (cmd.length() == 0) {
    Serial.println("ERR EMPTY");
  } else if (cmd == "PING") {
    Serial.println("OK PONG");
  } else if (cmd == "VERSION") {
    Serial.print("OK ");
    Serial.println(FW_VERSION);
  } else if (cmd == "LED ON") {
    digitalWrite(LED_PIN, HIGH);
    ledState = true;
    Serial.println("OK LED ON");
  } else if (cmd == "LED OFF") {
    digitalWrite(LED_PIN, LOW);
    ledState = false;
    Serial.println("OK LED OFF");
  } else if (cmd == "LED?") {
    Serial.println(ledState ? "OK LED ON" : "OK LED OFF");
  } else if (cmd == "READ POT") {
    Serial.print("OK ");
    Serial.println(analogRead(POT_PIN));   // 0-4095 on ESP32
  } else if (cmd == "READ BTN") {
    // INPUT_PULLUP: pin reads LOW when the button is pressed
    Serial.println(digitalRead(BUTTON_PIN) == LOW ? "OK 1" : "OK 0");
  } else if (cmd.startsWith("ECHO ")) {
    Serial.print("OK ");
    Serial.println(cmd.substring(5));
  } else {
    Serial.println("ERR UNKNOWN_CMD");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  digitalWrite(LED_PIN, LOW);
  inputBuffer.reserve(MAX_CMD_LEN);
  delay(500);
  Serial.println("READY");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n') {
      if (overflow) {
        Serial.println("ERR TOO_LONG");
      } else {
        handleCommand(inputBuffer);
      }
      inputBuffer = "";
      overflow = false;
    } else if (c != '\r') {
      if (inputBuffer.length() < MAX_CMD_LEN) {
        inputBuffer += c;
      } else {
        overflow = true;   // keep reading until newline, then report error
      }
    }
  }
}
