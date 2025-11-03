const int RELAY_PRESSURE = 10;
const int RELAY_PUMP = 12;

void setup() {
  Serial.begin(9600);

  closeRelays();

  pinMode(RELAY_PRESSURE, OUTPUT);
  pinMode(RELAY_PUMP, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == '1') {
      openRelays();
    }
    if (command == '2') {
      closeRelays();
    }
  }
}

void openRelays() {
  digitalWrite(RELAY_PRESSURE, LOW);
  digitalWrite(RELAY_PUMP, LOW);
}

void closeRelays() {
  digitalWrite(RELAY_PRESSURE, HIGH);
  digitalWrite(RELAY_PUMP, HIGH);
}