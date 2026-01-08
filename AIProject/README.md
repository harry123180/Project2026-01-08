# AI Gesture Recognition Project (AI 手勢辨識專案)

## 專案核心目標
利用深度學習技術（CNN 卷積神經網絡）實現即時手勢辨識，並結合現代化 GUI 介面，讓使用者能直觀地與 AI 模型進行互動。此專案專為手勢控制、手語翻譯或人機互動 (HCI) 原型開發而設計。

---

## 🖐️ 手勢辨識設計細節 (System Architecture)

### 1. 影像處理管道 (Image Processing Pipeline)
為了確保 AI 模型的辨識準確度，每一幀從攝影機獲取的影像都會經過以下標準化流程：
- **Aspect Ratio Maintenance**: 使用 `PIL.ImageOps.fit` 進行中心裁剪，防止手勢因比例壓縮而變形。
- **Resolution Scaling**: 統一調整為 `224x224` 像素（MobileNetV2 標準輸入尺寸）。
- **Normalization**: 將像素值從 `[0, 255]` 映射至 `[-1, 1]`，以符合 Keras 預訓練模型的數學期望。

### 2. 模型架構與相容性
- **Base Model**: Google Teachable Machine (基於 MobileNet)。
- **Back-end**: 使用 `tf-keras` 支援舊版 `.h5` 格式，解決 Keras 3 的反序列化相容性問題。
- **Inference Speed**: 優化後的推論循環可確保在一般筆電 CPU 上達到穩定流暢的 FPS。

---

## 🎨 UI/UX 概念設計 (User Interface Design)

### 設計美學
- **Theme**: 採用 Dark Mode (深色模式)，降低長時間觀看攝影機畫面的視覺疲勞。
- **Color Palette**: 
  - 成功辨識 (信心度 > 80%)：`#2CC985` (翡翠綠)
  - 低信心度/不確定：`#EB5757` (警示紅)

### 介面佈局 (Layout)
1. **左側控制面板 (Sidebar)**：顯示系統狀態、模型載入資訊及控制按鈕。
2. **中央主要區域 (Main Stage)**：
   - **Live View**: 640x480 的流暢預覽畫面。
   - **Result HUD**: 位於畫面下方，顯示目前辨識出的手勢名稱。
   - **Confidence Bar**: 動態進度條，顯示 AI 對目前判斷的「肯定程度」。

### UI 概念設計圖預留位
<!-- 請將您的圖片放在專案目錄下，並將下方的路徑替換為您的檔名 -->
![UI Design Concept Sketch](path/to/your/ui_design_sketch.png)
> *圖 1：AI 手勢辨識系統介面原型草圖*

---

## 📁 專案目錄結構
```text
AIProject/
├── Example/
│   ├── gui_app.py      # 主程式 (GUI 整合版)
│   ├── tm.py           # 原始推論腳本 (CLI 調試版)
│   ├── keras_model.h5  # AI 模型檔 (預留)
│   └── labels.txt      # 標籤檔 (預留)
├── README.md           # 專案說明文件
└── (其他後端/前端開發中檔案...)
```

---

## 🛠️ 開發環境需求
- **OS**: Windows / macOS / Linux
- **Environment**: Python 3.11 (推薦使用 Anaconda `myenv` 環境)
- **Key Libraries**:
  - `customtkinter`: 現代化 UI 組件
  - `tf-keras`: 處理模型載入
  - `opencv-python`: 處理攝影機串流
  - `pillow`: 影像預處理

## 🚀 快速啟動
```bash
# 安裝依賴項
pip install tensorflow tf-keras customtkinter opencv-python pillow

# 啟動應用
python Example/gui_app.py
```
