import cv2
from ultralytics.models.sam import SAM3SemanticPredictor

# 載入 SAM3 模型 (使用 GPU + 半精度加速)
predictor = SAM3SemanticPredictor(overrides=dict(
    conf=0.25,
    task="segment",
    mode="predict",
    model="sam3.pt",
    device=0,       # 使用 GPU
    half=True       # 半精度加速
))

# 文字提示（可以修改成你要偵測的物件）
TEXT_PROMPT = ["dice"]

# 滑鼠框選相關變數
drawing = False
start_point = None
end_point = None
exemplar_bbox = None  # 儲存範例 bounding box
use_text_only = True  # 預設先用文字模式

def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, end_point, exemplar_bbox, use_text_only

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        end_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        # 設定範例 bbox [x1, y1, x2, y2]
        x1 = min(start_point[0], end_point[0])
        y1 = min(start_point[1], end_point[1])
        x2 = max(start_point[0], end_point[0])
        y2 = max(start_point[1], end_point[1])
        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:  # 確保框選區域夠大
            exemplar_bbox = [x1, y1, x2, y2]
            use_text_only = False
            print(f"已設定範例區域: {exemplar_bbox}")
            print(f"模式: 文字 '{TEXT_PROMPT}' + 範例框")

# 開啟攝影機
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("無法開啟攝影機")
    exit()

# 設定視窗和滑鼠回調
cv2.namedWindow("SAM3 Dice Detection")
cv2.setMouseCallback("SAM3 Dice Detection", mouse_callback)

print("=" * 50)
print("SAM3 骰子偵測 - 文字 + 範例模式")
print("=" * 50)
print(f"文字提示: {TEXT_PROMPT}")
print("操作說明:")
print("  - 啟動後自動用文字偵測")
print("  - 用滑鼠框選可加入範例輔助")
print("  - 按 't' 切換純文字模式")
print("  - 按 'c' 清除範例")
print("  - 按 'q' 退出程式")
print("=" * 50)

while True:
    ret, frame = cap.read()
    if not ret:
        print("無法讀取畫面")
        break

    # 設定當前幀
    predictor.set_image(frame)

    # 根據模式進行預測
    try:
        if use_text_only:
            # 純文字模式
            results = predictor(text=TEXT_PROMPT)
        elif exemplar_bbox is not None:
            # 文字 + 範例模式
            results = predictor(text=TEXT_PROMPT, bboxes=[exemplar_bbox], labels=[1])
        else:
            results = None
    except Exception as e:
        # 如果組合模式失敗，退回純文字模式
        results = predictor(text=TEXT_PROMPT)

    # 繪製結果
    if results and len(results) > 0:
        annotated_frame = results[0].plot()
    else:
        annotated_frame = frame.copy()

    # 繪製正在框選的矩形
    if drawing and start_point and end_point:
        cv2.rectangle(annotated_frame, start_point, end_point, (0, 255, 0), 2)

    # 顯示範例區域（黃色框）
    if exemplar_bbox is not None and not use_text_only:
        cv2.rectangle(annotated_frame,
                      (exemplar_bbox[0], exemplar_bbox[1]),
                      (exemplar_bbox[2], exemplar_bbox[3]),
                      (0, 255, 255), 2)
        cv2.putText(annotated_frame, "Exemplar",
                    (exemplar_bbox[0], exemplar_bbox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # 顯示目前模式
    mode_text = f"Mode: Text '{TEXT_PROMPT[0]}'" if use_text_only else f"Mode: Text + Exemplar"
    cv2.putText(annotated_frame, mode_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 顯示畫面
    cv2.imshow("SAM3 Dice Detection", annotated_frame)

    # 鍵盤控制
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        exemplar_bbox = None
        use_text_only = True
        print("已清除範例，切換到純文字模式")
    elif key == ord('t'):
        use_text_only = True
        print(f"切換到純文字模式: {TEXT_PROMPT}")

cap.release()
cv2.destroyAllWindows()
