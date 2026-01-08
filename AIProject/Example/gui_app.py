import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import numpy as np
import threading
import os
import time
import warnings
from tf_keras.models import load_model

# Environment setup to suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
warnings.filterwarnings("ignore")

# Configuration
MODEL_PATH = r"D:\AWORKSPACE\Github\Project2026-01-08\HarryAIProject\keras_model.h5"
LABELS_PATH = r"D:\AWORKSPACE\Github\Project2026-01-08\HarryAIProject\labels.txt"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
CAMERA_INDEX = 0

class AIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("AI Visual Classifier - Gemini Powered")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        
        # Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables
        self.cap = None
        self.is_running = False
        self.model = None
        self.class_names = []
        self.current_frame = None

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AI Vision", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        self.start_button = ctk.CTkButton(self.sidebar_frame, text="Start Camera", command=self.start_camera)
        self.start_button.grid(row=2, column=0, padx=20, pady=10)

        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="Stop Camera", command=self.stop_camera, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.stop_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.load_info_label = ctk.CTkLabel(self.sidebar_frame, text="Model Not Loaded", text_color="red", wraplength=180)
        self.load_info_label.grid(row=5, column=0, padx=20, pady=20)

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1) # Video area
        self.main_frame.grid_rowconfigure(1, weight=0) # Info area

        # Video Display
        self.video_label = ctk.CTkLabel(self.main_frame, text="", corner_radius=10)
        self.video_label.grid(row=0, column=0, padx=10, pady=10)

        # Result Display Area
        self.result_frame = ctk.CTkFrame(self.main_frame, height=150, fg_color="transparent")
        self.result_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.prediction_label = ctk.CTkLabel(self.result_frame, text="Waiting for Input...", font=ctk.CTkFont(size=32, weight="bold"))
        self.prediction_label.pack(pady=5)

        self.confidence_bar = ctk.CTkProgressBar(self.result_frame, orientation="horizontal")
        self.confidence_bar.pack(pady=10, fill="x", padx=50)
        self.confidence_bar.set(0)

        self.confidence_text = ctk.CTkLabel(self.result_frame, text="0.00%", font=ctk.CTkFont(size=16))
        self.confidence_text.pack(pady=0)

        # Initialize Model
        self.init_model()

    def init_model(self):
        try:
            self.status_label.configure(text="Status: Loading Model...")
            self.update() # Force update UI
            
            # Path Logic (Same as tm.py)
            model_path = MODEL_PATH
            labels_path = LABELS_PATH

            if not os.path.exists(model_path):
                # Fallback to local directory
                local_model = os.path.join(os.path.dirname(__file__), "keras_model.h5")
                if os.path.exists(local_model):
                    model_path = local_model
                    labels_path = os.path.join(os.path.dirname(__file__), "labels.txt")
                else:
                    raise FileNotFoundError(f"Model not found at {model_path} or {local_model}")

            if not os.path.exists(labels_path):
                 raise FileNotFoundError(f"Labels not found at {labels_path}")
            
            self.model = load_model(model_path, compile=False)
            
            with open(labels_path, "r", encoding="utf-8") as f:
                self.class_names = [line.strip() for line in f.readlines()]
                
            self.load_info_label.configure(text="Model Loaded Successfully", text_color="green")
            self.status_label.configure(text="Status: Ready")
        except Exception as e:
            self.load_info_label.configure(text=f"Error: {str(e)}", text_color="red")
            self.status_label.configure(text="Status: Error")
            print(f"Model Load Error: {e}")

    def start_camera(self):
        if not self.is_running:
            try:
                self.cap = cv2.VideoCapture(CAMERA_INDEX)
                if not self.cap.isOpened():
                     raise Exception("Could not open video device")
                self.is_running = True
                self.status_label.configure(text="Status: Running", text_color="green")
                self.update_video()
            except Exception as e:
                self.status_label.configure(text=f"Camera Error", text_color="red")
                print(f"Camera Error: {e}")

    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.video_label.configure(image=None)
        self.status_label.configure(text="Status: Stopped", text_color="gray")

    def update_video(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # 1. Process for Display (BGR -> RGB -> ImageTk)
                # Resize specifically for the GUI display (e.g., 640x480 or fit)
                display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = display_frame.shape
                # Simple aspect ratio scaling if needed, or fixed size
                # Let's keep it simple: scale to fit available space if possible, or fixed
                display_image = Image.fromarray(display_frame)
                
                # Resize for UI smoothness
                display_image = display_image.resize((640, 480)) 
                ctk_img = ctk.CTkImage(light_image=display_image, dark_image=display_image, size=(640, 480))
                
                self.video_label.configure(image=ctk_img, text="")
                self.video_label.image = ctk_img # Keep reference

                # 2. Process for Model (Resize -> Normalize -> Predict)
                self.process_inference(display_image)

            # Schedule next update
            self.after(30, self.update_video)

    def process_inference(self, pil_image):
        if self.model and self.class_names:
            try:
                # Prepare image for model (224x224)
                # Resize/Crop logic similar to tm.py
                size = (224, 224)
                image = pil_image.copy() # Use the PIL image we already have
                image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
                image_array = np.asarray(image)
                normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
                
                data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
                data[0] = normalized_image_array

                # Predict
                prediction = self.model.predict(data, verbose=0)
                index = np.argmax(prediction)
                class_name = self.class_names[index]
                confidence_score = prediction[0][index]

                # Update UI
                display_name = class_name.split(" ", 1)[1] if " " in class_name else class_name
                self.prediction_label.configure(text=display_name)
                
                # Update Bar color based on confidence
                if confidence_score > 0.8:
                    self.confidence_bar.configure(progress_color="#2CC985") # Green
                elif confidence_score > 0.5:
                    self.confidence_bar.configure(progress_color="#F2C94C") # Yellow
                else:
                    self.confidence_bar.configure(progress_color="#EB5757") # Red

                self.confidence_bar.set(confidence_score)
                self.confidence_text.configure(text=f"{confidence_score*100:.2f}%")

            except Exception as e:
                print(f"Inference Error: {e}")

from PIL import ImageOps # Added missing import

if __name__ == "__main__":
    app = AIApp()
    app.mainloop()
