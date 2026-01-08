# AI視覺辨識-剪刀石頭布

這是一個使用 `customtkinter` 創建的簡單 AI 應用程式，它能夠即時讀取攝影機串流、將影像傳遞給模型進行預測，並將預測結果顯示在直觀的圖形使用者介面 (GUI) 上。

## 特色 (Features)

*   **即時攝影機串流**：顯示來自網路攝影機的即時影像。
*   **AI模型預測**：將攝影機影像輸入到預訓練的 Keras 模型中進行分類。
*   **視覺化預測結果**：以進度條形式清晰展示每個類別的置信度分數。
*   **易於操作的 GUI**：透過簡單的按鈕控制攝影機的開啟與關閉。
*   **固定佈局**：GUI 介面各區塊大小與位置固定，不會隨內容變動。

## 畫面預覽 (Screenshot)

以下是應用程式實際運行的截圖：

![AI 辨識展演平台運行截圖](剪刀.png)

## 整體流程 (Overall Workflow)

1.  **攝影機輸入 (Camera Input)**：
    *   使用者點擊「開啟相機」按鈕啟動攝影機。
    *   應用程式使用 `opencv-python` 庫從預設的網路攝影機捕捉影像幀。
    *   捕捉到的影像幀會被即時顯示在 GUI 左側的「圖片顯示區域」。

2.  **影像預處理 (Image Preprocessing)**：
    *   每個捕捉到的影像幀都會經過預處理，以符合 Keras 模型的輸入要求。
    *   影像會被調整為 224x224 像素的大小。
    *   影像像素值會被正規化 (normalize)，通常是從 0-255 範圍縮放到 -1 到 1 的範圍，以適應模型訓練時的資料格式。

3.  **模型預測 (Model Prediction)**：
    *   預處理後的影像會被送入預載入的 Keras 模型（`keras_model.h5`）。
    *   模型會對影像內容進行分類，輸出每個類別的置信度分數。

4.  **結果顯示 (Result Display)**：
    *   模型的預測結果（各類別的置信度分數）會即時更新到 GUI 右上方的「AI預測結果」區塊。
    *   每個類別的名稱及其對應的置信度（百分比形式）會透過進度條清晰地顯示。

5.  **攝影機控制 (Camera Control)**：
    *   使用者可以隨時點擊「關閉相機」按鈕來停止攝影機串流和模型預測。


## 使用方式 (Usage)

1.  **下載 (Clone the Repository)**：
    ```bash
    git clone [repo連結]
    cd [repo目錄]
    ```

2.  **確保模型與標籤檔案存在 (Ensure Model and Label Files Exist)**：
    請將您的 `keras_model.h5` 和 `labels.txt` 檔案放置在 `Joanna_20260107/converted_keras_joanna/` 路徑下。

3.  **運行應用程式 (Run the Application)**：
    ```bash
    python app_gui.py
    ```

4.  **操作介面 (Operate the GUI)**：
    *   點擊 GUI 上的「開啟相機」按鈕開始辨識。
    *   點擊「關閉相機」按鈕停止辨識。

## 檔案結構 (File Structure)

```
.
├── app_gui.py                  # 主應用程式文件，包含GUI和AI邏輯
├── Joanna_20260107/
│   └── converted_keras_joanna/
│       ├── keras_model.h5      # 預訓練的Keras模型文件
│       └── labels.txt          # 模型分類標籤文件
└── 螢幕擷取畫面 2026-01-08 144607.png   # 應用程式運行截圖
# ... 其他文件 ...
```