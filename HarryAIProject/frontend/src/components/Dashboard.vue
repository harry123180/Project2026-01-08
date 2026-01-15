<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- 今天 -->
    <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
      <h3 class="text-lg font-bold text-blue-800 mb-3 flex items-center">
        <span class="mr-2">📅</span> 今天 (Today)
      </h3>
      <div v-if="todayTasks.length === 0" class="text-gray-500 text-sm text-center py-4">
        今天沒有行程 🎉
      </div>
      <div v-else class="space-y-3">
        <div v-for="task in todayTasks" :key="task.id" class="bg-white p-3 rounded shadow-sm border-l-4 border-blue-500">
          <div class="flex justify-between items-start">
            <h4 :class="{'line-through text-gray-400': task.is_completed}" class="font-medium">{{ task.title }}</h4>
            <input type="checkbox" :checked="task.is_completed" @change="toggleComplete(task)" class="mt-1 h-4 w-4 text-blue-600 rounded">
          </div>
          <p class="text-xs text-gray-500 mt-1">{{ formatTime(task.due_date) }}</p>
          <p v-if="task.description" class="text-sm text-gray-600 mt-2 whitespace-pre-line">{{ task.description }}</p>
          <button @click="deleteTask(task.id)" class="text-red-400 text-xs hover:text-red-600 mt-2">刪除</button>
        </div>
      </div>
    </div>

    <!-- 這禮拜 -->
    <div class="bg-green-50 p-4 rounded-lg border border-green-200">
      <h3 class="text-lg font-bold text-green-800 mb-3 flex items-center">
        <span class="mr-2">🗓️</span> 這禮拜 (This Week)
      </h3>
      <div v-if="weekTasks.length === 0" class="text-gray-500 text-sm text-center py-4">
        本週後續無行程
      </div>
      <div v-else class="space-y-3">
        <div v-for="task in weekTasks" :key="task.id" class="bg-white p-3 rounded shadow-sm border-l-4 border-green-500">
          <div class="flex justify-between items-start">
            <h4 :class="{'line-through text-gray-400': task.is_completed}" class="font-medium">{{ task.title }}</h4>
            <input type="checkbox" :checked="task.is_completed" @change="toggleComplete(task)" class="mt-1 h-4 w-4 text-green-600 rounded">
          </div>
          <p class="text-xs text-gray-500 mt-1">{{ formatDate(task.due_date) }}</p>
          <button @click="deleteTask(task.id)" class="text-red-400 text-xs hover:text-red-600 mt-2">刪除</button>
        </div>
      </div>
    </div>

    <!-- 下禮拜 -->
    <div class="bg-purple-50 p-4 rounded-lg border border-purple-200">
      <h3 class="text-lg font-bold text-purple-800 mb-3 flex items-center">
        <span class="mr-2">🔭</span> 下禮拜 (Next Week)
      </h3>
      <div v-if="nextWeekTasks.length === 0" class="text-gray-500 text-sm text-center py-4">
        下週尚無安排
      </div>
      <div v-else class="space-y-3">
        <div v-for="task in nextWeekTasks" :key="task.id" class="bg-white p-3 rounded shadow-sm border-l-4 border-purple-500">
          <div class="flex justify-between items-start">
            <h4 :class="{'line-through text-gray-400': task.is_completed}" class="font-medium">{{ task.title }}</h4>
            <input type="checkbox" :checked="task.is_completed" @change="toggleComplete(task)" class="mt-1 h-4 w-4 text-purple-600 rounded">
          </div>
          <p class="text-xs text-gray-500 mt-1">{{ formatDate(task.due_date) }}</p>
          <button @click="deleteTask(task.id)" class="text-red-400 text-xs hover:text-red-600 mt-2">刪除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { isToday, isThisWeek, addWeeks, isSameWeek, format, parseISO } from 'date-fns';
import { zhTW } from 'date-fns/locale';
import api from '../api';

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update-needed']);

// 過濾邏輯
const todayTasks = computed(() => {
  return props.tasks.filter(t => t.due_date && isToday(parseISO(t.due_date)));
});

const weekTasks = computed(() => {
  // 排除今天，只顯示本週剩下的
  return props.tasks.filter(t => {
    if (!t.due_date) return false;
    const date = parseISO(t.due_date);
    return isThisWeek(date, { weekStartsOn: 1 }) && !isToday(date);
  });
});

const nextWeekTasks = computed(() => {
  const nextWeekDate = addWeeks(new Date(), 1);
  return props.tasks.filter(t => {
    if (!t.due_date) return false;
    const date = parseISO(t.due_date);
    // 檢查是否與"下週的今天"處於同一週
    return isSameWeek(date, nextWeekDate, { weekStartsOn: 1 });
  });
});

// 操作方法
const toggleComplete = async (task) => {
  try {
    await api.updateTask(task.id, { is_completed: !task.is_completed });
    emit('update-needed');
  } catch (e) {
    console.error(e);
  }
};

const deleteTask = async (id) => {
  if (!confirm('確定要刪除這個行程嗎？')) return;
  try {
    await api.deleteTask(id);
    emit('update-needed');
  } catch (e) {
    console.error(e);
  }
};

// 格式化輔助
const formatTime = (isoString) => {
  return format(parseISO(isoString), 'HH:mm', { locale: zhTW });
};

const formatDate = (isoString) => {
  return format(parseISO(isoString), 'MM/dd (eee) HH:mm', { locale: zhTW });
};
</script>
