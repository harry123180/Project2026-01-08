import cv2
import mediapipe as mp
import time
import numpy as np
import math
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# === 設定參數 ===
MODEL_PATH = 'Gemini_Hand_gesture_app/gesture_recognizer.task'
WINDOW_NAME = 'Physics Ball Game'
BALL_RADIUS = 30
BALL_COLOR = (0, 165, 255) # 橘色 (BGR)

# 物理參數
FRICTION = 0.98       # 摩擦力 (0.0 ~ 1.0, 越小停越快)
BOUNCE_FACTOR = 0.8   # 反彈係數 (碰撞牆壁後的能量保留)
HIT_FORCE = 0.3       # 手指擊球力道係數
MAX_SPEED = 40        # 球的最大速度限制

# === 全域變數 ===
recognition_result = None

# 球的狀態
ball_pos = np.array([320.0, 240.0]) # 位置 (x, y)
ball_vel = np.array([0.0, 0.0])     # 速度 (vx, vy)

# 手指狀態 (用於計算手指速度)
prev_finger_pos = None

# 手部連線定義
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

def main():
    global recognition_result, ball_pos, ball_vel, prev_finger_pos
    
    # 初始化 MediaPipe
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=save_result
    )

    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(0)
        
        # 設定較高的解析度讓畫面更寬敞
        width = 1280
        height = 720
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        print(f"--- 物理碰撞球 App 已啟動 ---")
        print(f"用食指去 '撞' 那顆球！")
        print(f"按 ESC 離開")

        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            # 1. 翻轉與轉色
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # 2. 辨識
            timestamp = time.time_ns() // 1_000_000
            recognizer.recognize_async(mp_image, timestamp)

            # 3. 物理更新: 摩擦力
            ball_vel *= FRICTION
            
            # 速度截斷 (太小就歸零，避免微小滑動)
            if np.linalg.norm(ball_vel) < 0.1:
                ball_vel = np.array([0.0, 0.0])

            # 限制最大速度
            speed = np.linalg.norm(ball_vel)
            if speed > MAX_SPEED:
                ball_vel = (ball_vel / speed) * MAX_SPEED

            # 更新位置
            ball_pos += ball_vel

            # 4. 邊界反彈檢查
            # 左牆
            if ball_pos[0] - BALL_RADIUS < 0:
                ball_pos[0] = BALL_RADIUS
                ball_vel[0] *= -BOUNCE_FACTOR
            # 右牆
            elif ball_pos[0] + BALL_RADIUS > w:
                ball_pos[0] = w - BALL_RADIUS
                ball_vel[0] *= -BOUNCE_FACTOR
            # 上牆
            if ball_pos[1] - BALL_RADIUS < 0:
                ball_pos[1] = BALL_RADIUS
                ball_vel[1] *= -BOUNCE_FACTOR
            # 下牆
            elif ball_pos[1] + BALL_RADIUS > h:
                ball_pos[1] = h - BALL_RADIUS
                ball_vel[1] *= -BOUNCE_FACTOR


            # 5. 手指互動邏輯
            current_finger_pos = None
            
            if recognition_result and recognition_result.hand_landmarks:
                landmarks = recognition_result.hand_landmarks[0]
                
                # 繪製骨架
                for start_idx, end_idx in HAND_CONNECTIONS:
                    p1 = landmarks[start_idx]
                    p2 = landmarks[end_idx]
                    pt1 = (int(p1.x * w), int(p1.y * h))
                    pt2 = (int(p2.x * w), int(p2.y * h))
                    cv2.line(frame, pt1, pt2, (200, 200, 200), 1)

                # 取得食指指尖 (Index 8)
                idx_tip = landmarks[8]
                cx, cy = int(idx_tip.x * w), int(idx_tip.y * h)
                current_finger_pos = np.array([float(cx), float(cy)])

                # 畫出指尖
                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # 計算手指碰撞
                if prev_finger_pos is not None:
                    # 計算手指與球的距離
                    dist = np.linalg.norm(ball_pos - current_finger_pos)
                    
                    # 碰撞判定：距離 < 球半徑 + 指尖半徑(約10)
                    if dist < (BALL_RADIUS + 10):
                        # 計算手指移動向量 (速度)
                        finger_vel = current_finger_pos - prev_finger_pos
                        
                        # 簡單的動量傳遞：把手指速度加到球上
                        # 只有當手指真的在動的時候才推球，避免手指停在球裡導致球亂噴
                        if np.linalg.norm(finger_vel) > 2.0:
                            ball_vel += finger_vel * HIT_FORCE
                            
                            # 稍微把球推開一點，避免重疊黏住
                            direction = ball_pos - current_finger_pos
                            if np.linalg.norm(direction) > 0:
                                direction /= np.linalg.norm(direction)
                                ball_pos = current_finger_pos + direction * (BALL_RADIUS + 12)
                            
                            # 碰撞特效顏色
                            cv2.circle(frame, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS + 5, (255, 255, 255), 2)

                prev_finger_pos = current_finger_pos
            else:
                prev_finger_pos = None # 沒偵測到手就重置

            # 6. 繪製球
            bx, by = int(ball_pos[0]), int(ball_pos[1])
            # 陰影效果
            cv2.circle(frame, (bx+5, by+5), BALL_RADIUS, (50, 50, 50), -1)
            # 球體
            cv2.circle(frame, (bx, by), BALL_RADIUS, BALL_COLOR, -1)
            # 高光
            cv2.circle(frame, (bx-10, by-10), BALL_RADIUS//3, (255, 200, 150), -1)

            # 顯示資訊
            cv2.putText(frame, "Hit the Ball!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow(WINDOW_NAME, frame)
            
            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()