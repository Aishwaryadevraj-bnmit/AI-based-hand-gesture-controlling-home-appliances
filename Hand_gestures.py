import cv2
import mediapipe as mp
import serial
import time
import speech_recognition as sr
import pyttsx3
import threading

# ===== Serial Communication Setup =====
arduino = serial.Serial('COM4', 9600, timeout=1)  # Change COM port as needed
time.sleep(2)  # Allow Arduino to initialize

# ===== Text-to-Speech Engine =====
engine = pyttsx3.init()

def _speak(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    threading.Thread(target=_speak, args=(text,), daemon=True).start()

# ===== Speech Recognition Setup =====
recognizer = sr.Recognizer()

def listen_command():
    try:
        with sr.Microphone() as source:
            speak("Please say the command.")
            print("Listening for command...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            command = recognizer.recognize_google(audio).lower()
            print("You said:", command)
            process_voice_command(command)
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand.")
    except sr.RequestError:
        speak("Network error.")
    except sr.WaitTimeoutError:
        speak("Listening timed out.")

def process_voice_command(command):
    if "one" in command:
        arduino.write(b'1\n')
        speak("Bulb one is on")
    elif "two" in command:
        arduino.write(b'2\n')
        speak("Bulb two is on")
    elif "both" in command or "all" in command:
        arduino.write(b'5\n')
        speak("Both bulbs are on")
    elif "off" in command:
        arduino.write(b'0\n')
        speak("All bulbs are off")
    else:
        speak("Command not recognized")

# ===== MediaPipe Hand Setup =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
finger_tips = [4, 8, 12, 16, 20]

# ===== OpenCV Camera Setup =====
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_sent = None
last_finger_count = None
last_time = 0
cooldown = 2  # seconds

def count_fingers(hand):
    fingers = []
    fingers.append(1 if hand.landmark[finger_tips[0]].x < hand.landmark[finger_tips[0] - 1].x else 0)
    for tip in finger_tips[1:]:
        fingers.append(1 if hand.landmark[tip].y < hand.landmark[tip - 2].y else 0)
    return sum(fingers)

# ===== Main Loop =====
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_count = -1
    hand_detected = False

    if result.multi_hand_landmarks:
        hand_detected = True
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_count = count_fingers(hand_landmarks)

    current_time = time.time()

    if not hand_detected:
        if current_time - last_time > cooldown:
            speak("No hand detected")
            last_time = current_time
        cv2.putText(frame, "No hand detected", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    else:
        if finger_count != -1 and finger_count != last_finger_count:
            if current_time - last_time > cooldown:
                if finger_count in [1, 2, 5]:
                    arduino.write(f"{finger_count}\n".encode())
                    if finger_count == 1:
                        speak("Bulb one is on")
                    elif finger_count == 2:
                        speak("Bulb two is on")
                    elif finger_count == 5:
                        speak("Both bulbs are on")
                    last_sent = finger_count
                elif finger_count in [0, 3, 4]:
                    if last_sent != 0:
                        arduino.write(b'0\n')
                        speak("All bulbs are off")
                        last_sent = 0
                last_finger_count = finger_count
                last_time = current_time

        if finger_count != -1:
            cv2.putText(frame, f"{finger_count}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)

    cv2.imshow("Gesture & Voice Control", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('v'):
        threading.Thread(target=listen_command, daemon=True).start()
    elif key == 27:  # ESC key
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
