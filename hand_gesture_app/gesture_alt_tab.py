import cv2
import mediapipe as mp
import time
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# === 設定參數 ===
MODEL_PATH = 'gesture_recognizer.task'
COOLDOWN_TIME = 0.5  # 手勢冷卻時間 (秒) - 避免重複觸發
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
            print("Action: Open Alt+Tab")
            pyautogui.keyDown('alt')
            pyautogui.press('tab')
            is_alt_tab_active = True
        else:
            print("Action: Release Alt (Select Window)")
            pyautogui.keyUp('alt')
            is_alt_tab_active = False
        last_action_time = current_time

    elif is_alt_tab_active: # 只有在 Alt+Tab 開啟時才偵測左右切換
        if gesture_name == GESTURE_THUMB_UP:
            print("Action: Right Arrow")
            pyautogui.press('right')
            last_action_time = current_time # 稍微更新冷卻，避免滑太快
        
        elif gesture_name == GESTURE_THUMB_DOWN:
            print("Action: Left Arrow")
            pyautogui.press('left')
            last_action_time = current_time

def main():
    global recognition_result
    
    # 初始化 MediaPipe
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1, # 控制單手即可
        min_hand_detection_confidence=CONFIDENCE_THRESHOLD,
        min_hand_presence_confidence=CONFIDENCE_THRESHOLD,
        min_tracking_confidence=CONFIDENCE_THRESHOLD,
        result_callback=save_result
    )

    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        
        print(f"啟動中... 請使用環境: mp_env")
        print("操作說明:")
        print(f"1. {GESTURE_VICTORY}: 開啟/關閉 Alt+Tab 選單")
        print(f"2. {GESTURE_THUMB_UP}: 向右選擇 (需先開啟 Alt+Tab)")
        print(f"3. {GESTURE_THUMB_DOWN}: 向左選擇 (需先開啟 Alt+Tab)")
        print("按 ESC 離開")

        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            # 翻轉畫面 (鏡像)
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            timestamp = time.time_ns() // 1_000_000
            recognizer.recognize_async(mp_image, timestamp)

            current_gesture_name = "None"

            if recognition_result:
                # 繪製手部特徵點
                if recognition_result.hand_landmarks:
                    draw_landmarks_on_frame(frame, recognition_result.hand_landmarks)
                
                # 取得手勢名稱
                if recognition_result.gestures:
                    # 取出信心度最高的手勢
                    gesture = recognition_result.gestures[0][0]
                    current_gesture_name = gesture.category_name
                    score = round(gesture.score, 2)
                    
                    # 顯示當前手勢
                    color = (0, 255, 0) if is_alt_tab_active else (255, 255, 0)
                    cv2.putText(frame, f"Gesture: {current_gesture_name} ({score})", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
                    # 執行邏輯
                    handle_gestures(current_gesture_name)

            # 顯示狀態
            status_text = "Status: Alt+Tab ACTIVE" if is_alt_tab_active else "Status: Idle"
            cv2.putText(frame, status_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow('Gesture Controller', frame)
            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()
        
        # 確保程式結束時釋放 Alt 鍵 (避免卡住)
        if is_alt_tab_active:
            pyautogui.keyUp('alt')

if __name__ == "__main__":
    main()