import cv2

def show_camera_stream():
    """
    開啟並顯示預設鏡頭的即時影像串流。

    按下 'q' 鍵可以關閉視窗並結束程式。
    """
    # 嘗試開啟預設鏡頭 (通常索引值為 0)
    cap = cv2.VideoCapture(0)

    # 檢查鏡頭是否成功開啟
    if not cap.isOpened():
        print("錯誤：無法開啟鏡頭。請確認您的鏡頭已連接且未被其他程式佔用。")
        return

    print("鏡頭已開啟。按下 'q' 鍵以關閉視窗。")

    # 迴圈以持續讀取並顯示影像
    while True:
        # 從鏡頭讀取一幀影像
        # ret 是一個布林值，表示是否成功讀取
        # frame 是讀取到的影像幀
        ret, frame = cap.read()

        # 如果讀取失敗 (例如：鏡頭被拔除)，則跳出迴圈
        if not ret:
            print("錯誤：無法讀取影像幀。")
            break

        # 在一個名為 "Camera Stream" 的視窗中顯示影像
        cv2.imshow('Camera Stream', frame)

        # 等待 1 毫秒，並檢查是否有按鍵輸入
        # 0xFF & ord('q') 是為了確保在不同系統上都能正確捕捉到 'q' 鍵
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("接收到關閉指令...")
            break

    # 釋放鏡頭資源
    cap.release()
    # 關閉所有 OpenCV 建立的視窗
    cv2.destroyAllWindows()
    print("程式已結束。")

if __name__ == '__main__':
    show_camera_stream()
