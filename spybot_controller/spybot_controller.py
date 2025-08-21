import cv2
import mediapipe as mp
import socket
import time

ESP32_IP = '192.168.4.1'
PORT = 1511

def send_command(cmd):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ESP32_IP, PORT))
        sock.send(cmd.encode())
        sock.close()
        print(f"[INFO] Dikirim: '{cmd}'")
    except Exception as e:
        print(f"[ERROR] Gagal mengirim ke ESP32: {e}")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]
    fingers = []
    
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)
        
    for tip in finger_tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return fingers

cap = cv2.VideoCapture(0)
prev_command = None
last_sent_time = 0

print("Hand gesture is running, press Q to quit.")

if not cap.isOpened():
    print("Cannot access the camera!")
    exit()

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Cannot catch the frame!")
        break
    
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            fingers = count_fingers(hand_landmarks)
            total_fingers = sum(fingers)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            command = None
            
            if fingers == [1, 1, 1, 1, 1]:
                command = 'f'
                cv2.putText(frame, "FORWARD", (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            elif fingers == [0, 1, 0, 0, 0]:
                command = 'r'
                cv2.putText(frame, "TURN RIGHT", (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            elif fingers == [0, 1, 1, 0, 0]:
                command = 'l'
                cv2.putText(frame, "TURN LEFT", (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            elif fingers == [1, 0, 0, 0, 0]:
                command = 'b'
                cv2.putText(frame, "BACKWARD", (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            elif fingers == [0, 0, 0, 0, 0]:
                command = 's'
                cv2.putText(frame, "STOP", (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
            now = time.time()
            if command and (command != prev_command or now - last_sent_time > 1):
                send_command(command)
                prev_command = command
                last_sent_time = now
    
    cv2.imshow("SPYBOT CONTROLLER", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
    
    