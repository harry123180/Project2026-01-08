# 個人化行程管理 App 開發計畫 (V2)

這份計畫基於 V1 版本進行修訂，旨在滿足使用者個人化的行程與工作管理需求。核心是建立一個以日曆為中心、方便記錄客戶會議與工作內容的單人使用工具。

---

## 1. 專案目標 (V2)

- **核心定位**: 一個為個人設計的行程管理與工作日誌工具。
- **關鍵特色**:
    - 以日曆視覺化呈現所有行程。
    - 快速記錄與客戶相關的會議或任務。
    - 清晰地區分已完成和未完成的項目。
    - 完全為單人使用，無需複雜的登入或權限管理。

---

## 2. 技術棧 (Technology Stack)

- **前端 (Frontend)**:
    - Vue.js (Vue 3 + Vite)
    - **FullCalendar**: 一個功能強大的日曆組件庫，用於實現日曆檢視。
- **後端 (Backend)**: Python 3, Flask
- **資料庫 (Database)**: SQLite 3

---

## 3. 核心功能 (V2)

- [ ] **日曆檢視 (Calendar View)**:
    - 以月/週/日的形式顯示所有行程與任務。
    - 事件可以有不同的顏色標記（例如：會議 vs. 個人任務）。
    - 可以透過拖曳來快速更改事件的日期。
- [ ] **列表檢視 (List View)**:
    - 傳統的列表模式，可篩選顯示所有、已完成或未完成的任務。
- [ ] **新增事件/任務**:
    - 表單應包含：標題（工作內容）、開始時間、結束時間、相關客戶（可選填）。
- [ ] **修改事件/任務**:
    - 可點擊日曆上的事件來編輯其所有詳細資訊。
- [ ] **標記完成**:
    - 在日曆或列表中都能夠將一個事件/任務標記為已完成。已完成的項目應有明顯的視覺區別（如變灰、劃掉）。
- [ ] **刪除事件/任務**:
    - 永久刪除一個行程記錄。

---

## 4. 架構設計 (V2 修訂)

### 4.1. 資料庫設計 (SQLite)

為了儲存更豐富的資訊，我們將原來的 `todos` 表擴充為 `tasks` 表。

**資料表: `tasks`**

| 欄位 (Column)   | 型別 (Type)         | 描述 (Description)                           |
|-----------------|---------------------|----------------------------------------------|
| `id`            | `INTEGER`           | 主鍵，自動增長。                             |
| `title`         | `TEXT`              | 行程標題或工作內容，不允許為空。             |
| `client_name`   | `TEXT`              | 相關客戶名稱，可為空。                       |
| `start_time`    | `DATETIME`          | 行程開始時間，不允許為空。                   |
| `end_time`      | `DATETIME`          | 行程結束時間，可為空。                       |
| `completed`     | `BOOLEAN`           | 是否完成，預設為 `false` (0)。                 |
| `created_at`    | `DATETIME`          | 記錄建立時間，預設為當前時間戳記。           |

**SQL 建立語法:**
```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    client_name TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2. 後端 API 設計 (Flask)

API 端點將進行調整以處理日曆所需的時間範圍查詢。

| HTTP 方法 | 路徑 (Path)             | 描述                                     | 請求 Body (JSON)                                | 成功回應 (JSON)                                        |
|-----------|-------------------------|------------------------------------------|-------------------------------------------------|--------------------------------------------------------|
| `GET`     | `/tasks`                | 取得指定時間範圍內的行程                 | Query Params: `?start=YYYY-MM-DD&end=YYYY-MM-DD` | `[{"id": 1, "title": "與 A 客戶開會", ...}, ...]`        |
| `POST`    | `/tasks`                | 新增一個行程                             | `{"title": "...", "client_name": "...", "start_time": "..."}` | `{"id": 2, "title": "...", ...}`                         |
| `PUT`     | `/tasks/<int:task_id>`  | 更新一個行程（內容、時間、狀態等）       | `{"title": "...", "completed": true, ...}`       | `{"id": 1, "title": "...", ...}`                         |
| `DELETE`  | `/tasks/<int:task_id>`  | 刪除一個行程                             | N/A                                             | `{"message": "Task deleted successfully"}`             |

### 4.3. 前端設計 (Vue.js)

- **主要佈局**: 可能採用左右佈局，左側為 FullCalendar 日曆，右側為當天或選定日期的任務列表。或者使用頁籤切換「日曆」與「列表」模式。
- **`CalendarView.vue`**: 核心組件，整合 `FullCalendar`。
    - 負責在載入時及切換月份時，向後端發送 `GET /api/tasks` 請求，並將回傳的事件渲染到日曆上。
    - 處理日曆事件的點擊（開啟編輯彈窗）、拖曳（呼叫 `PUT` API 更新時間）。
- **`TaskForm.vue`**: 一個彈出視窗 (Modal) 或獨立頁面，用於新增/編輯任務。
    - 包含標題、客戶名稱輸入框，以及日期時間選擇器。
- **`TaskList.vue`**: 傳統的列表檢視，作為日曆的補充。

---

## 5. 開發步驟 (V2 修訂)

1.  **環境建置**: (同 V1)
2.  **後端開發**:
    -   建立 Flask App，設定 CORS。
    -   使用新的 Schema 建立 `tasks` 資料庫。
    -   **優先實作 `GET /api/tasks` (含時間範圍查詢) 和 `POST /api/tasks`**。
    -   接著完成 `PUT` 和 `DELETE` 端點。
3.  **前端開發**:
    -   安裝並設定 Vite + Vue 3。
    -   **安裝 `fullcalendar` 及其 Vue 組件 (`@fullcalendar/vue3`, `@fullcalendar/daygrid`, etc.)**。
    -   建立 `CalendarView` 組件，讓日曆能成功渲染，並能從後端抓取資料顯示。
    -   建立 `TaskForm` 組件，並實作新增行程的功能。
    -   將日曆的拖曳與點擊事件與後端 API 對接。
    -   完成標記完成與刪除功能。
4.  **整合與測試**: 全面測試所有功能，特別是日期的正確性。

---

這份 V2 計畫更貼近您的實際需求，我們可以以此為藍圖開始進行開發。