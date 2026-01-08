<template>
  <div class="schedule-container glass-card p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0"><i class="far fa-calendar-check text-success me-2"></i>行程日曆</h2>
      <router-link to="/" class="btn btn-outline-primary rounded-pill">
        <i class="fas fa-arrow-left me-1"></i> 返回編輯
      </router-link>
    </div>

    <div class="calendar-wrapper bg-white rounded p-3 shadow-sm">
      <FullCalendar :options="calendarOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';

const API_BASE = '/api';
const todos = ref([]);

const fetchTodos = async () => {
  try {
    const res = await axios.get(`${API_BASE}/todos`);
    todos.value = res.data;
  } catch (error) {
    console.error("Failed to fetch todos:", error);
  }
};

const calendarEvents = computed(() => {
  return todos.value.map(todo => {
    let color = '#4e54c8'; // Primary theme color
    if (todo.task_type === 'meeting') {
      color = '#28a745'; 
    }
    if (todo.done) {
      color = '#6c757d'; 
    }

    return {
      id: String(todo.id),
      title: (todo.done ? '✓ ' : '') + todo.content,
      date: todo.due_date,
      backgroundColor: color,
      borderColor: color,
      classNames: todo.done ? ['event-done'] : ['event-active'],
      extendedProps: {
        type: todo.task_type,
        done: todo.done
      }
    };
  }).filter(event => event.date);
});

const handleEventClick = (info) => {
  const event = info.event;
  const status = event.extendedProps.done ? '已完成' : '未完成';
  const type = event.extendedProps.type === 'meeting' ? '會議' : '工作';
  
  // Simple view for now, could be a modal later
  alert(`【${type}】${event.title.replace('✓ ', '')}\n----------------\n狀態：${status}\n日期：${event.startStr}`);
};

const handleEventDrop = async (info) => {
  if (!confirm(`確定要將 "${info.event.title}" 移動到 ${info.event.startStr} 嗎？`)) {
    info.revert();
    return;
  }

  try {
    const newDate = info.event.startStr;
    await axios.put(`${API_BASE}/todos/${info.event.id}`, {
      due_date: newDate
    });
    // Update local state to reflect change without refetching if possible, 
    // but refetching ensures consistency.
    await fetchTodos(); 
  } catch (e) {
    console.error("Update failed", e);
    info.revert();
    alert("更新失敗，請稍後再試");
  }
};

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'zh-tw',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth'
  },
  buttonText: {
    today: '今天',
    month: '月'
  },
  events: calendarEvents.value,
  editable: true, // Enable Drag & Drop
  droppable: true,
  eventClick: handleEventClick,
  eventDrop: handleEventDrop,
  height: 'auto',
  dayMaxEvents: true 
}));

onMounted(fetchTodos);
</script>

<style scoped>
.schedule-container {
  max-width: 1000px;
  margin: 30px auto;
}

.calendar-wrapper {
  min-height: 650px;
}

/* Calendar Customization */
:deep(.fc-toolbar-title) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

:deep(.fc-button-primary) {
  background-color: #4e54c8;
  border-color: #4e54c8;
}
:deep(.fc-button-primary:hover) {
  background-color: #373b8c;
  border-color: #373b8c;
}

:deep(.fc-day-today) {
  background-color: rgba(78, 84, 200, 0.05) !important;
}

:deep(.event-done) {
  text-decoration: line-through;
  opacity: 0.6;
}
:deep(.event-active) {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
