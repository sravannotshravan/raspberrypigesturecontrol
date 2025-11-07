#!/usr/bin/env python3
"""
Gesture Control Client - Arduino USB Serial Version
Runs on laptop with webcam and connects to Arduino via USB Serial

This program:
1. Detects hand gestures using laptop's webcam
2. Sends control commands to Arduino via USB serial
3. Receives status updates from Arduino
4. Displays visual feedback on screen
"""

import cv2
import mediapipe as mp
import math
import time
import serial
import serial.tools.list_ports
import threading

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id):
        tip = landmarks[finger_tip_id]
        pip = landmarks[finger_pip_id]
        
        if finger_tip_id == 4:
            return tip.x < landmarks[3].x if landmarks[0].x < landmarks[9].x else tip.x > landmarks[3].x
        
        return tip.y < pip.y
    
    def count_extended_fingers(self, landmarks):
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        extended = []
        for tip_id, pip_id in zip(finger_tips, finger_pips):
            if self.is_finger_extended(landmarks, tip_id, pip_id):
                extended.append(tip_id)
        
        return len(extended), extended
    
    def detect_gesture(self, landmarks):
        count, extended_fingers = self.count_extended_fingers(landmarks)
        
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        wrist = landmarks[0]
        palm_center = landmarks[9]
        
        thumb_extended = 4 in extended_fingers
        
        # Thumbs Up
        if thumb_extended and count == 1:
            if thumb_tip.y < wrist.y and thumb_tip.y < thumb_ip.y - 0.05:
                other_fingers_closed = all([
                    landmarks[8].y > landmarks[6].y,
                    landmarks[12].y > landmarks[10].y,
                    landmarks[16].y > landmarks[14].y,
                    landmarks[20].y > landmarks[18].y
                ])
                if other_fingers_closed:
                    return "THUMBS_UP"
        
        # Thumbs Down
        if thumb_extended and count == 1:
            if thumb_tip.y > palm_center.y + 0.05:
                other_fingers_closed = all([
                    landmarks[8].y > landmarks[6].y,
                    landmarks[12].y > landmarks[10].y,
                    landmarks[16].y > landmarks[14].y,
                    landmarks[20].y > landmarks[18].y
                ])
                if other_fingers_closed:
                    return "THUMBS_DOWN"
        
        # Number 1
        if 8 in extended_fingers and count == 1 and not thumb_extended:
            return "ONE"
        
        # Number 2
        if 8 in extended_fingers and 12 in extended_fingers and count == 2:
            distance = self.calculate_distance(index_tip, middle_tip)
            if distance > 0.05:
                return "TWO"
        
        # Open Hand
        if count >= 4 and thumb_extended:
            return "OPEN"
        
        # Closed Fist
        if count == 0:
            avg_distance = sum([
                self.calculate_distance(palm_center, landmarks[tip])
                for tip in [4, 8, 12, 16, 20]
            ]) / 5
            
            if avg_distance < 0.12:
                return "CLOSED"
        
        return "UNKNOWN"
    
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture = None
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
            
            gesture = self.detect_gesture(hand_landmarks.landmark)
            
            h, w, _ = frame.shape
            cv2.putText(frame, gesture, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        return frame, gesture
    
    def close(self):
        self.hands.close()


class ArduinoController:
    def __init__(self, port=None, baudrate=115200):
        self.serial_conn = None
        self.port = port
        self.baudrate = baudrate
        self.mode = "LED"
        self.led_on = False
        self.led_level = 3
        self.motor_on = False
        self.motor_level = 3
        self.connected = False
        self.status_thread = None
        self.running = False
        
    def find_arduino(self):
        """Auto-detect Arduino port"""
        ports = serial.tools.list_ports.comports()
        
        print("\nAvailable serial ports:")
        for i, port in enumerate(ports):
            print(f"  {i+1}. {port.device} - {port.description}")
        
        # Look for Arduino
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                print(f"\n✓ Found Arduino at: {port.device}")
                return port.device
        
        return None
    
    def connect(self):
        """Connect to Arduino"""
        try:
            if self.port is None:
                self.port = self.find_arduino()
                
                if self.port is None:
                    print("\n✗ No Arduino found automatically")
                    self.port = input("Enter COM port manually (e.g., COM3): ").strip()
            
            print(f"\nConnecting to Arduino on {self.port}...")
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            
            # Wait for ready message
            start_time = time.time()
            while time.time() - start_time < 5:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    print(f"Arduino: {line}")
                    if line.startswith("READY:"):
                        self.connected = True
                        print("✓ Connected to Arduino successfully!")
                        
                        # Start status monitoring thread
                        self.running = True
                        self.status_thread = threading.Thread(target=self._monitor_responses, daemon=True)
                        self.status_thread.start()
                        
                        return True
            
            print("✗ Arduino did not respond")
            return False
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def _monitor_responses(self):
        """Monitor responses from Arduino"""
        buffer = ""
        while self.running and self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8')
                    buffer += data
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self._process_response(line)
                
                time.sleep(0.01)
            except:
                break
    
    def _process_response(self, line):
        """Process response from Arduino"""
        if line.startswith("STATUS:"):
            # Parse: STATUS:mode,led_state,led_level,motor_state,motor_level
            parts = line[7:].split(',')
            if len(parts) == 5:
                self.mode = parts[0]
                self.led_on = parts[1] == "ON"
                self.led_level = int(parts[2])
                self.motor_on = parts[3] == "ON"
                self.motor_level = int(parts[4])
        elif line.startswith("MODE:"):
            self.mode = line[5:]
        elif line.startswith("LED:"):
            if "ON" in line:
                self.led_on = True
            elif "OFF" in line:
                self.led_on = False
            elif "LEVEL:" in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    self.led_level = int(parts[2])
        elif line.startswith("MOTOR:"):
            if "ON" in line:
                self.motor_on = True
            elif "OFF" in line:
                self.motor_on = False
            elif "LEVEL:" in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    self.motor_level = int(parts[2])
    
    def send_command(self, command):
        """Send command to Arduino"""
        if self.connected and self.serial_conn:
            try:
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                self.serial_conn.flush()
                return True
            except:
                return False
        return False
    
    def set_mode(self, mode):
        """Switch control mode"""
        self.send_command(f"MODE:{mode}")
    
    def turn_on(self):
        """Turn on current device"""
        if self.mode == "LED":
            self.send_command("LED:ON")
        else:
            self.send_command("MOTOR:ON")
    
    def turn_off(self):
        """Turn off current device"""
        if self.mode == "LED":
            self.send_command("LED:OFF")
        else:
            self.send_command("MOTOR:OFF")
    
    def increase(self):
        """Increase brightness/speed"""
        if self.mode == "LED":
            self.send_command("LED:UP")
        else:
            self.send_command("MOTOR:UP")
    
    def decrease(self):
        """Decrease brightness/speed"""
        if self.mode == "LED":
            self.send_command("LED:DOWN")
        else:
            self.send_command("MOTOR:DOWN")
    
    def disconnect(self):
        """Disconnect from Arduino"""
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        print("\n✓ Disconnected from Arduino")


def main():
    print("=" * 60)
    print("GESTURE CONTROL CLIENT - ARDUINO USB")
    print("=" * 60)
    print("\nControls:")
    print("  1 finger (☝)  : Switch to LED control mode")
    print("  2 fingers (✌)  : Switch to Motor control mode")
    print("  Open hand (✋) : Turn ON current device")
    print("  Closed hand (✊): Turn OFF current device")
    print("  Thumbs up (👍) for 2s : Increase brightness/speed")
    print("  Thumbs down (👎) for 2s: Decrease brightness/speed")
    print("\nPress 'q' to quit\n")
    print("=" * 60)
    
    # Initialize Arduino connection
    arduino = ArduinoController()
    if not arduino.connect():
        print("\nFailed to connect to Arduino. Please check:")
        print("  1. Arduino is connected via USB")
        print("  2. Correct drivers are installed")
        print("  3. Arduino code is uploaded")
        return
    
    # Initialize gesture detector
    detector = HandGestureDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        arduino.disconnect()
        return
    
    print("\n✓ Camera opened successfully")
    print("✓ System ready!\n")
    
    # Gesture timing
    last_gesture = None
    gesture_start_time = None
    HOLD_DURATION = 2.0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Process gesture
            processed_frame, gesture = detector.process_frame(frame)
            
            # Display status
            mode_color = (0, 255, 255) if arduino.mode == "LED" else (255, 128, 0)
            cv2.putText(processed_frame, f"MODE: {arduino.mode}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
            
            # Device status
            if arduino.mode == "LED":
                status = f"LED: {'ON' if arduino.led_on else 'OFF'} ({arduino.led_level}/5)"
            else:
                status = f"MOTOR: {'ON' if arduino.motor_on else 'OFF'} ({arduino.motor_level}/5)"
            
            cv2.putText(processed_frame, status, (10, processed_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Handle gestures
            if gesture:
                # Mode switching
                if gesture == "ONE":
                    if arduino.mode != "LED":
                        arduino.set_mode("LED")
                        print("\n📍 Switched to LED control mode")
                
                elif gesture == "TWO":
                    if arduino.mode != "MOTOR":
                        arduino.set_mode("MOTOR")
                        print("\n📍 Switched to MOTOR control mode")
                
                # On/Off
                elif gesture == "OPEN":
                    arduino.turn_on()
                
                elif gesture == "CLOSED":
                    arduino.turn_off()
                
                # Thumbs up/down with hold
                elif gesture in ["THUMBS_UP", "THUMBS_DOWN"]:
                    if gesture != last_gesture:
                        last_gesture = gesture
                        gesture_start_time = time.time()
                        cv2.putText(processed_frame, "Hold for 2 seconds...", 
                                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 255, 255), 2)
                    else:
                        elapsed = time.time() - gesture_start_time
                        remaining = HOLD_DURATION - elapsed
                        
                        if elapsed >= HOLD_DURATION:
                            if gesture == "THUMBS_UP":
                                arduino.increase()
                            else:
                                arduino.decrease()
                            gesture_start_time = time.time()
                        else:
                            cv2.putText(processed_frame, 
                                       f"Hold: {remaining:.1f}s", 
                                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                       0.7, (0, 255, 255), 2)
                else:
                    last_gesture = None
                    gesture_start_time = None
            else:
                last_gesture = None
                gesture_start_time = None
            
            # Display
            cv2.imshow('Gesture Control - Arduino USB', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        arduino.disconnect()
        print("\n✓ System shutdown complete")


if __name__ == "__main__":
    main()
