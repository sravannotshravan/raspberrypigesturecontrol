/*
 * Gesture-Controlled LED and Servo Motor - Arduino Code
 * 
 * This Arduino receives commands via USB Serial from the laptop
 * and controls an LED and continuous rotation servo motor.
 * 
 * Hardware Connections:
 * - LED: Pin 9 (PWM) + 220Ω resistor to GND
 * - Servo: Pin 8 (PWM)
 * 
 * Serial Protocol:
 * Commands from laptop:
 *   MODE:LED    - Switch to LED control mode
 *   MODE:MOTOR  - Switch to Motor control mode
 *   LED:ON      - Turn LED on
 *   LED:OFF     - Turn LED off
 *   LED:UP      - Increase LED brightness
 *   LED:DOWN    - Decrease LED brightness
 *   MOTOR:ON    - Turn motor on (start rotating)
 *   MOTOR:OFF   - Turn motor off (stop)
 *   MOTOR:UP    - Increase motor speed
 *   MOTOR:DOWN  - Decrease motor speed
 *   STATUS      - Request current status
 * 
 * Responses to laptop:
 *   STATUS:mode,led_state,led_level,motor_state,motor_level
 */

#include <Servo.h>

// Pin definitions
const int LED_PIN = 9;      // PWM pin for LED
const int SERVO_PIN = 8;    // PWM pin for Servo

// Device objects
Servo motor;

// State variables
String currentMode = "LED";  // Current control mode: "LED" or "MOTOR"
bool ledOn = false;
bool motorOn = false;
int ledLevel = 3;      // 0-5
int motorLevel = 3;    // 0-5

// Serial communication
String inputString = "";
boolean stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect (needed for native USB)
  }
  
  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, 0);  // Start off
  
  // Initialize Servo
  motor.attach(SERVO_PIN);
  motor.write(90);  // Neutral position (stopped for continuous rotation servo)
  
  // Reserve 64 bytes for input string
  inputString.reserve(64);
  
  // Send ready message
  Serial.println("READY:Arduino Gesture Control System");
  Serial.println("INFO:LED=Pin9, Servo=Pin8");
  Serial.flush();
}

void loop() {
  // Check for incoming serial commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

// Serial event handler (called automatically)
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n') {
      stringComplete = true;
    } else if (inChar != '\r') {
      inputString += inChar;
    }
  }
}

// Process incoming command
void processCommand(String command) {
  command.trim();
  
  if (command.startsWith("MODE:")) {
    String mode = command.substring(5);
    mode.toUpperCase();
    
    if (mode == "LED" || mode == "MOTOR") {
      currentMode = mode;
      Serial.print("MODE:");
      Serial.println(currentMode);
    }
  }
  else if (command.startsWith("LED:")) {
    String action = command.substring(4);
    action.toUpperCase();
    
    if (action == "ON") {
      ledTurnOn();
    } else if (action == "OFF") {
      ledTurnOff();
    } else if (action == "UP") {
      ledIncrease();
    } else if (action == "DOWN") {
      ledDecrease();
    }
  }
  else if (command.startsWith("MOTOR:")) {
    String action = command.substring(6);
    action.toUpperCase();
    
    if (action == "ON") {
      motorTurnOn();
    } else if (action == "OFF") {
      motorTurnOff();
    } else if (action == "UP") {
      motorIncrease();
    } else if (action == "DOWN") {
      motorDecrease();
    }
  }
  else if (command == "STATUS") {
    sendStatus();
  }
}

// LED Control Functions
void ledTurnOn() {
  ledOn = true;
  if (ledLevel == 0) {
    ledLevel = 3;  // Default to medium
  }
  setLedBrightness(ledLevel);
  Serial.println("LED:ON");
}

void ledTurnOff() {
  ledOn = false;
  analogWrite(LED_PIN, 0);
  Serial.println("LED:OFF");
}

void ledIncrease() {
  if (ledOn && ledLevel < 5) {
    ledLevel++;
    setLedBrightness(ledLevel);
  }
}

void ledDecrease() {
  if (ledOn && ledLevel > 1) {
    ledLevel--;
    setLedBrightness(ledLevel);
  }
}

void setLedBrightness(int level) {
  if (ledOn) {
    // Map level 1-5 to PWM 51-255 (20%-100%)
    int pwmValue = map(level, 1, 5, 51, 255);
    analogWrite(LED_PIN, pwmValue);
    
    int percentage = (level * 100) / 5;
    Serial.print("LED:LEVEL:");
    Serial.print(level);
    Serial.print(":");
    Serial.println(percentage);
  }
}

// Motor Control Functions
void motorTurnOn() {
  motorOn = true;
  if (motorLevel == 0) {
    motorLevel = 3;  // Default to medium
  }
  setMotorSpeed(motorLevel);
  Serial.println("MOTOR:ON");
}

void motorTurnOff() {
  motorOn = false;
  motor.write(90);  // Stop (neutral position)
  Serial.println("MOTOR:OFF");
}

void motorIncrease() {
  if (motorOn && motorLevel < 5) {
    motorLevel++;
    setMotorSpeed(motorLevel);
  }
}

void motorDecrease() {
  if (motorOn && motorLevel > 1) {
    motorLevel--;
    setMotorSpeed(motorLevel);
  }
}

void setMotorSpeed(int level) {
  if (motorOn) {
    // For continuous rotation servo:
    // 90 = stopped
    // 0-89 = reverse (not used)
    // 91-180 = forward rotation
    // Map level 1-5 to servo angles 100-180 (slow to fast forward)
    int servoAngle = map(level, 1, 5, 100, 180);
    motor.write(servoAngle);
    
    int percentage = (level * 100) / 5;
    Serial.print("MOTOR:LEVEL:");
    Serial.print(level);
    Serial.print(":");
    Serial.println(percentage);
  }
}

// Send current status
void sendStatus() {
  // Format: STATUS:mode,led_state,led_level,motor_state,motor_level
  Serial.print("STATUS:");
  Serial.print(currentMode);
  Serial.print(",");
  Serial.print(ledOn ? "ON" : "OFF");
  Serial.print(",");
  Serial.print(ledLevel);
  Serial.print(",");
  Serial.print(motorOn ? "ON" : "OFF");
  Serial.print(",");
  Serial.println(motorLevel);
}
