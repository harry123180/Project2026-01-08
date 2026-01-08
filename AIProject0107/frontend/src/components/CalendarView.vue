<template>
  <div>
    <FullCalendar :options="calendarOptions" />
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue' // 引入 ref 和 defineEmits
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'

// 定義這個組件會發出的事件
const emit = defineEmits(['add-task', 'edit-task']);

// 使用 ref 來創建響應式的 calendarOptions
const calendarOptions = ref({
  plugins: [ dayGridPlugin, interactionPlugin ],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'addTaskButton dayGridMonth,dayGridWeek,dayGridDay' // 加入自訂按鈕
  },

  // 自訂按鈕
  customButtons: {
    addTaskButton: {
      text: '新增行程',
      click: () => {
        emit('add-task'); // 當按鈕被點擊時，發出 add-task 事件
      }
    }
  },
  
  // events 函式來動態獲取資料
  events: (fetchInfo, successCallback, failureCallback) => {
    const startDate = fetchInfo.start.toISOString().split('T')[0];
    const endDate = fetchInfo.end.toISOString().split('T')[0];

    fetch(`http://localhost:5000/api/tasks?start=${startDate}&end=${endDate}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        const events = data.map(task => ({
          id: task.id,
          title: task.title,
          start: task.start_time,
          end: task.end_time,
          backgroundColor: task.completed ? 'grey' : '#3788d8',
          borderColor: task.completed ? 'grey' : '#3788d8',
          // 將原始 task 資料存起來，方便點擊時取用
          extendedProps: {
            ...task
          }
        }));
        successCallback(events);
      })
      .catch(error => {
        console.error('Error fetching tasks:', error);
        failureCallback(error);
      });
  },

  editable: true,
  selectable: true,

  // 點擊事件
  eventClick: (info) => {
    info.jsEvent.preventDefault(); // 阻止瀏覽器預設行為
    // 發出 edit-task 事件，並附上完整的 task 資料
    emit('edit-task', info.event.extendedProps);
  },

  // 拖曳事件
  eventDrop: (info) => {
    handleEventDrop(info.event);
  },
});

const handleEventDrop = (event) => {
  const updatedTask = {
    start_time: event.start.toISOString(),
    end_time: event.end ? event.end.toISOString() : null,
  };

  fetch(`http://localhost:5000/api/tasks/${event.id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updatedTask),
  })
  .then(response => {
    if (!response.ok) throw new Error('更新失敗');
    return response.json();
  })
  .then(data => {
    console.log('Successfully updated via drag:', data);
  })
  .catch(error => {
    console.error('Error updating event:', error);
    // 如果 API 更新失敗，將事件還原到原始位置
    info.revert();
  });
};
</script>

<style>
/* 樣式已移至 main.js，此處保持空白或移除 */
</style>