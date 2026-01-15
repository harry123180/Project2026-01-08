import customtkinter as ctk
import cv2
from PIL import Image, ImageOps
import numpy as np
import os
import threading

# 嘗試匯入 tf_keras，如果失敗則提示使用者
try:
    from tf_keras.models import load_model
except ImportError:
    print("請先安裝 tf-keras: pip install tf-keras")
    exit()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 視窗設定 ---
        self.title("AI Object Recognition App")
        self.geometry("1000x600")
        
        # 設定顏色主題 (可以自定義顏色，這裡直接使用元件的顏色參數)
        ctk.set_appearance_mode("Light") # 根據圖片背景看起來是白色的
        ctk.set_default_color_theme("blue")

        # --- 載入模型 (背景執行以免卡住介面) ---
        self.model = None
        self.class_names = []
        self.load_model_thread = threading.Thread(target=self.load_ai_model)
        self.load_model_thread.start()

        # --- 介面佈局 ---
        # 配置 Grid (2列 x 2欄)
        self.grid_columnconfigure(0, weight=1) # 左欄 (畫布)
        self.grid_columnconfigure(1, weight=1) # 右欄 (結果與按鈕)
        self.grid_rowconfigure(0, weight=0)    # 標題列 (固定高度)
        self.grid_rowconfigure(1, weight=1)    # 內容區

        # 1. UI 標題 (藍色區塊)
        # 對應圖片上方的藍色長條
        self.header_frame = ctk.CTkFrame(self, fg_color="#4472C4", corner_radius=20)
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        
        self.header_label = ctk.CTkLabel(self.header_frame, text="UI 標題", font=("Microsoft JhengHei UI", 32, "bold"), text_color="white")
        self.header_label.pack(pady=30)

        # 2. 畫面 Canva(畫布) (綠色區塊)
        # 對應圖片左側的綠色方形
        # 使用 CTkLabel 來顯示影像，預設給一個綠色背景
        self.camera_frame = ctk.CTkLabel(self, text="畫面\nCanva(畫布)", 
                                         fg_color="#70AD47", 
                                         text_color="white",
                                         font=("Microsoft JhengHei UI", 24),
                                         corner_radius=0, # 圖片中看起來比較方
                                         width=450, height=400) 
        self.camera_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # 右側容器 (用來包裝 結果 與 按鈕)
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1) # 上半部
        self.right_panel.grid_rowconfigure(1, weight=1) # 下半部

        # 3. AI結果 (Label) (橘色區塊)
        # 對應圖片右上的橘色圓角矩形
        self.result_label = ctk.CTkLabel(self.right_panel, 
                                         text="AI結果\n(Label)", 
                                         fg_color="#ED7D31", 
                                         text_color="white",
                                         font=("Microsoft JhengHei UI", 28, "bold"),
                                         corner_radius=30,
                                         width=350, height=200)
        self.result_label.pack(side="top", pady=(20, 40), expand=True)

        # 4. 辨識(BTN) (灰色區塊)
        # 對應圖片右下的灰色按鈕
        self.predict_btn = ctk.CTkButton(self.right_panel, 
                                         text="辨識(BTN)", 
                                         fg_color="#A5A5A5", 
                                         hover_color="#808080",
                                         text_color="white",
                                         font=("Microsoft JhengHei UI", 24),
                                         corner_radius=15,
                                         width=200, height=60,
                                         command=self.predict_frame)
        self.predict_btn.pack(side="bottom", pady=(0, 40))

        # --- 攝影機設定 ---
        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def load_ai_model(self):
        """載入 AI 模型與標籤 (背景執行)"""
        try:
            # 取得程式所在路徑，確保能找到模型
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, "..")
            model_path = os.path.join(project_root, "keras_model.h5")
            labels_path = os.path.join(project_root, "labels.txt")

            print(f"Loading model from: {model_path}...")
            self.model = load_model(model_path, compile=False)
            
            with open(labels_path, "r", encoding="utf-8") as f:
                self.class_names = f.readlines()
            
            print("Model loaded successfully!")
            # 更新 UI 狀態 (非必要，但可以提示使用者)
            self.result_label.configure(text="AI 準備就緒")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.result_label.configure(text="模型載入失敗")

    def update_camera(self):
        """讀取攝影機畫面並更新到 UI"""
        ret, frame = self.cap.read()
        if ret:
            # 格式轉換: BGR (OpenCV) -> RGB (Pillow)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            
            # 調整大小以適應 UI (保持比例或填滿)
            # 這裡我們讓它填滿綠色區塊的大小 (450x400)
            img_w, img_h = self.camera_frame.winfo_width(), self.camera_frame.winfo_height()
            if img_w > 1 and img_h > 1: # 避免視窗還沒初始化時長寬為1
                image = ImageOps.fit(image, (img_w, img_h), Image.Resampling.LANCZOS)
            
            # 轉為 CTkImage
            ctk_img = ctk.CTkImage(light_image=image, size=(img_w, img_h))
            
            # 更新 Label
            self.camera_frame.configure(image=ctk_img, text="") # 清除文字，顯示圖片
            self.current_pil_image = image # 保存當前圖片供辨識使用
        
        # 每 10 毫秒呼叫一次自己
        self.after(10, self.update_camera)

    def predict_frame(self):
        """按下按鈕時進行辨識"""
        if self.model is None:
            self.result_label.configure(text="模型載入中...")
            return
            
        if not hasattr(self, 'current_pil_image'):
            return

        try:
            # 準備圖片資料
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            
            # 裁切並縮放至 224x224 (模型需求)
            image = ImageOps.fit(self.current_pil_image, (224, 224), Image.Resampling.LANCZOS)
            image_array = np.asarray(image)
            
            #正規化
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
            data[0] = normalized_image_array

            # 預測
            prediction = self.model.predict(data, verbose=0)
            index = np.argmax(prediction)
            class_name = self.class_names[index].strip()
            confidence_score = prediction[0][index]

            # 更新 UI (去除標籤前面的編號 0, 1, ... 如果有的話)
            # 假設 labels.txt 格式是 "0 ClassName"
            display_name = class_name[2:] if len(class_name) > 2 else class_name
            
            result_text = f"類別: {display_name}\n信心: {confidence_score:.2%}"
            self.result_label.configure(text=result_text)
            print(f"Predicted: {class_name} ({confidence_score})")

        except Exception as e:
            print(f"Prediction error: {e}")
            self.result_label.configure(text="辨識錯誤")

    def on_closing(self):
        """關閉視窗時釋放資源"""
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
