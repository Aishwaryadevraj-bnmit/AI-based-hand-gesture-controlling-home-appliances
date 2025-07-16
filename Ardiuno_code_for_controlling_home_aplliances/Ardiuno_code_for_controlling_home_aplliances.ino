// Corrected and Clean Code

int relay1 = 10; // IN1 of Relay Module
int relay2 = 9;  // IN2 of Relay Module

String input = "";

void setup() {
  Serial.begin(9600);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);

  // Initially turn OFF both (HIGH = OFF for active LOW relays)
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
}

void loop() {
  if (Serial.available()) {
    input = Serial.readStringUntil('\n');
    input.trim();  // Remove newline and whitespace

    if (input == "1") {
      // Only Relay 1 ON
      digitalWrite(relay1, LOW);   // ON
      digitalWrite(relay2, HIGH);  // OFF
    }
    else if (input == "2") {
      // Only Relay 2 ON
      digitalWrite(relay1, HIGH);  // OFF
      digitalWrite(relay2, LOW);   // ON
    }
    else if (input == "5") {
      // Both Relays ON
      digitalWrite(relay1, HIGH);   // ON
      digitalWrite(relay2, HIGH);   // ON
    }
    else if (input == "0" || input == "3" || input == "4") {
      // Both Relays OFF
      digitalWrite(relay1, LOW);  // OFF
      digitalWrite(relay2, LOW);  // OFF
    }

    // Optional debug print
    Serial.println("Received: " + input);
  }
}