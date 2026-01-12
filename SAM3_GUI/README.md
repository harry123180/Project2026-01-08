# ViT 測試 - SAM3 GUI

基於 Meta SAM3 (Segment Anything Model 3) 的即時影像分割工具。

## 功能

- 即時攝影機串流
- 文字提示 (Text Prompt) 分割
- 正向/負向 Sample 範例學習
- 信心度門檻調整
- 多線程架構，GUI 不阻塞

## 安裝

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 安裝 PyTorch GPU 版本（建議）

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

### 3. 下載 SAM3 模型

1. 前往 [Hugging Face - facebook/sam3](https://huggingface.co/facebook/sam3) 申請存取權限
2. 下載 `sam3.pt` 檔案
3. 將檔案放置於專案根目錄（與 `SAM3_GUI` 資料夾同層）

```
Project/
├── sam3.pt          # 模型檔案放這裡
├── SAM3_GUI/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
```

## 使用方式

```bash
cd SAM3_GUI
python main.py
```

## 操作說明

| 功能 | 說明 |
|------|------|
| **START/STOP** | 開啟/關閉攝影機 |
| **TEXT PROMPT** | 輸入文字提示，如 `dice, person` |
| **CONFIDENCE** | 調整信心度門檻 (0.05 - 0.95) |
| **Positive (+)** | 選擇正向範例模式 |
| **Negative (-)** | 選擇負向範例模式 |
| **框選** | 在影像上拖曳滑鼠框選物件 |
| **SAVE** | 保存框選的範例 |
| **APPLY** | 套用文字提示設定 |

## 架構

```
┌─────────────────────────────────────────────┐
│              GUI Thread                      │
│         (介面更新、使用者互動)                │
└──────────────────┬──────────────────────────┘
                   │ Signal/Slot
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐   ┌─────────────────┐
│  CameraThread   │   │ InferenceThread │
│  (攝影機捕獲)    │ → │  (SAM3 推理)    │
└─────────────────┘   └─────────────────┘
```

## 系統需求

- Python 3.10+
- NVIDIA GPU (建議 8GB+ VRAM)
- CUDA 12.x

## License

MIT
