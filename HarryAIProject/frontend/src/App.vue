<template>
  <div class="min-h-screen bg-gray-100 p-4 md:p-8">
    <header class="max-w-6xl mx-auto mb-8 flex flex-col md:flex-row justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-800 mb-4 md:mb-0">
        🚀 Harry's Schedule
      </h1>
      <div class="flex space-x-4">
        <button 
          @click="currentView = 'dashboard'"
          :class="currentView === 'dashboard' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700'"
          class="px-4 py-2 rounded-lg shadow-sm font-medium transition-colors"
        >
          看板視圖
        </button>
        <button 
          @click="currentView = 'calendar'"
          :class="currentView === 'calendar' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700'"
          class="px-4 py-2 rounded-lg shadow-sm font-medium transition-colors"
        >
          日曆視圖
        </button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-8">
      <!-- 左側：新增表單 -->
      <div class="lg:col-span-1">
        <TaskForm @task-added="fetchTasks" />
        
        <!-- 簡易統計 -->
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="font-bold text-gray-600 mb-2">統計</h3>
          <p class="text-sm text-gray-500">待辦事項: {{ activeTasksCount }}</p>
          <p class="text-sm text-gray-500">已完成: {{ completedTasksCount }}</p>
        </div>
      </div>

      <!-- 右側：主要視圖 -->
      <div class="lg:col-span-3">
        <component 
          :is="currentView === 'dashboard' ? Dashboard : CalendarView" 
          :tasks="tasks"
          @update-needed="fetchTasks"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from './api';
import TaskForm from './components/TaskForm.vue';
import Dashboard from './components/Dashboard.vue';
import CalendarView from './components/CalendarView.vue';

const tasks = ref([]);
const currentView = ref('dashboard');

const fetchTasks = async () => {
  try {
    const res = await api.getTasks();
    tasks.value = res.data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
  }
};

const activeTasksCount = computed(() => tasks.value.filter(t => !t.is_completed).length);
const completedTasksCount = computed(() => tasks.value.filter(t => t.is_completed).length);

onMounted(() => {
  fetchTasks();
});
</script>
