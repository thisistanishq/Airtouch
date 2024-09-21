from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import pyautogui
import os
import time

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create the Flask application with explicit template and static folders
app = Flask(__name__, 
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Mouse control parameters
CLICK_THRESHOLD = 30
DOUBLE_TAP_THRESHOLD = 0.3
MOVE_THRESHOLD = 5
SCROLL_THRESHOLD = 30
DRAG_THRESHOLD = 20

# Get screen size
screen_width, screen_height = pyautogui.size()

# Variables for mouse control
previous_index_tip = None
previous_middle_tip = None
last_click_time = 0
is_dragging = False

def gen_frames():
    global previous_index_tip, previous_middle_tip, last_click_time, is_dragging

    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                        # Move cursor
                        cursor_x = int(index_tip.x * screen_width)
                        cursor_y = int(index_tip.y * screen_height)
                        pyautogui.moveTo(cursor_x, cursor_y)

                        # Click (when middle finger goes down)
                        if previous_middle_tip and middle_tip.y - previous_middle_tip.y > CLICK_THRESHOLD / 1000:
                            current_time = time.time()
                            if current_time - last_click_time < DOUBLE_TAP_THRESHOLD:
                                pyautogui.doubleClick()
                            else:
                                pyautogui.click()
                            last_click_time = current_time

                        # Drag functionality
                        if abs(middle_tip.y - index_tip.y) * screen_height > DRAG_THRESHOLD:
                            if not is_dragging:
                                pyautogui.mouseDown()
                                is_dragging = True
                        elif is_dragging:
                            pyautogui.mouseUp()
                            is_dragging = False

                        # Scroll functionality
                        if previous_index_tip:
                            if abs(index_tip.y - previous_index_tip.y) * screen_height > SCROLL_THRESHOLD:
                                scroll_amount = int((index_tip.y - previous_index_tip.y) * screen_height)
                                pyautogui.scroll(-scroll_amount)

                        previous_index_tip = index_tip
                        previous_middle_tip = middle_tip

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)