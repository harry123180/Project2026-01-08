# 個人行程管理 App 開發計畫 (含日曆與週計畫)

本文件旨在規劃一個為**個人使用**設計的全端行程管理網頁應用程式。此應用程式的核心是日曆和週計畫功能，幫助使用者記錄和管理行程與工作內容。應用程式將採用前後端分離的架構。

---

## 1. 專案概覽

- **應用程式名稱**: ScheduleApp
- **核心目標**: 提供一個視覺化的日曆和週計畫介面，讓使用者可以新增、查看、編輯和刪除每日的行程與工作任務。
- **核心使用者**: 單一使用者（個人使用）。
- **架構**: 前後端分離。
  - **前端**: 一個單頁應用程式（SPA），負責所有使用者介面和互動（日曆、週計畫）。
  - **後端**: 一個 RESTful API 伺服器，負責處理業務邏輯和資料庫存取。
  - **資料庫**: 儲存所有行程和任務資料。

---

## 2. 技術棧 (Technology Stack)

| 層級 | 技術 | 說明 |
| :--- | :--- | :--- |
| **前端 (Frontend)** | Vue.js (Vue 3) | 用於建構使用者介面的現代化 JavaScript 框架。 |
| | **FullCalendar/Vue** | **(新增)** 強大且功能齊全的日曆元件庫，用於實現日曆和週計畫視圖。 |
| | Axios | 一個基於 Promise 的 HTTP 客戶端，用於與後端 API 通訊。 |
| | Tailwind CSS / Bootstrap | (可選) 用於快速建構美觀的 UI。 |
| **後端 (Backend)** | Python 3 | 主要開發語言。 |
| | Flask | 一個輕量級的 WSGI Web 應用框架。 |
| | Flask-SQLAlchemy | 用於操作資料庫的 ORM。 |
| | Flask-CORS | 處理跨來源資源共用（CORS）。 |
| **資料庫 (Database)** | SQLite | 一個輕量級、無伺服器的本地資料庫，適合個人專案。 |
| **開發工具** | Node.js / Vite | 用於前端開發環境、依賴管理和建構。 |
| | `venv` (Python) | 用於建立獨立的 Python 開發環境。 |
| | Git | 版本控制系統。 |

---

## 3. 系統架構

系統架構保持不變，但前後端的職責更加具體化：

1.  **Vue.js 前端**:
    - 透過 **FullCalendar** 元件渲染月視圖、週視圖（週計畫）。
    - 處理使用者互動，如點擊日期新增行程、拖曳調整行程時間。
    - 呼叫後端 API 來獲取、新增、更新和刪除行程資料。
    - 提供表單或彈出視窗（Modal）供使用者輸入行程的詳細資訊。

2.  **Flask 後端 API**:
    - 提供基於日期範圍查詢的 API 端點。
    - 執行行程資料的增刪改查（CRUD）邏輯。
    - 與 SQLite 資料庫進行互動。

3.  **SQLite 資料庫**:
    - 儲存所有行程資料。所有存取都必須經過後端 API。

---

## 4. 核心功能 (MVP - 最小可行性產品)

- **日曆視圖 (Calendar View)**:
  - 以月曆形式顯示所有行程。
  - 使用者可以點擊日曆上的某一天或拖曳選取多天來新增行程。
- **週計畫視圖 (Weekly Planner View)**:
  - 以一週七天的佈局顯示行程，方便使用者規劃一週的工作。
- **新增行程/任務**:
  - 使用者可以定義行程的標題、詳細說明、開始時間和結束時間。
- **編輯行程/任務**:
  - 使用者可以點擊現有行程來修改其內容。
- **刪除行程/任務**:
  - 使用者可以刪除一個行程。
- **拖放修改**:
  - 使用者可以直接在日曆上拖曳行程以更改其日期和時間。

---

## 5. 資料庫結構 (Database Schema)

為了支援日曆功能，我們需要一個更詳細的資料表，將原來的 `todos` 改為 `events`。

**`events` 資料表**

| 欄位名稱 | 資料類型 | 說明 |
| :--- | :--- | :--- |
| `id` | Integer | 主鍵，自動遞增。 |
| `title` | String | 行程或任務的標題，不可為空。 |
| `description` | Text | (新增) 行程的詳細說明或工作內容，可選。 |
| `start_time` | DateTime | (修改) 行程的開始時間，包含日期和時間。 |
| `end_time` | DateTime | (新增) 行程的結束時間，可選。 |
| `is_all_day` | Boolean | (新增) 標記是否為全天行程，預設為 `false`。 |

---

## 6. API 端點設計 (RESTful API)

API 端點需要更新以反映新的資料模型和查詢需求，特別是基於日期的查詢。

| HTTP 方法 | 路徑 | 說明 | 請求 Body (範例) | 回應 (成功) |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/events` | **(修改)** 取得指定日期範圍內的行程。 | (Query Params) `?start=...&end=...` | `200 OK` + `[{"id": 1, ...}]` |
| `POST` | `/api/events` | **(修改)** 新增一個行程。 | `{"title": "...", "start_time": "..."}` | `201 Created` + `{"id": 2, ...}` |
| `PUT` | `/api/events/<int:event_id>` | **(修改)** 更新一個行程。 | `{"title": "...", "start_time": "..."}` | `200 OK` + `{"id": 1, ...}` |
| `DELETE` | `/api/events/<int:event_id>` | **(修改)** 刪除一個行程。 | (無) | `200 OK` + `{"message": "Event deleted"}` |

---

## 7. 專案檔案結構

前端的元件結構將會改變，以容納日曆和相關功能。

```
...
└── frontend/
    ...
    ├── src/
    │   ├── views/          # (新增) 頁面級元件
    │   │   ├── CalendarView.vue
    │   │   └── WeeklyPlannerView.vue
    │   ├── components/      # (修改) 可複用元件
    │   │   └── EventModal.vue # 用於新增/編輯行程的彈出視窗
    ...
```

---

## 8. 開發步驟 (Roadmap) - **已更新**

1.  **第一階段：後端開發**
    1.  設定 Python 虛擬環境並安裝所需套件。
    2.  在 `models.py` 中定義新的 `Event` 資料庫模型。
    3.  **修改 `app.py` 中的 API 端點**：
        - `GET /api/events` 必須能接收 `start` 和 `end` 查詢參數，並回傳該範圍內的行程。
        - 更新 `POST` 和 `PUT` 端點以處理包含 `title`, `start_time`, `end_time` 等新欄位的請求。
    4.  使用 Postman 或 curl 測試 API，特別是日期範圍查詢功能。

2.  **第二階段：前端開發**
    1.  使用 Vite 建立 Vue 專案。
    2.  安裝 `axios` 和 **`@fullcalendar/vue3`** 以及其相關插件 (`@fullcalendar/daygrid`, `@fullcalendar/timegrid`, `@fullcalendar/interaction`)。
    3.  建立 `CalendarView.vue` 頁面，並在其中初始化 FullCalendar 元件。
    4.  設定 FullCalendar 的 `events` 屬性為一個函式，該函式會根據日曆當前的日期範圍去呼叫後端的 `GET /api/events` API。
    5.  建立 `EventModal.vue` 元件，作為新增和編輯行程的表單介面。
    6.  實現 FullCalendar 的互動功能：
        - **`dateClick`**: 點擊日期時，打開 `EventModal` 以新增行程。
        - **`eventClick`**: 點擊行程時，打開 `EventModal` 以編輯該行程。
        - **`eventDrop`** (拖放): 當使用者拖放行程後，呼叫 `PUT /api/events/<id>` 來更新行程的時間。
    7.  建立 `WeeklyPlannerView.vue` 頁面，可以使用 FullCalendar 的 `timeGridWeek` 視圖來實現。

3.  **第三階段：整合與樣式**
    1.  同時執行前後端伺服器進行完整測試。
    2.  調整 FullCalendar 的樣式，使其符合整體設計。
    3.  確保所有互動（點擊、拖放、刪除）都能正確地與後端通訊並更新畫面。

---

## 9. 未來可擴充功能

- **週期性行程**: 支援建立每天、每週、每月重複的行程。
- **提醒功能**: 透過瀏覽器通知在行程開始前提醒使用者。
- **標籤與分類**: 允許使用者為行程加上標籤（如「工作」、「個人」），並進行篩選。
- **資料匯出/匯入**: 提供將日曆資料匯出成 `.ics` 格式或從中匯入的功能。
