<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <VCalendar 
      expanded 
      :attributes="attributes"
      @dayclick="handleDayClick"
    />
    
    <div v-if="selectedDateTasks.length > 0" class="mt-6 border-t pt-4">
      <h3 class="font-bold text-lg mb-3">
        {{ formatDate(selectedDate) }} 的行程
      </h3>
      <ul class="space-y-2">
        <li v-for="task in selectedDateTasks" :key="task.id" class="flex items-center justify-between p-2 bg-gray-50 rounded">
          <span :class="{'line-through text-gray-400': task.is_completed}">
            {{ formatTime(task.due_date) }} - {{ task.title }}
          </span>
           <button @click="deleteTask(task.id)" class="text-red-400 hover:text-red-600">刪除</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { parseISO, isSameDay, format } from 'date-fns';
import { zhTW } from 'date-fns/locale';
import api from '../api';

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update-needed']);

const selectedDate = ref(new Date());

const attributes = computed(() => {
  return [
    // 標記今天的樣式
    {
      key: 'today',
      highlight: {
        color: 'purple',
        fillMode: 'outline',
      },
      dates: new Date(),
    },
    // 將所有任務標記在日曆上
    ...props.tasks
      .filter(t => t.due_date)
      .map(t => ({
        key: t.id,
        dot: t.is_completed ? 'gray' : 'red',
        dates: parseISO(t.due_date),
        popover: {
          label: t.title,
        },
        customData: t
      }))
  ];
});

const selectedDateTasks = computed(() => {
  if (!selectedDate.value) return [];
  return props.tasks.filter(t => 
    t.due_date && isSameDay(parseISO(t.due_date), selectedDate.value)
  );
});

const handleDayClick = (day) => {
  selectedDate.value = day.date;
};

const deleteTask = async (id) => {
  if (!confirm('確定刪除？')) return;
  await api.deleteTask(id);
  emit('update-needed');
};

const formatDate = (date) => format(date, 'yyyy/MM/dd', { locale: zhTW });
const formatTime = (iso) => format(parseISO(iso), 'HH:mm');
</script>
