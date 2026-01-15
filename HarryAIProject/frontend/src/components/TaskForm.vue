<template>
  <div class="bg-white p-6 rounded-lg shadow-md mb-6">
    <h2 class="text-xl font-bold mb-4">新增行程</h2>
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">標題</label>
        <input 
          v-model="form.title" 
          type="text" 
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          placeholder="例如：與客戶開會"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700">預定時間</label>
        <input 
          v-model="form.due_date" 
          type="datetime-local" 
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">詳細描述</label>
        <textarea 
          v-model="form.description" 
          rows="3"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          placeholder="例如：準備簡報資料、會議室 301..."
        ></textarea>
      </div>

      <button 
        type="submit" 
        class="w-full inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        新增行程
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import api from '../api';

const emit = defineEmits(['task-added']);

const form = reactive({
  title: '',
  description: '',
  due_date: ''
});

const handleSubmit = async () => {
  try {
    // 若沒有選擇時間，後端可以接受 null，但這裡我們強制要求
    if (!form.due_date) return;

    await api.createTask({
      title: form.title,
      description: form.description,
      due_date: new Date(form.due_date).toISOString()
    });

    // 重置表單
    form.title = '';
    form.description = '';
    form.due_date = '';
    
    // 通知父組件更新列表
    emit('task-added');
  } catch (error) {
    console.error('Failed to create task:', error);
    alert('新增失敗，請檢查網路連線或輸入資料');
  }
};
</script>
