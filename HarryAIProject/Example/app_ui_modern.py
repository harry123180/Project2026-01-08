import customtkinter as ctk
import cv2
from PIL import Image, ImageOps
import numpy as np
import os
import threading
import time
from datetime import datetime

# 設定主題
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# 嘗試匯入 tf_keras
try:
    from tf_keras.models import load_model
except ImportError:
    try:
        from tensorflow.keras.models import load_model
    except:
        print("請確認已安裝 tensorflow 或 tf-keras")
        exit()

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 視窗基礎設定 ---
        self.title("Gemini AI Vision Pro")
        self.geometry("1200x720")
        
        # 載入模型相關變數
        self.model = None
        self.class_names = []
        self.is_auto_predict = False
        self.last_predict_time = 0
        self.confidence_threshold = 0.7

        # --- 介面佈局 ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================
        # 1. 左側側邊欄
        # =============================
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AI VISION", 
                                       font=ctk.CTkFont(size=24, weight="bold", family="Impact"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="v2.0 Dashboard", 
                                          text_color="gray", font=ctk.CTkFont(size=12))
        self.version_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.auto_switch_var = ctk.BooleanVar(value=False)
        self.auto_switch = ctk.CTkSwitch(self.sidebar_frame, text="即時自動偵測",
                                         command=self.toggle_auto_predict,
                                         variable=self.auto_switch_var,
                                         progress_color="#00E676")
        self.auto_switch.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.slider_label = ctk.CTkLabel(self.sidebar_frame, text="信心門檻: 70%", anchor="w")
        self.slider_label.grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.threshold_slider = ctk.CTkSlider(self.sidebar_frame, from_=0, to=1, number_of_steps=100,
                                              command=self.update_threshold_label)
        self.threshold_slider.set(0.7)
        self.threshold_slider.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.predict_btn = ctk.CTkButton(self.sidebar_frame, text="手動掃描 (SCAN)",
                                         height=50,
                                         fg_color="#2962FF", hover_color="#0039CB",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         command=self.predict_frame)
        self.predict_btn.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="系統狀態: 初始化...", 
                                         text_color="orange", anchor="w")
        self.status_label.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")

        # =============================
        # 2. 右側主內容區
        # =============================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.camera_container = ctk.CTkFrame(self.main_frame, fg_color="#1A1A1A", corner_radius=15)
        self.camera_container.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        self.camera_label = ctk.CTkLabel(self.camera_container, text="", corner_radius=15)
        self.camera_label.place(relx=0.5, rely=0.5, anchor="center")

        # 修正: 使用 Hex Color 而非 rgba
        self.fps_label = ctk.CTkLabel(self.camera_container, text="FPS: 0", 
                                      fg_color="#333333", corner_radius=5, width=60)
        self.fps_label.place(x=20, y=20)

        self.dashboard_frame = ctk.CTkFrame(self.main_frame, height=200, fg_color="#2B2B2B", corner_radius=15)
        self.dashboard_frame.grid(row=1, column=0, sticky="ew")
        self.dashboard_frame.grid_columnconfigure(1, weight=1)

        self.result_panel = ctk.CTkFrame(self.dashboard_frame, width=300, fg_color="transparent")
        self.result_panel.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        
        self.result_title = ctk.CTkLabel(self.result_panel, text="DETECTED OBJECT", 
                                         font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.result_title.pack(anchor="w")

        self.class_label = ctk.CTkLabel(self.result_panel, text="WAITING...", 
                                        font=ctk.CTkFont(size=36, weight="bold"), text_color="#00E676")
        self.class_label.pack(anchor="w", pady=(5, 0))

        self.conf_label = ctk.CTkLabel(self.result_panel, text="Confidence: 0%", anchor="w")
        self.conf_label.pack(anchor="w", pady=(15, 5))
        
        self.conf_bar = ctk.CTkProgressBar(self.result_panel, width=250, height=15)
        self.conf_bar.set(0)
        self.conf_bar.pack(anchor="w")

        self.log_box = ctk.CTkTextbox(self.dashboard_frame, font=("Consolas", 12), text_color="#00FF00", fg_color="black")
        self.log_box.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.log_message("System initialized.")
        self.log_message("Waiting for camera source...")

        # 啟動攝影機
        self.cap = cv2.VideoCapture(0)
        self.prev_time = time.time()
        self.update_camera()
        
        # 修正: 直接在主線程載入模型 (避免 Tkinter 線程安全問題)
        # 雖然會稍微卡頓一下，但保證安全
        self.after(100, self.load_ai_model) 

    def load_ai_model(self):
        """載入 AI 模型"""
        try:
            self.status_label.configure(text="狀態: 載入模型中...", text_color="yellow")
            self.update_idletasks() # 強制刷新 UI 顯示載入中
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, "..")
            model_path = os.path.join(project_root, "keras_model.h5")
            labels_path = os.path.join(project_root, "labels.txt")

            print(f"Loading model from: {model_path}")
            self.model = load_model(model_path, compile=False)
            
            with open(labels_path, "r", encoding="utf-8") as f:
                self.class_names = f.readlines()
            
            self.status_label.configure(text="狀態: 系統就緒", text_color="#00E676")
            self.log_message(f"Model loaded: {os.path.basename(model_path)}")
            self.log_message(f"Classes found: {len(self.class_names)}")
            
        except Exception as e:
            self.status_label.configure(text="狀態: 模型錯誤", text_color="red")
            self.log_message(f"Error: {e}")
            print(e)

    def update_threshold_label(self, value):
        self.confidence_threshold = value
        self.slider_label.configure(text=f"信心門檻: {int(value*100)}%")

    def toggle_auto_predict(self):
        self.is_auto_predict = self.auto_switch_var.get()
        if self.is_auto_predict:
            self.log_message("Auto-detection mode: ON")
            self.predict_btn.configure(state="disabled", fg_color="gray")
        else:
            self.log_message("Auto-detection mode: OFF")
            self.predict_btn.configure(state="normal", fg_color="#2962FF")

    def log_message(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            # 計算 FPS
            curr_time = time.time()
            fps = 1 / (curr_time - self.prev_time) if (curr_time - self.prev_time) > 0 else 0
            self.prev_time = curr_time
            self.fps_label.configure(text=f"FPS: {int(fps)}")

            # 轉 RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_pil_image = Image.fromarray(image)

            # 縮放顯示
            container_w = self.camera_container.winfo_width()
            container_h = self.camera_container.winfo_height()
            
            if container_w > 50 and container_h > 50:
                img_ratio = image.shape[1] / image.shape[0]
                container_ratio = container_w / container_h
                
                if img_ratio > container_ratio:
                    new_w = container_w
                    new_h = int(new_w / img_ratio)
                else:
                    new_h = container_h
                    new_w = int(new_h * img_ratio)
                
                pil_resized = self.current_pil_image.resize((new_w, new_h), Image.Resampling.BILINEAR)
                ctk_img = ctk.CTkImage(light_image=pil_resized, size=(new_w, new_h))
                self.camera_label.configure(image=ctk_img)

            if self.is_auto_predict and (curr_time - self.last_predict_time > 0.5):
                self.predict_frame()
                self.last_predict_time = curr_time
        
        self.after(10, self.update_camera)

    def predict_frame(self):
        if self.model is None or not hasattr(self, 'current_pil_image'):
            return
        
        # 這裡推論使用線程是安全的，因為我們會在回調中使用 after 更新 UI
        threading.Thread(target=self._run_inference).start()

    def _run_inference(self):
        try:
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            image = ImageOps.fit(self.current_pil_image, (224, 224), Image.Resampling.LANCZOS)
            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
            data[0] = normalized_image_array

            prediction = self.model.predict(data, verbose=0)
            index = np.argmax(prediction)
            raw_class_name = self.class_names[index].strip()
            confidence = prediction[0][index]
            display_name = raw_class_name[2:] if len(raw_class_name) > 2 else raw_class_name

            # 關鍵修正: 在主線程更新 UI
            self.after(0, lambda: self._update_results(display_name, confidence))

        except Exception as e:
            print(f"Inference error: {e}")

    def _update_results(self, name, confidence):
        if confidence < self.confidence_threshold:
            color = "#FF3D00"
            status_text = f"Low Confidence ({name})"
        else:
            color = "#00E676"
            status_text = name
            if not self.is_auto_predict:
                 self.log_message(f"Detected: {name} ({confidence:.2%})")
            
        self.class_label.configure(text=status_text, text_color=color)
        self.conf_label.configure(text=f"Confidence: {confidence:.2%}")
        self.conf_bar.set(confidence)
        self.conf_bar.configure(progress_color=color)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = ModernApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()