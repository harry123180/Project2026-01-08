<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'

// --- 狀態管理 ---
const events = ref([])
const showAddModal = ref(false)
const showDetailModal = ref(false)
const calendarRef = ref(null)

// 編輯/新增表單資料
const form = ref({
  title: '',
  start_time: '',
  description: '',
  color: '#3b82f6'
})

// 選中的行程 (用於查看詳情)
const selectedEvent = ref(null)

// API 路徑
const API_URL = '/api/events'

// --- FullCalendar 設定 ---
const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,listMonth'
  },
  locale: 'zh-tw',
  editable: true, // 啟用拖曳與縮放
  selectable: true,
  events: [], 
  
  // 點擊行程 -> 開啟詳情
  eventClick: (info) => {
    selectedEvent.value = {
      id: info.event.id,
      title: info.event.title,
      start: info.event.start,
      end: info.event.end,
      description: info.event.extendedProps.description,
      color: info.event.backgroundColor
    }
    showDetailModal.value = true
  },

  // 拖曳行程 -> 更新時間
  eventDrop: handleEventChange,
  
  // 拉長/縮短行程 -> 更新時間
  eventResize: handleEventChange,

  // 點擊空白處 -> 快速新增 (可選)
  dateClick: (info) => {
    // 預填點擊的日期
    const dateStr = info.dateStr + 'T09:00'
    form.value = { title: '', start_time: dateStr, description: '', color: '#3b82f6' }
    showAddModal.value = true
  }
})

// --- API 互動邏輯 ---

// 讀取所有行程
const fetchEvents = () => {
  axios.get(API_URL).then(res => {
    events.value = res.data
    // 轉換成 FullCalendar 需要的格式
    const calendarEvents = res.data.map(e => ({
      id: e.id,
      title: e.title,
      start: e.start_time,
      end: e.end_time,
      description: e.description,
      backgroundColor: e.color,
      borderColor: e.color
    }))
    calendarOptions.value.events = calendarEvents
  }).catch(err => console.error("無法讀取行程", err))
}

// 新增行程
const saveEvent = () => {
  if (!form.value.title) {
    alert('請填寫標題')
    return
  }
  
  axios.post(API_URL, form.value).then(() => {
    showAddModal.value = false
    // 清空表單
    form.value = { title: '', start_time: '', description: '', color: '#3b82f6' }
    fetchEvents()
  }).catch(err => alert('新增失敗: ' + err.message))
}

// 更新行程 (拖曳或縮放時觸發)
function handleEventChange(info) {
  const event = info.event
  const payload = {
    start_time: event.start?.toISOString(),
    end_time: event.end?.toISOString()
  }
  
  axios.put(`${API_URL}/${event.id}`, payload)
    .then(() => {
        console.log('時間更新成功')
        fetchEvents() // 同步右側清單
    })
    .catch(err => {
      alert('更新失敗，將還原操作')
      info.revert()
    })
}

// 刪除行程
const deleteEvent = () => {
  if(!selectedEvent.value) return
  if(!confirm(`確定要刪除「${selectedEvent.value.title}」嗎？`)) return

  axios.delete(`${API_URL}/${selectedEvent.value.id}`)
    .then(() => {
      showDetailModal.value = false
      selectedEvent.value = null
      fetchEvents()
    })
    .catch(err => alert('刪除失敗'))
}

// 標記完成 (簡單實作: 更新標題或顏色，這裡示範更新顏色變灰)
const toggleComplete = () => {
    if(!selectedEvent.value) return
    axios.put(`${API_URL}/${selectedEvent.value.id}`, {
        color: '#9ca3af', // 灰色
        title: '(已完成) ' + selectedEvent.value.title
    }).then(() => {
        showDetailModal.value = false
        fetchEvents()
    })
}

// --- 工具函式 ---
const formatTime = (isoString) => {
  if(!isoString) return ''
  return new Date(isoString).toLocaleString('zh-TW', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const openAddModal = () => {
    const now = new Date()
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset()) // 修正時區
    form.value = { 
        title: '', 
        start_time: now.toISOString().slice(0, 16), 
        description: '', 
        color: '#3b82f6' 
    }
    showAddModal.value = true
}

onMounted(() => {
  fetchEvents()
})
</script>

<template>
  <div class="container mx-auto p-4 lg:p-8 h-screen flex flex-col">
    <!-- Header -->
    <header class="mb-6 flex justify-between items-center flex-shrink-0">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 tracking-tight">My Schedule</h1>
        <p class="text-slate-500 text-sm">拖曳可調整時間，點擊可查看詳情</p>
      </div>
      <button @click="openAddModal" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg shadow-md transition font-medium flex items-center gap-2">
        <span class="text-xl leading-none">+</span> 新增行程
      </button>
    </header>

    <div class="flex-grow grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden">
      <!-- 左側日曆區 (佔 3/4) -->
      <div class="lg:col-span-3 bg-white p-4 rounded-xl shadow-sm border border-slate-200 overflow-auto h-full">
        <FullCalendar ref="calendarRef" :options="calendarOptions" class="h-full" />
      </div>

      <!-- 右側清單區 (佔 1/4) -->
      <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-full">
        <h2 class="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span>📅</span> 近期任務
        </h2>
        
        <div class="overflow-y-auto flex-grow pr-2 space-y-3">
            <div v-if="events.length === 0" class="text-center text-slate-400 py-10">
                <p>目前沒有行程</p>
                <p class="text-sm mt-1">點擊「新增行程」開始規劃</p>
            </div>
            
            <div v-for="event in events" :key="event.id" 
                 class="group p-3 bg-slate-50 hover:bg-slate-100 rounded-lg border-l-4 transition cursor-pointer" 
                 :style="{ borderColor: event.color }"
                 @click="selectedEvent = { ...event, start: event.start_time }; showDetailModal = true">
                <div class="font-medium text-slate-800 group-hover:text-blue-700 transition">{{ event.title }}</div>
                <div class="text-xs text-slate-500 mt-1 flex justify-between">
                    <span>{{ formatTime(event.start_time) }}</span>
                </div>
            </div>
        </div>
      </div>
    </div>

    <!-- Modal 1: 新增行程 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all scale-100">
        <div class="p-6">
          <h3 class="text-xl font-bold mb-4 text-slate-800">新增行程</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">標題</label>
              <input v-model="form.title" type="text" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="輸入行程名稱..." autofocus>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">顏色標籤</label>
              <div class="flex gap-2">
                  <button v-for="c in ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']" :key="c"
                    @click="form.color = c"
                    class="w-6 h-6 rounded-full border-2 transition"
                    :class="form.color === c ? 'border-slate-600 scale-110' : 'border-transparent'"
                    :style="{ backgroundColor: c }">
                  </button>
              </div>
            </div>
            <div class="grid grid-cols-1 gap-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">開始時間</label>
                    <input v-model="form.start_time" type="datetime-local" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">詳細內容</label>
              <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none" placeholder="備註..."></textarea>
            </div>
          </div>
        </div>
        <div class="bg-slate-50 px-6 py-4 flex justify-end gap-3 border-t">
          <button @click="showAddModal = false" class="px-4 py-2 text-slate-600 hover:bg-slate-200 rounded-lg transition font-medium">取消</button>
          <button @click="saveEvent" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-md transition font-medium">儲存</button>
        </div>
      </div>
    </div>

    <!-- Modal 2: 查看/編輯詳情 -->
    <div v-if="showDetailModal && selectedEvent" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden border-t-8" :style="{ borderColor: selectedEvent.color || selectedEvent.backgroundColor }">
            <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-2xl font-bold text-slate-800">{{ selectedEvent.title }}</h3>
                    <button @click="showDetailModal = false" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
                </div>
                
                <div class="space-y-4 text-slate-600">
                    <div class="flex items-center gap-2 text-sm">
                        <span class="bg-slate-100 px-2 py-1 rounded">🕒 開始：{{ formatTime(selectedEvent.start || selectedEvent.start_time) }}</span>
                    </div>
                    
                    <div class="bg-slate-50 p-3 rounded-lg border border-slate-100 min-h-[80px]">
                        <p class="whitespace-pre-wrap">{{ selectedEvent.description || '無詳細內容' }}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-slate-50 px-6 py-4 flex justify-between border-t">
                <button @click="deleteEvent" class="text-red-500 hover:bg-red-50 px-3 py-2 rounded-lg transition font-medium flex items-center gap-1">
                    🗑️ 刪除
                </button>
                <div class="flex gap-2">
                    <button @click="toggleComplete" class="text-green-600 hover:bg-green-50 px-3 py-2 rounded-lg transition font-medium">
                        ✓ 標記完成
                    </button>
                    <button @click="showDetailModal = false" class="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded-lg transition font-medium">
                        關閉
                    </button>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<style>
/* 讓日曆充滿容器 */
.fc { height: 100%; }
.fc-toolbar-title { font-size: 1.25rem !important; }
.fc-button { text-transform: capitalize; }
</style>