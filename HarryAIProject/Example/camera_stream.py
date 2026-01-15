import cv2

def main():
    # 開啟攝影機 (0 通常是預設攝影機)
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("錯誤：無法開啟攝影機。")
        return
    print("攝影機已開啟。按下 'q' 鍵可退出視窗。")
    while True:
        # 逐幀捕獲影像
        ret, frame = cap.read()
        if not ret:
            print("錯誤：無法接收串流幀。")
            break

        # 顯示影像
        cv2.imshow('Camera AAAAAAAAA Example', frame)

        # 偵測按鍵，按下 'q' 鍵退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 釋放攝影機資源並關閉視窗
    cap.release()
    cv2.destroyAllWindows()
    print("串流已停止。")

if __name__ == "__main__":
    main()
