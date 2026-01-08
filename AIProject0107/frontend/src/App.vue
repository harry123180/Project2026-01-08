<template>
  <div id="app" class="p-8 bg-gray-100 min-h-screen">
    <header class="mb-8">
      <h1 class="text-4xl font-bold text-gray-800">個人行程管理</h1>
      <p class="text-gray-600">使用 Vue.js, Flask, 和 FullCalendar 來管理您的行程</p>
    </header>
    <main>
      <!-- 加上 :key 來讓 Vue 可以在 key 改變時重新渲染組件 -->
      <CalendarView 
        :key="calendarKey" 
        @add-task="showAddTaskForm"
        @edit-task="showEditTaskForm" 
      />
    </main>

    <!-- TaskForm 會在 isFormVisible 為 true 時顯示 -->
    <TaskForm 
      v-if="isFormVisible" 
      :initial-task="editingTask"
      @close="closeForm"
      @save="handleSaveTask"
      @delete="handleDeleteTask"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CalendarView from './components/CalendarView.vue';
import TaskForm from './components/TaskForm.vue';

const isFormVisible = ref(false);
const calendarKey = ref(0); // 用於刷新日曆的 key
const editingTask = ref(null); // 儲存正在編輯的 task

const showAddTaskForm = () => {
  editingTask.value = null; // 確保是新增模式
  isFormVisible.value = true;
};

const showEditTaskForm = (task) => {
  editingTask.value = task; // 設置正在編輯的 task
  isFormVisible.value = true;
};

const closeForm = () => {
  isFormVisible.value = false;
  editingTask.value = null; // 清除正在編輯的 task
};

const forceRerenderCalendar = () => {
  calendarKey.value += 1;
};

const handleSaveTask = (taskData) => {
  const isEditMode = !!editingTask.value;
  const url = isEditMode 
    ? `http://localhost:5000/api/tasks/${editingTask.value.id}` 
    : 'http://localhost:5000/api/tasks';
  
  const method = isEditMode ? 'PUT' : 'POST';

  fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(taskData),
  })
  .then(response => {
    if (!response.ok) throw new Error('儲存失敗');
    return response.json();
  })
  .then(data => {
    console.log('Successfully saved:', data);
    closeForm();
    forceRerenderCalendar(); // 儲存成功後，強制刷新日曆
  })
  .catch((error) => {
    console.error('Error:', error);
  });
};

const handleDeleteTask = (taskId) => {
  fetch(`http://localhost:5000/api/tasks/${taskId}`, {
    method: 'DELETE',
  })
  .then(response => {
    if (!response.ok) throw new Error('刪除失敗');
    return response.json();
  })
  .then(data => {
    console.log('Successfully deleted:', data);
    closeForm();
    forceRerenderCalendar(); // 刪除成功後，強制刷新日曆
  })
  .catch((error) => {
    console.error('Error:', error);
  });
};
</script>

<style>
body {
  font-family: sans-serif;
}
</style>
