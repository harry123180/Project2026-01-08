# 專案規劃：個人日程管理與待辦事項系統 (Personal Schedule & To-Do App)

這是一份構建前後端分離日程管理應用程式的開發計畫。

## 1. 專案背景與目標 (Context & Goals)

*   **目標對象:** 個人使用 (Single User)。
*   **核心動機:**
    *   工作事務繁雜，容易遺忘，需要外部大腦輔助記憶。
    *   需要記錄詳細的會議時間與工作內容，而不僅僅是標題。
*   **關鍵功能:**
    *   **日曆看板 (Calendar Dashboard):** 視覺化呈現每日、每週行程。
    *   **詳細記錄:** 支援長篇幅的工作內容描述。
    *   **時間管理:** 明確的開始時間與截止時間。

## 2. 技術堆疊 (Tech Stack)

*   **前端 (Frontend):**
    *   **框架:** Vue.js 3 (Composition API)
    *   **日曆套件:** FullCalendar (Vue adapter) 或 V-Calendar (用於日曆視圖)
    *   **HTTP 客戶端:** Axios
    *   **UI 框架:** Tailwind CSS (建議，方便快速刻出好看的看板介面)
*   **後端 (Backend):**
    *   **框架:** Python Flask
    *   **ORM:** Flask-SQLAlchemy
    *   **跨域處理:** Flask-CORS
*   **資料庫 (Database):**
    *   **類型:** SQLite (輕量級、單一檔案，適合個人使用)

## 3. 專案結構 (Project Structure)

```text
schedule-app/
├── backend/                # 後端 API
│   ├── app.py              # Flask 應用入口
│   ├── models.py           # 資料庫模型 (DB Schema)
│   ├── routes.py           # API 路由邏輯 (Controller)
│   └── todo.db             # SQLite 資料庫
└── frontend/               # 前端 Vue 應用
    ├── src/
    │   ├── components/
    │   │   ├── CalendarView.vue  # 日曆視圖組件
    │   │   ├── TaskForm.vue      # 新增/編輯任務表單
    │   │   └── TaskList.vue      # 清單視圖組件
    │   ├── views/
    │   │   └── Dashboard.vue     # 主看板頁面
    │   └── ...
    └── ...
```

## 4. 資料庫設計 (Database Schema)

**Table Name:** `event` (改名為 event 更符合行程管理概念)

| 欄位名稱      | 類型      | 描述                       |
| :------------ | :-------- | :------------------------- |
| `id`          | Integer   | Primary Key                |
| `title`       | String    | 行程標題 (如：專案會議)    |
| `description` | Text      | 詳細工作內容、備註         |
| `start_time`  | DateTime  | 開始時間 (支援日曆顯示)    |
| `end_time`    | DateTime  | 結束時間 (選填)            |
| `is_completed`| Boolean   | 是否已完成                 |
| `color`       | String    | 標籤顏色 (選填，用於區分緊急程度) |

## 5. API 接口設計 (API Endpoints)

所有 API 前綴為 `/api`。

| 方法   | 路徑           | 描述                 | Request Body 範例 |
| :----- | :------------- | :------------------- | :---------------- |
| GET    | `/events`      | 取得所有行程 (可篩選日期範圍) | `?start=2023-10-01&end=2023-10-31` |
| POST   | `/events`      | 新增行程/待辦        | `{"title": "會議", "start_time": "2023-10-10 14:00", "description": "討論Q4財報"}` |
| PUT    | `/events/<id>` | 更新行程 (拖拉日曆時更新時間) | `{"start_time": "2023-10-11 10:00"}` |
| DELETE | `/events/<id>` | 刪除行程             | N/A |

## 6. 開發步驟 (Roadmap)

1.  **後端基礎建設**: 
    *   建立 Flask 環境。
    *   定義 `Event` 資料庫模型 (包含時間欄位)。
    *   實作 CRUD API。
2.  **前端基礎建設**:
    *   建立 Vue 3 + Vite 專案。
    *   安裝 Tailwind CSS。
3.  **日曆整合**:
    *   安裝 FullCalendar。
    *   串接 GET `/api/events` 將資料顯示在日曆上。
4.  **詳細記錄功能**:
    *   製作彈出視窗 (Modal) 用於填寫詳細描述與時間。
    *   串接 POST 與 PUT API。
5.  **優化體驗**:
    *   支援在日曆上拖曳行程來改變時間 (Drag & Drop)。