<template>
  <!-- 我們將使用一個固定的覆蓋層來顯示表單 -->
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
    <div class="relative mx-auto p-8 border w-full max-w-lg shadow-lg rounded-md bg-white">
      <h3 class="text-2xl font-bold mb-6">{{ formTitle }}</h3>
      
      <form @submit.prevent="handleSubmit">
        <!-- 標題 -->
        <div class="mb-4">
          <label for="title" class="block text-gray-700 text-sm font-bold mb-2">標題 / 工作內容</label>
          <input type="text" id="title" v-model="task.title" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required>
        </div>
        
        <!-- 客戶名稱 -->
        <div class="mb-4">
          <label for="client_name" class="block text-gray-700 text-sm font-bold mb-2">相關客戶 (可選)</label>
          <input type="text" id="client_name" v-model="task.client_name" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
        </div>
        
        <!-- 開始時間 -->
        <div class="mb-4">
          <label for="start_time" class="block text-gray-700 text-sm font-bold mb-2">開始時間</label>
          <input type="datetime-local" id="start_time" v-model="task.start_time" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required>
        </div>

        <!-- 結束時間 -->
        <div class="mb-6">
          <label for="end_time" class="block text-gray-700 text-sm font-bold mb-2">結束時間 (可選)</label>
          <input type="datetime-local" id="end_time" v-model="task.end_time" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
        </div>

        <!-- 按鈕 -->
        <div class="flex items-center justify-between">
          <div>
            <!-- 只有在編輯模式時才顯示刪除按鈕 -->
            <button v-if="isEditMode" type="button" @click="handleDelete" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
              刪除
            </button>
          </div>
          <div class="space-x-4">
            <button type="button" @click="$emit('close')" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
              取消
            </button>
            <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
              儲存
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  initialTask: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'save', 'delete']);

const isEditMode = computed(() => !!props.initialTask);
const formTitle = computed(() => isEditMode.value ? '編輯行程' : '新增行程');

const task = ref({
  id: props.initialTask?.id || null,
  title: props.initialTask?.title || '',
  client_name: props.initialTask?.client_name || '',
  start_time: props.initialTask?.start_time ? props.initialTask.start_time.slice(0, 16) : '',
  end_time: props.initialTask?.end_time ? props.initialTask.end_time.slice(0, 16) : '',
});

const handleSubmit = () => {
  emit('save', { ...task.value });
};

const handleDelete = () => {
  if (confirm('您確定要刪除這個行程嗎？')) {
    emit('delete', task.value.id);
  }
};
</script>
