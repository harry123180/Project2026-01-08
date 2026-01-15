import sys
import cv2
import numpy as np
from pathlib import Path
from queue import Queue, Empty
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QSlider, QFrame, QScrollArea,
    QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex, QPoint, QRect
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor


class VideoLabel(QLabel):
    """可框選的影像顯示元件"""
    bbox_selected = pyqtSignal(list, np.ndarray)  # bbox, cropped_image

    def __init__(self):
        super().__init__()
        self.drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.temp_bbox = None
        self.original_size = None
        self.display_rect = QRect()
        self.current_frame = None

    def set_original_size(self, width, height):
        self.original_size = (width, height)

    def set_current_frame(self, frame):
        self.current_frame = frame

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.end_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            self.end_point = event.pos()

            if self.original_size and self.display_rect.isValid():
                bbox = self._calculate_bbox()
                if bbox and self.current_frame is not None:
                    self.temp_bbox = bbox
                    x1, y1, x2, y2 = bbox
                    cropped = self.current_frame[y1:y2, x1:x2].copy()
                    self.bbox_selected.emit(bbox, cropped)
            self.update()

    def _calculate_bbox(self):
        if not self.original_size or not self.display_rect.isValid():
            return None

        dx = self.display_rect.x()
        dy = self.display_rect.y()
        dw = self.display_rect.width()
        dh = self.display_rect.height()
        ow, oh = self.original_size

        x1 = int((min(self.start_point.x(), self.end_point.x()) - dx) * ow / dw)
        y1 = int((min(self.start_point.y(), self.end_point.y()) - dy) * oh / dh)
        x2 = int((max(self.start_point.x(), self.end_point.x()) - dx) * ow / dw)
        y2 = int((max(self.start_point.y(), self.end_point.y()) - dy) * oh / dh)

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(ow, x2), min(oh, y2)

        if x2 - x1 > 10 and y2 - y1 > 10:
            return [x1, y1, x2, y2]
        return None

    def clear_temp_bbox(self):
        self.temp_bbox = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        if self.drawing:
            painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.PenStyle.DashLine))
            rect = QRect(self.start_point, self.end_point).normalized()
            painter.drawRect(rect)

        elif self.temp_bbox and self.original_size and self.display_rect.isValid():
            painter.setPen(QPen(QColor(0, 255, 0), 2))
            dx = self.display_rect.x()
            dy = self.display_rect.y()
            dw = self.display_rect.width()
            dh = self.display_rect.height()
            ow, oh = self.original_size

            x1 = int(self.temp_bbox[0] * dw / ow + dx)
            y1 = int(self.temp_bbox[1] * dh / oh + dy)
            x2 = int(self.temp_bbox[2] * dw / ow + dx)
            y2 = int(self.temp_bbox[3] * dh / oh + dy)
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            painter.drawText(x1, y1 - 5, "Press SAVE")


class SampleItem(QFrame):
    """單個 Sample 顯示元件"""
    delete_clicked = pyqtSignal(int)  # sample index

    def __init__(self, index, pixmap, is_positive, parent=None):
        super().__init__(parent)
        self.index = index
        self.is_positive = is_positive

        self.setFixedSize(90, 75)
        border_color = "#0f0" if is_positive else "#f00"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #111;
                border: 2px solid {border_color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # 圖片
        img_label = QLabel()
        img_label.setPixmap(pixmap.scaled(80, 50, Qt.AspectRatioMode.KeepAspectRatio))
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        # 標籤和刪除
        bottom = QHBoxLayout()
        label = QLabel("+" if is_positive else "-")
        label.setStyleSheet(f"color: {border_color}; font-weight: bold; font-size: 12px;")
        bottom.addWidget(label)

        del_btn = QPushButton("×")
        del_btn.setFixedSize(18, 18)
        del_btn.setStyleSheet("""
            QPushButton {
                background: #333; color: #888;
                border: none; font-size: 12px;
            }
            QPushButton:hover { background: #f00; color: #fff; }
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        bottom.addWidget(del_btn)

        layout.addLayout(bottom)


class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = False
        self.camera = None

    def run(self):
        self.camera = cv2.VideoCapture(0)
        self.running = True

        while self.running:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    self.frame_ready.emit(frame.copy())
            self.msleep(30)

        if self.camera:
            self.camera.release()

    def stop(self):
        self.running = False
        self.wait()


class InferenceThread(QThread):
    result_ready = pyqtSignal(np.ndarray)
    status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.predictor = None
        self.model_loaded = False
        self.frame_queue = Queue(maxsize=2)

        self.text_prompt = []
        self.exemplar_bboxes = []  # list of [x1,y1,x2,y2]
        self.exemplar_labels = []  # list of 1 or 0
        self.confidence = 0.25
        self.mutex = QMutex()

    def load_model(self, model_path):
        try:
            from ultralytics.models.sam import SAM3SemanticPredictor
            self.status_update.emit("Loading model...")

            self.predictor = SAM3SemanticPredictor(overrides=dict(
                conf=self.confidence,
                task="segment",
                mode="predict",
                model=str(model_path),
                device=0,
                half=True
            ))
            self.model_loaded = True
            self.status_update.emit("Ready")
            return True
        except Exception as e:
            self.status_update.emit(f"Load failed: {str(e)[:30]}")
            return False

    def set_prompt(self, text_prompt):
        self.mutex.lock()
        self.text_prompt = text_prompt
        self.mutex.unlock()

    def set_exemplars(self, bboxes, labels):
        self.mutex.lock()
        self.exemplar_bboxes = bboxes
        self.exemplar_labels = labels
        self.mutex.unlock()

    def set_confidence(self, conf):
        self.mutex.lock()
        self.confidence = conf
        if self.predictor:
            self.predictor.args.conf = conf
        self.mutex.unlock()

    def add_frame(self, frame):
        try:
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except Empty:
                    pass
            self.frame_queue.put_nowait(frame)
        except:
            pass

    def run(self):
        self.running = True

        while self.running:
            try:
                frame = self.frame_queue.get(timeout=0.1)

                self.mutex.lock()
                current_prompt = self.text_prompt.copy() if self.text_prompt else []
                current_bboxes = self.exemplar_bboxes.copy()
                current_labels = self.exemplar_labels.copy()
                self.mutex.unlock()

                has_exemplars = len(current_bboxes) > 0

                if self.model_loaded and (current_prompt or has_exemplars):
                    try:
                        self.predictor.set_image(frame)

                        if current_prompt and has_exemplars:
                            results = self.predictor(
                                text=current_prompt,
                                bboxes=current_bboxes,
                                labels=current_labels
                            )
                        elif current_prompt:
                            results = self.predictor(text=current_prompt)
                        elif has_exemplars:
                            results = self.predictor(
                                bboxes=current_bboxes,
                                labels=current_labels
                            )
                        else:
                            results = None

                        if results and len(results) > 0:
                            frame = results[0].plot()
                    except:
                        pass

                self.result_ready.emit(frame)

            except Empty:
                continue
            except:
                continue

    def stop(self):
        self.running = False
        self.wait()


class SAM3GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ViT 測試")
        self.setMinimumSize(1200, 800)

        self.camera_thread = None
        self.inference_thread = None
        self.is_camera_on = False

        # Sample 相關
        self.pending_bbox = None
        self.pending_crop = None
        self.samples = []  # list of {'bbox': [], 'crop': np.array, 'is_positive': bool}

        self.init_ui()
        self.init_threads()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # === 左側：影像區 ===
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        self.camera_label = VideoLabel()
        self.camera_label.setMinimumSize(750, 560)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #0a0a0a;
                border: 1px solid #333;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setText("Camera Off")
        self.camera_label.setFont(QFont("Consolas", 14))
        self.camera_label.bbox_selected.connect(self.on_bbox_selected)
        left_panel.addWidget(self.camera_label)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        left_panel.addWidget(self.status_label)

        main_layout.addLayout(left_panel, stretch=3)

        # === 右側：控制面板 ===
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        # Camera
        self.btn_camera = QPushButton("START")
        self.btn_camera.setStyleSheet(self.get_button_style())
        self.btn_camera.clicked.connect(self.toggle_camera)
        right_panel.addWidget(self.btn_camera)

        right_panel.addWidget(self.create_separator())

        # Text Prompt
        prompt_label = QLabel("TEXT PROMPT")
        prompt_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        right_panel.addWidget(prompt_label)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("e.g. dice, person")
        self.text_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; font-size: 13px;
                border: 1px solid #333; background-color: #111; color: #fff;
            }
            QLineEdit:focus { border-color: #fff; }
        """)
        self.text_input.returnPressed.connect(self.apply_settings)
        right_panel.addWidget(self.text_input)

        right_panel.addWidget(self.create_separator())

        # Confidence
        conf_label = QLabel("CONFIDENCE")
        conf_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        right_panel.addWidget(conf_label)

        conf_layout = QHBoxLayout()
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setMinimum(5)
        self.conf_slider.setMaximum(95)
        self.conf_slider.setValue(25)
        self.conf_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #333; }
            QSlider::handle:horizontal {
                background: #fff; width: 14px; height: 14px;
                margin: -5px 0; border-radius: 7px;
            }
            QSlider::sub-page:horizontal { background: #888; }
        """)
        self.conf_slider.valueChanged.connect(self.on_confidence_changed)
        conf_layout.addWidget(self.conf_slider)

        self.conf_value = QLabel("0.25")
        self.conf_value.setStyleSheet("color: #fff; font-size: 12px; min-width: 35px;")
        conf_layout.addWidget(self.conf_value)
        right_panel.addLayout(conf_layout)

        right_panel.addWidget(self.create_separator())

        # === SAMPLES 區域 ===
        samples_label = QLabel("SAMPLES")
        samples_label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold;")
        right_panel.addWidget(samples_label)

        # 正向/負向選擇
        mode_layout = QHBoxLayout()
        self.btn_group = QButtonGroup(self)

        self.radio_positive = QRadioButton("Positive (+)")
        self.radio_positive.setChecked(True)
        self.radio_positive.setStyleSheet("color: #0f0; font-size: 11px;")
        self.btn_group.addButton(self.radio_positive, 1)
        mode_layout.addWidget(self.radio_positive)

        self.radio_negative = QRadioButton("Negative (-)")
        self.radio_negative.setStyleSheet("color: #f00; font-size: 11px;")
        self.btn_group.addButton(self.radio_negative, 0)
        mode_layout.addWidget(self.radio_negative)

        right_panel.addLayout(mode_layout)

        # 提示
        hint = QLabel("Draw box on video, then SAVE")
        hint.setStyleSheet("color: #555; font-size: 10px;")
        right_panel.addWidget(hint)

        # Sample 列表區域
        self.samples_container = QWidget()
        self.samples_layout = QHBoxLayout(self.samples_container)
        self.samples_layout.setContentsMargins(0, 0, 0, 0)
        self.samples_layout.setSpacing(5)
        self.samples_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.samples_container)
        scroll.setFixedHeight(95)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: #0a0a0a; border: 1px solid #333; }
            QScrollBar:horizontal {
                height: 8px; background: #111;
            }
            QScrollBar::handle:horizontal {
                background: #444; border-radius: 4px;
            }
        """)
        right_panel.addWidget(scroll)

        # Sample 數量
        self.sample_count = QLabel("0 samples")
        self.sample_count.setStyleSheet("color: #666; font-size: 10px;")
        right_panel.addWidget(self.sample_count)

        # Save / Clear 按鈕
        sample_btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("SAVE")
        self.btn_save.setStyleSheet(self.get_button_style(accent=True))
        self.btn_save.clicked.connect(self.save_sample)
        self.btn_save.setEnabled(False)
        sample_btn_layout.addWidget(self.btn_save)

        self.btn_clear_all_samples = QPushButton("CLEAR ALL")
        self.btn_clear_all_samples.setStyleSheet(self.get_button_style(secondary=True))
        self.btn_clear_all_samples.clicked.connect(self.clear_all_samples)
        sample_btn_layout.addWidget(self.btn_clear_all_samples)

        right_panel.addLayout(sample_btn_layout)

        right_panel.addWidget(self.create_separator())

        # Apply
        self.btn_apply = QPushButton("APPLY")
        self.btn_apply.setStyleSheet(self.get_button_style(primary=True))
        self.btn_apply.clicked.connect(self.apply_settings)
        right_panel.addWidget(self.btn_apply)

        right_panel.addStretch()

        # 設定顯示
        self.current_settings = QLabel("")
        self.current_settings.setStyleSheet("color: #444; font-size: 10px;")
        self.current_settings.setWordWrap(True)
        right_panel.addWidget(self.current_settings)

        main_layout.addLayout(right_panel, stretch=1)

        # 全域樣式
        self.setStyleSheet("""
            QMainWindow { background-color: #000; }
            QWidget {
                color: #fff;
                font-family: 'Consolas', 'SF Mono', monospace;
            }
        """)

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #222; max-height: 1px;")
        return line

    def get_button_style(self, primary=False, secondary=False, accent=False):
        if primary:
            return """
                QPushButton {
                    background-color: #fff; color: #000;
                    border: none; padding: 12px;
                    font-size: 13px; font-weight: bold;
                }
                QPushButton:hover { background-color: #ddd; }
            """
        elif accent:
            return """
                QPushButton {
                    background-color: #0a0; color: #fff;
                    border: none; padding: 10px;
                    font-size: 12px; font-weight: bold;
                }
                QPushButton:hover { background-color: #0c0; }
                QPushButton:disabled { background-color: #333; color: #666; }
            """
        elif secondary:
            return """
                QPushButton {
                    background-color: transparent; color: #666;
                    border: 1px solid #333; padding: 10px;
                    font-size: 11px;
                }
                QPushButton:hover { color: #fff; border-color: #666; }
            """
        else:
            return """
                QPushButton {
                    background-color: #111; color: #fff;
                    border: 1px solid #333; padding: 12px;
                    font-size: 13px; font-weight: bold;
                }
                QPushButton:hover { background-color: #222; border-color: #555; }
            """

    def init_threads(self):
        self.inference_thread = InferenceThread()
        self.inference_thread.result_ready.connect(self.display_frame)
        self.inference_thread.status_update.connect(self.update_status)

        model_path = Path(__file__).parent.parent / "sam3.pt"
        self.inference_thread.load_model(model_path)
        self.inference_thread.start()

    def toggle_camera(self):
        if self.is_camera_on:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.on_frame_captured)
        self.camera_thread.start()

        self.is_camera_on = True
        self.btn_camera.setText("STOP")
        self.update_status("Camera on")

    def stop_camera(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None

        self.is_camera_on = False
        self.btn_camera.setText("START")
        self.camera_label.setText("Camera Off")
        self.camera_label.setPixmap(QPixmap())
        self.update_status("Camera off")

    def on_frame_captured(self, frame):
        h, w = frame.shape[:2]
        self.camera_label.set_original_size(w, h)
        self.camera_label.set_current_frame(frame)

        if self.inference_thread:
            self.inference_thread.add_frame(frame.copy())

    def display_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        label_w, label_h = self.camera_label.width(), self.camera_label.height()
        pix_w, pix_h = scaled_pixmap.width(), scaled_pixmap.height()
        dx = (label_w - pix_w) // 2
        dy = (label_h - pix_h) // 2
        self.camera_label.display_rect = QRect(dx, dy, pix_w, pix_h)

        self.camera_label.setPixmap(scaled_pixmap)

    def on_bbox_selected(self, bbox, cropped):
        self.pending_bbox = bbox
        self.pending_crop = cropped
        self.btn_save.setEnabled(True)
        mode = "Positive" if self.radio_positive.isChecked() else "Negative"
        self.update_status(f"Press SAVE ({mode})")

    def save_sample(self):
        if self.pending_bbox is None or self.pending_crop is None:
            return

        is_positive = self.radio_positive.isChecked()

        # 建立預覽圖
        crop_rgb = cv2.cvtColor(self.pending_crop, cv2.COLOR_BGR2RGB)
        h, w, ch = crop_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(crop_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # 儲存 sample
        self.samples.append({
            'bbox': self.pending_bbox,
            'crop': self.pending_crop,
            'is_positive': is_positive,
            'pixmap': pixmap
        })

        # 更新 UI
        self.refresh_samples_ui()
        self.update_inference_exemplars()

        # 清除暫存
        self.camera_label.clear_temp_bbox()
        self.pending_bbox = None
        self.pending_crop = None
        self.btn_save.setEnabled(False)

        pos_count = sum(1 for s in self.samples if s['is_positive'])
        neg_count = len(self.samples) - pos_count
        self.update_status(f"Saved ({pos_count}+ / {neg_count}-)")

    def refresh_samples_ui(self):
        # 清除舊的
        while self.samples_layout.count():
            item = self.samples_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 添加新的
        for i, sample in enumerate(self.samples):
            item = SampleItem(i, sample['pixmap'], sample['is_positive'])
            item.delete_clicked.connect(self.delete_sample)
            self.samples_layout.addWidget(item)

        self.sample_count.setText(f"{len(self.samples)} samples")
        self.update_current_settings()

    def delete_sample(self, index):
        if 0 <= index < len(self.samples):
            del self.samples[index]
            self.refresh_samples_ui()
            self.update_inference_exemplars()

    def clear_all_samples(self):
        self.samples.clear()
        self.pending_bbox = None
        self.pending_crop = None
        self.camera_label.clear_temp_bbox()
        self.btn_save.setEnabled(False)

        self.refresh_samples_ui()
        self.update_inference_exemplars()
        self.update_status("Samples cleared")

    def update_inference_exemplars(self):
        if self.inference_thread:
            bboxes = [s['bbox'] for s in self.samples]
            labels = [1 if s['is_positive'] else 0 for s in self.samples]
            self.inference_thread.set_exemplars(bboxes, labels)

    def on_confidence_changed(self, value):
        conf = value / 100.0
        self.conf_value.setText(f"{conf:.2f}")

        if self.inference_thread:
            self.inference_thread.set_confidence(conf)

    def apply_settings(self):
        text = self.text_input.text().strip()
        text_prompt = [t.strip() for t in text.split(",") if t.strip()] if text else []

        if self.inference_thread:
            self.inference_thread.set_prompt(text_prompt)

        self.update_current_settings()
        self.update_status("Applied")

    def update_current_settings(self):
        parts = []
        text = self.text_input.text().strip()
        if text:
            parts.append(f"text: {text}")

        pos = sum(1 for s in self.samples if s['is_positive'])
        neg = len(self.samples) - pos
        if self.samples:
            parts.append(f"samples: {pos}+ / {neg}-")

        self.current_settings.setText(" | ".join(parts) if parts else "")

    def update_status(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        self.stop_camera()
        if self.inference_thread:
            self.inference_thread.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = SAM3GUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
