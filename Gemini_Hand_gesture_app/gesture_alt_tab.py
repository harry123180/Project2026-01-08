import cv2
import mediapipe as mp
import time
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# === 設定參數 ===
# 確保模型檔案在這個資料夾下
MODEL_PATH = 'Gemini_Hand_gesture_app/gesture_recognizer.task'
COOLDOWN_TIME = 0.6  # 稍微增加冷卻時間，讓操作更穩定
CONFIDENCE_THRESHOLD = 0.5

# === 初始化變數 ===
last_action_time = 0
is_alt_tab_active = False # 紀錄 Alt+Tab 視窗是否開啟
recognition_result = None

# 定義手勢名稱 (根據 MediaPipe 預設模型)
GESTURE_VICTORY = "Victory"
GESTURE_THUMB_UP = "Thumb_Up"
GESTURE_THUMB_DOWN = "Thumb_Down"

# 為了繪圖定義連線
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]

def save_result(result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global recognition_result
    recognition_result = result

def draw_landmarks_on_frame(frame, hand_landmarks_list):
    h, w, _ = frame.shape
    for hand_landmarks in hand_landmarks_list:
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
        for start_idx, end_idx in HAND_CONNECTIONS:
            cv2.line(frame, points[start_idx], points[end_idx], (0, 255, 0), 2)
        for pt in points:
            cv2.circle(frame, pt, 5, (255, 0, 0), -1)

def handle_gestures(gesture_name):
    global last_action_time, is_alt_tab_active

    current_time = time.time()
    if current_time - last_action_time < COOLDOWN_TIME:
        return

    if gesture_name == GESTURE_VICTORY:
        if not is_alt_tab_active:
            print(">>> 觸發: 開啟 Alt+Tab")
            pyautogui.keyDown('alt')
            pyautogui.press('tab')
            is_alt_tab_active = True
        else:
            print(">>> 觸發: 放開 Alt (切換完成)")
            pyautogui.keyUp('alt')
            is_alt_tab_active = False
        last_action_time = current_time

    elif is_alt_tab_active: # 只有在 Alt+Tab 開啟時才偵測左右切換
        if gesture_name == GESTURE_THUMB_UP:
            print(">>> 觸發: 向右選取 (Right)")
            pyautogui.press('right')
            last_action_time = current_time
        
        elif gesture_name == GESTURE_THUMB_DOWN:
            print(">>> 觸發: 向左選取 (Left)")
            pyautogui.press('left')
            last_action_time = current_time

def main():
    global recognition_result
    
    # 初始化 MediaPipe Gesture Recognizer
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        min_hand_detection_confidence=CONFIDENCE_THRESHOLD,
        result_callback=save_result
    )

    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        
        print(f"--- 手勢辨識 Alt+Tab 控制器已啟動 ---")
        print(f"環境: mp_env")
        print(f"1. Victory (YA): 開啟/確認 Alt+Tab")
        print(f"2. Thumb Up (讚): 向右選取")
        print(f"3. Thumb Down (倒讚): 向左選取")
        print(f"按 ESC 結束程式")

        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            frame = cv2.flip(frame, 1) # 鏡像
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            timestamp = time.time_ns() // 1_000_000
            recognizer.recognize_async(mp_image, timestamp)

            if recognition_result:
                if recognition_result.hand_landmarks:
                    draw_landmarks_on_frame(frame, recognition_result.hand_landmarks)
                
                if recognition_result.gestures:
                    gesture = recognition_result.gestures[0][0]
                    category_name = gesture.category_name
                    score = round(gesture.score, 2)
                    
                    # 顯示資訊
                    color = (0, 255, 0) if is_alt_tab_active else (255, 255, 255)
                    cv2.putText(frame, f"Gesture: {category_name} ({score})", (20, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    
                    handle_gestures(category_name)

            # 狀態顯示
            status_text = "ALT+TAB: ON" if is_alt_tab_active else "ALT+TAB: OFF"
            cv2.putText(frame, status_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow('Gemini Hand Gesture App', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        
        if is_alt_tab_active:
            pyautogui.keyUp('alt')

if __name__ == "__main__":
    main()
