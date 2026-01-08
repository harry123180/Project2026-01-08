import customtkinter
import cv2
import numpy as np
from keras.models import load_model
from PIL import Image, ImageTk
import threading
import time

# --- Main Application Class ---
class AIApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Basic Setup ---
        self.title("AI辨識展演平台")
        self.geometry("1000x600") # Estimated size, can be adjusted
        customtkinter.set_appearance_mode("System")
        
        # --- Model and Camera Setup ---
        self.model = load_model(r"Joanna_20260107/converted_keras_joanna/keras_model.h5", compile=False)
        self.class_names = [line.strip() for line in open(r"Joanna_20260107/converted_keras_joanna/labels.txt", "r", encoding='utf-8').readlines()]
        
        self.camera = None
        self.running = False
        self.thread = None

        # --- Layout Configuration ---
        # Using place for fixed size and position
        # self.grid_columnconfigure(0, weight=3) # Camera feed gets more space
        # self.grid_columnconfigure(1, weight=2) # Controls/Results get less space
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)

        # --- Widgets ---
        # 1. Camera Display Area (Left)
        self.camera_view = customtkinter.CTkLabel(self, text="攝影機未開啟", fg_color="#FFC0CB", corner_radius=10, width=560, height=560)
        self.camera_view.place(x=20, y=20)

        # 2. AI Prediction Result Area (Top Right)
        self.results_frame = customtkinter.CTkFrame(self, fg_color="#FFFFE0", corner_radius=10, width=380, height=270)
        self.results_frame.place(x=600, y=20)
        self.results_frame.grid_columnconfigure((0,1), weight=1) # Keep grid for content inside the frame
        
        results_title = customtkinter.CTkLabel(self.results_frame, text="AI預測結果", font=("Arial", 20))
        results_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.prediction_labels = {}
        self.prediction_bars = {}
        for i, class_name in enumerate(self.class_names, start=1):
            label = customtkinter.CTkLabel(self.results_frame, text=f"{class_name.split(' ')[1]}: 0%", font=("Arial", 16))
            label.grid(row=i, column=0, padx=20, pady=5, sticky="w")
            self.prediction_labels[class_name] = label
            
            bar = customtkinter.CTkProgressBar(self.results_frame, progress_color="lightblue")
            bar.set(0)
            bar.grid(row=i, column=1, padx=20, pady=5, sticky="ew")
            self.prediction_bars[class_name] = bar


        # 3. Button Area (Bottom Right)
        self.button_frame = customtkinter.CTkFrame(self, fg_color="#ADD8E6", corner_radius=10, width=380, height=270)
        self.button_frame.place(x=600, y=310)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure((0,1), weight=1)
        
        self.start_button = customtkinter.CTkButton(self.button_frame, text="開啟相機", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=50, pady=20, sticky="ew")

        self.stop_button = customtkinter.CTkButton(self.button_frame, text="關閉相機", command=self.stop_camera, state="disabled")
        self.stop_button.grid(row=1, column=0, padx=50, pady=20, sticky="ew")
        
        # --- Protocol for closing window ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_camera(self):
        if not self.running:
            self.running = True
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.camera.isOpened():
                self.camera_view.configure(text="無法開啟攝影機")
                self.running = False
                return
            
            self.thread = threading.Thread(target=self.video_stream)
            self.thread.start()
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")

    def stop_camera(self):
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join() # Wait for the thread to finish
            if self.camera is not None:
                self.camera.release()
            self.camera_view.configure(image=None, text="攝影機未開啟")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            # Reset prediction bars and labels
            for class_name in self.class_names:
                self.prediction_labels[class_name].configure(text=f"{class_name.split(' ')[1]}: 0%")
                self.prediction_bars[class_name].set(0)


    def video_stream(self):
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                time.sleep(0.1)
                continue

            # --- Image Processing for Display ---
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # --- Aspect Ratio Preserving Resize ---
            view_w, view_h = 560, 560 # self.camera_view.cget("width"), self.camera_view.cget("height")
            img_w, img_h = pil_image.size
            
            # Calculate the scaling factor
            scale = min(view_w / img_w, view_h / img_h)
            
            # New image dimensions
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            
            # Resize with high-quality downsampling filter
            resized_image = pil_image.resize((new_w, new_h), Image.LANCZOS)
            
            # Create a new image with the view's background color and paste the resized image onto it
            bg_color = self.camera_view.cget("fg_color") # Directly get the color string
            background = Image.new("RGB", (view_w, view_h), bg_color)
            
            # Calculate position to paste the image so it's centered
            paste_x = (view_w - new_w) // 2
            paste_y = (view_h - new_h) // 2
            
            background.paste(resized_image, (paste_x, paste_y))

            ctk_image = ImageTk.PhotoImage(image=background)
            self.camera_view.configure(image=ctk_image, text="")
            self.camera_view.image = ctk_image # Keep a reference

            # --- Image Processing for Model ---
            model_image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
            model_image_np = np.asarray(model_image, dtype=np.float32).reshape(1, 224, 224, 3)
            normalized_image = (model_image_np / 127.5) - 1

            # --- Prediction ---
            prediction = self.model.predict(normalized_image)
            
            # --- Update UI with Predictions ---
            for i, class_name in enumerate(self.class_names):
                score = prediction[0][i]
                self.prediction_labels[class_name].configure(text=f"{class_name.split(' ')[1]}: {score:.0%}")
                self.prediction_bars[class_name].set(score)

            time.sleep(0.01) # Small delay to prevent high CPU usage

    def on_closing(self):
        self.stop_camera()
        self.destroy()

# --- Run the application ---
if __name__ == "__main__":
    app = AIApp()
    app.mainloop()
