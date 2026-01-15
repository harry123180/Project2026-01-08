import cv2
import torch
import numpy as np
import time
import os
from datetime import datetime
import mediapipe as mp
import customtkinter as ctk
from PIL import Image, ImageTk
from torchvision import transforms
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 引用你的訓練模型架構
from training import ConvNet 

class ProAirWritingWhite(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. 視窗與主題設定 ---
        self.title("手寫辨識")
        self.geometry("1200x900")
        ctk.set_appearance_mode("light") # 切換為亮色模式
        ctk.set_default_color_theme("blue")

        # 載入權重
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ConvNet().to(self.device)
        try:
            self.model.load_state_dict(torch.load("mnist_cnn_10.pth", map_location=self.device))
            self.model.eval()
        except:
            print("請確認 mnist_cnn.pth 是否在資料夾中")

        self.canvas_data = None 
        self.prev_x, self.prev_y = 0, 0
        self.recognition_result = None
        self.current_finger_pos = None # 儲存當前指尖座標

        # --- 2. 介面配置 ---
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 左側：白底視訊區
        self.main_view = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.main_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.main_view, text="")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # 右側：數據面板
        self.side_panel = ctk.CTkFrame(self, corner_radius=15)
        self.side_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.side_panel, text="信心度分析", font=("Arial", 18, "bold")).pack(pady=20)

        self.bar_items = []
        for i in range(10):
            f = ctk.CTkFrame(self.side_panel, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=5)
            lbl = ctk.CTkLabel(f, text=f"{i}", width=20)
            lbl.pack(side="left")
            bar = ctk.CTkProgressBar(f, height=12)
            bar.pack(side="left", fill="x", expand=True, padx=10)
            bar.set(0)
            pct = ctk.CTkLabel(f, text="0%", width=35)
            pct.pack(side="right")
            self.bar_items.append({"bar": bar, "pct": pct, "lbl": lbl})

        # 下方：控制台
        self.control_panel = ctk.CTkFrame(self, height=100, corner_radius=15)
        self.control_panel.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.res_display = ctk.CTkLabel(self.control_panel, text="辨識結果：-", font=("Arial", 32, "bold"))
        self.res_display.pack(side="left", padx=40)

        ctk.CTkButton(self.control_panel, text="清除畫布 (C)", fg_color="#D35B58", command=self.clear_canvas).pack(side="right", padx=20)
        ctk.CTkButton(self.control_panel, text="儲存辨識 (P)", command=self.predict_digit).pack(side="right", padx=10)

        # --- 3. MediaPipe Tasks ---
        base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self.save_mp_result
        )
        self.recognizer = vision.GestureRecognizer.create_from_options(options)

        self.cap = cv2.VideoCapture(0)
        self.update_loop()

    def save_mp_result(self, result, output_image, timestamp_ms):
        self.recognition_result = result

    def update_loop(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            if self.canvas_data is None: self.canvas_data = np.zeros((h, w), dtype=np.uint8)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.recognizer.recognize_async(mp_image, int(time.time() * 1000))

            current_pos = None
            is_writing = False

            if self.recognition_result and self.recognition_result.hand_landmarks:
                lm = self.recognition_result.hand_landmarks[0]
                itip, mtip = lm[8], lm[12] # 食指與中指尖
                cx, cy = int(itip.x * w), int(itip.y * h)
                mx, my = int(mtip.x * w), int(mtip.y * h)
                current_pos = (cx, cy)
                
                dist = np.hypot(cx - mx, cy - my)
                if dist < 45: # 兩指併攏 = 下筆
                    is_writing = True
                    if self.prev_x != 0:
                        cv2.line(self.canvas_data, (self.prev_x, self.prev_y), (cx, cy), 255, 22)
                    self.prev_x, self.prev_y = cx, cy
                else:
                    self.prev_x, self.prev_y = 0, 0

            # --- 視覺處理：純白底色 ---
            # 建立純白背景
            white_bg = np.full(frame.shape, 255, dtype=np.uint8)
            # 將攝影機畫面變得很淡 (0.15)，背景主體為白色
            display_frame = cv2.addWeighted(frame, 0.4, white_bg, 0.6, 0)
            
            # 畫出筆跡 (深灰色)
            display_frame[self.canvas_data > 0] = [40, 40, 40]

            # --- 繪製食指追蹤點 (準心) ---
            if current_pos:
                color = (255, 0, 0) if not is_writing else (0, 0, 255) # 移動藍色，下筆紅色
                cv2.drawMarker(display_frame, current_pos, color, cv2.MARKER_CROSS, 20, 2)
                cv2.circle(display_frame, current_pos, 5, color, -1)

            img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)))
            self.video_label.configure(image=img_tk)
            self.video_label._image_cache = img_tk

        self.after(10, self.update_loop)

    def predict_digit(self):
        if self.canvas_data is None or np.sum(self.canvas_data) == 0: return
        
        # 1. 以時間戳記存檔
        if not os.path.exists("records"): os.makedirs("records")
        path = f"records/air_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        Image.fromarray(self.canvas_data).save(path)

        # 2. 預測邏輯
        transform = transforms.Compose([
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        input_tensor = transform(Image.open(path)).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)[0]
            pred = output.argmax(dim=1).item()

        # 3. 更新 UI
        self.res_display.configure(text=f"辨識結果：{pred}")
        for i, p in enumerate(probs):
            v = p.item()
            self.bar_items[i]["bar"].set(v)
            self.bar_items[i]["pct"].configure(text=f"{v*100:.1f}%")
            self.bar_items[i]["bar"].configure(progress_color="#3B8ED0" if i == pred else "gray")

    def clear_canvas(self):
        self.canvas_data.fill(0)
        self.res_display.configure(text="辨識結果：-")
        for b in self.bar_items: b["bar"].set(0); b["pct"].configure(text="0%")

    def on_closing(self):
        self.recognizer.close(); self.cap.release(); self.destroy()

if __name__ == "__main__":
    app = ProAirWritingWhite()
    app.bind("<p>", lambda e: app.predict_digit())
    app.bind("<c>", lambda e: app.clear_canvas())
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()