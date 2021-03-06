/* Garage door sensor and control code

*/

// constants won't change. Used here to 
// set pin numbers:
const int ledPin =     13;      // the number of the LED pin
const int sensorPin =   2;      // the number of the door sensor pin
const int pirPin =      3;      // the number of the motion detector pin
const int relayPin =    4;      // the number of the door opening relay pin
const int buttonPin =   5;      // the number of the button switch pin


// Variables will change:
int ledState = LOW;             // ledState used to set the LED
long previousMillis = 0;        // will store last time LED was updated
long interval = 250;            // interval at which to blink (milliseconds)
String command;

void setup() {
  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);
  pinMode(sensorPin, INPUT);
  digitalWrite(sensorPin, HIGH);
  pinMode(pirPin, INPUT);
  digitalWrite(pirPin, LOW);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
  pinMode(buttonPin, INPUT);
  digitalWrite(buttonPin, HIGH);
  //delay(20000); // Wait for PIR to warm up
  Serial.begin(9600);
}

String checkButton() {
  int state = digitalRead(buttonPin);
  if (state == HIGH) {
    return "UNPRESSED";
  } else {
    return "PRESSED";
  }
}

String checkDoor() {
  int state = digitalRead(sensorPin);
  if (state == LOW) {
    return "CLOSED";
  } else {
    return "OPEN";
  }
}

String checkMotion() {
  int state = digitalRead(pirPin);
  if (state == LOW) {
    return "NOMOTION";
  } else {
    return "MOTION";
  }
}

void checkRelay() {
  int i=0;
  while (Serial.available()) {
//  if (Serial.available()) {
      char c = Serial.read();
      if (c == '!') {
        if (command.substring(0,5) == "OPEN:") {
          String wait = command.substring(5);
          toggleRelay(wait.toInt());
          //Serial.println("Relay toggled with delay: " + String(command) );
        }
        command = "";
      } else {      
      command += c;  
      }
    }
  //Serial.println(String(command));
}

void toggleRelay(int wait) {
  //probably silly use of recursion but meh
  if (wait != 0) {
    toggleRelay(0);
    delay(wait);
  }
  digitalWrite(relayPin, LOW);
  delay(100);
  digitalWrite(relayPin, HIGH);
}

void loop()
{
  unsigned long currentMillis = millis();
 
  if(currentMillis - previousMillis > interval) {
    previousMillis = currentMillis;   
    checkRelay();
    Serial.println(checkDoor() + ":" + checkMotion() + ":" + checkButton());
    digitalWrite(ledPin, ledState);
  }
}

