# 個人行程與待辦事項管理系統 (Personal Schedule & Todo Manager) 專案規劃書

## 1. 專案概述與動機
這是一個為個人使用者量身打造的行程管理系統。
- **核心動機**: 使用者事務繁忙，需要一個可靠的系統來記錄行程（如客戶會議）與工作內容，避免遺忘。
- **主要目的**: 提供清晰的視覺化介面，讓使用者能快速掌握「今天」、「本週」與「下週」的待辦事項與行程。
- **呈現方式**: 網頁應用程式 (Web App)。

## 2. 技術堆疊 (Tech Stack)

### 前端 (Frontend)
- **框架**: Vue.js 3 (Composition API)
- **HTTP 客戶端**: Axios
- **UI/樣式**: Tailwind CSS 或 Bootstrap (為了快速刻畫看板與日曆佈局)
- **日曆套件**: `v-calendar` 或 `FullCalendar` (視情況選用，或自行實作簡易日曆)

### 後端 (Backend)
- **框架**: Python Flask
- **ORM**: Flask-SQLAlchemy
- **跨域處理**: Flask-CORS

### 資料庫 (Database)
- **系統**: SQLite (單一檔案 `schedule.db`，方便備份與遷移)

## 3. 功能需求 (Features)

### A. 任務/行程管理 (CRUD)
- 新增行程：需包含標題、**日期時間**、詳細描述（如會議地點、議程）。
- 編輯/刪除行程。
- 標記完成：已完成的項目可歸檔或淡化顯示。

### B. 視覺化看板 (Time-based Dashboard)
首頁採用「看板」形式佈局，分為三列：
1.  **今天 (Today)**: 顯示日期為今日的行程與未完成事項。
2.  **這禮拜 (This Week)**: 顯示今日之後，但屬於本週（週一至週日）的行程。
3.  **下禮拜 (Next Week)**: 顯示下週的預定行程。

### C. 日曆視圖 (Calendar View)
- 提供月曆模式，在日期格子上顯示當天的行程摘要點。
- 點擊日期可查看當日詳細清單。

## 4. 資料庫設計 (Schema)

**Table**: `task`

| 欄位名稱      | 型別      | 描述                       |
|:-------------|:---------|:--------------------------|
| `id`         | Integer  | 主鍵 (Primary Key)         |
| `title`      | String   | 行程標題 (如: 與 A 客戶開會)|
| `description`| Text     | 詳細內容/備註               |
| `due_date`   | DateTime | **關鍵欄位**: 預定日期時間   |
| `is_completed`| Boolean | 是否已完成 (預設 False)     |
| `created_at` | DateTime | 建立時間                   |

## 5. API 設計 (RESTful)

| 方法   | 路徑           | 描述/參數範例                  | Request Body / Query Params |
|:------|:--------------|:----------------------------|:---------------------------|
| GET   | `/api/tasks`  | 取得所有行程 (可選日期範圍篩選) | `?start_date=...&end_date=...`|
| POST  | `/api/tasks`  | 新增行程                      | `{ "title": "...", "due_date": "2026-01-07 14:00", "description": "..." }` |
| PUT   | `/api/tasks/<id>`| 更新行程 (改時間、內容、狀態) | `{ "is_completed": true }`  |
| DELETE| `/api/tasks/<id>`| 刪除行程                      | N/A                        |

## 6. 專案目錄結構

```text
/AIProject
├── /backend            # Flask 後端
│   ├── app.py          # 主程式
│   ├── models.py       # 資料庫模型
│   ├── routes.py       # (可選) 若路由變多可拆分
│   └── instance/       # SQLite 檔案位置
├── /frontend           # Vue 前端
│   ├── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.vue   # 看板視圖 (今天/本週/下週)
│   │   │   ├── CalendarView.vue# 日曆視圖
│   │   │   └── TaskForm.vue    # 新增/編輯表單
│   │   ├── views/
│   │   │   └── Home.vue        # 主頁面
│   │   └── App.vue
│   └── package.json
└── project_plan.md     # 本規劃書
```

## 7. 開發步驟

1.  **後端基礎**: 建立 Flask 環境，定義包含 `due_date` 的資料庫模型，完成 API。
2.  **前端基礎**: 初始化 Vue 專案。
3.  **核心功能 - 看板**:
    - 實作 API 串接。
    - 前端邏輯：取得資料後，根據 `due_date` 篩選並分類到「今天」、「這禮拜」、「下禮拜」陣列中。
    - UI 顯示三欄式佈局。
4.  **核心功能 - 日曆**: 整合日曆組件，將資料顯示在對應日期上。
5.  **優化**: 加入「詳細描述」的輸入與顯示，美化介面。

---
*此檔案依據使用者需求（行程紀錄、看板管理）更新。*