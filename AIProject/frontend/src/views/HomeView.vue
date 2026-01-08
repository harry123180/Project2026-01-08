<template>
  <div class="todo-container glass-card p-4 p-md-5">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1"><i class="fas fa-check-double text-primary me-2"></i>待辦清單</h2>
        <p class="text-muted mb-0 small">{{ currentDate }}</p>
      </div>
      <div>
        <button class="btn btn-outline-danger btn-sm me-2" @click="clearCompleted" v-if="hasCompleted" title="清除已完成">
          <i class="fas fa-trash-alt"></i> 清除已完成
        </button>
        <button class="btn btn-success btn-sm" @click="exportSchedule" title="匯出行程">
          <i class="fas fa-file-export"></i> 匯出
        </button>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="progress mb-4" style="height: 10px; border-radius: 5px;">
      <div class="progress-bar bg-gradient-primary" role="progressbar" 
           :style="{ width: progressPercentage + '%' }" 
           :aria-valuenow="progressPercentage" aria-valuemin="0" aria-valuemax="100">
      </div>
    </div>

    <!-- Input Area -->
    <div class="card border-0 shadow-sm mb-4 input-area">
      <div class="card-body p-2">
        <div class="row g-2 align-items-center">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white border-0"><i class="fas fa-pen text-muted"></i></span>
              <input type="text" v-model="newTodo" @keyup.enter="addTodo" class="form-control border-0" placeholder="想做些什麼？">
            </div>
          </div>
          <div class="col-md-3">
             <div class="input-group">
              <span class="input-group-text bg-white border-0"><i class="far fa-calendar-alt text-muted"></i></span>
              <input type="date" v-model="newDueDate" class="form-control border-0">
            </div>
          </div>
          <div class="col-md-2">
            <select v-model="newTaskType" class="form-select border-0 bg-light">
              <option value="work">💼 工作</option>
              <option value="meeting">📅 會議</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary w-100 rounded-pill fw-bold" @click="addTodo">
              <i class="fas fa-plus"></i> 新增
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Todo List with Transitions -->
    <ul class="list-group list-group-flush">
      <TransitionGroup name="list">
        <li v-for="todo in sortedTodos" :key="todo.id" class="list-group-item todo-item mb-2 rounded border-0 shadow-sm">
          <div class="d-flex align-items-center justify-content-between p-2">
            
            <div class="d-flex align-items-center flex-grow-1">
              <!-- Checkbox -->
              <div class="form-check m-0">
                <input class="form-check-input custom-checkbox" type="checkbox" :checked="todo.done" @change="toggleTodo(todo)">
              </div>
              
              <!-- Content -->
              <div class="ms-3 flex-grow-1" :class="{ 'done-text': todo.done }">
                <div class="d-flex align-items-center">
                  <span class="badge rounded-pill me-2" 
                        :class="todo.task_type === 'meeting' ? 'bg-success-subtle text-success' : 'bg-primary-subtle text-primary'">
                    {{ todo.task_type === 'meeting' ? '會議' : '工作' }}
                  </span>
                  <span class="fw-medium todo-content">{{ todo.content }}</span>
                </div>
                <div class="small text-muted mt-1" v-if="todo.due_date">
                  <i class="far fa-clock me-1"></i> {{ todo.due_date }}
                </div>
              </div>
            </div>

            <!-- Delete Action -->
            <button class="btn btn-link text-danger delete-btn" @click="deleteTodo(todo.id)">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </li>
      </TransitionGroup>
    </ul>

    <!-- Empty State -->
    <div v-if="todos.length === 0" class="text-center py-5">
      <div class="mb-3">
        <i class="fas fa-clipboard-check fa-4x text-light"></i>
      </div>
      <h5 class="text-muted">太棒了！目前沒有待辦事項</h5>
      <p class="text-secondary small">享受你的自由時間，或是新增一個挑戰吧！</p>
    </div>
    
    <div class="text-center mt-4">
        <router-link to="/schedule" class="btn btn-link text-decoration-none">
          查看行程日曆 <i class="fas fa-arrow-right ms-1"></i>
        </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const API_BASE = '/api';
const todos = ref([]);
const newTodo = ref('');
const newDueDate = ref('');
const newTaskType = ref('work');

// Formatted Date for Header
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
});

// Progress Calculation
const progressPercentage = computed(() => {
  if (todos.value.length === 0) return 0;
  const completed = todos.value.filter(t => t.done).length;
  return Math.round((completed / todos.value.length) * 100);
});

const hasCompleted = computed(() => {
  return todos.value.some(t => t.done);
});

// Sort: Pending first, then by date
const sortedTodos = computed(() => {
  return [...todos.value].sort((a, b) => {
    if (a.done === b.done) {
        // If both done or both pending, sort by date
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date) - new Date(b.due_date);
    }
    return a.done ? 1 : -1; // Done items go to bottom
  });
});

const fetchTodos = async () => {
  const res = await axios.get(`${API_BASE}/todos`);
  todos.value = res.data;
};

const addTodo = async () => {
  if (!newTodo.value.trim()) return;
  const payload = {
    content: newTodo.value,
    due_date: newDueDate.value || null,
    task_type: newTaskType.value
  };
  const res = await axios.post(`${API_BASE}/todos`, payload);
  todos.value.push(res.data);
  newTodo.value = '';
  // Keep date/type for continuous entry or clear? Let's clear date, keep type
  newDueDate.value = '';
};

const toggleTodo = async (todo) => {
  // Optimistic update
  todo.done = !todo.done;
  try {
    await axios.put(`${API_BASE}/todos/${todo.id}`, { done: todo.done });
  } catch (e) {
    todo.done = !todo.done; // Revert on error
    console.error(e);
  }
};

const deleteTodo = async (id) => {
  await axios.delete(`${API_BASE}/todos/${id}`);
  todos.value = todos.value.filter(t => t.id !== id);
};

const clearCompleted = async () => {
  if (!confirm("確定要刪除所有已完成的任務嗎？")) return;
  await axios.delete(`${API_BASE}/todos/completed`);
  todos.value = todos.value.filter(t => !t.done);
};

const exportSchedule = async () => {
  const res = await axios.post(`${API_BASE}/export_md`);
  alert(`行程已匯出至 ${res.data.filename}`);
};

onMounted(fetchTodos);
</script>

<style scoped>
.todo-container {
  max-width: 700px;
  margin: 40px auto;
}

.bg-gradient-primary {
  background: linear-gradient(90deg, #4e54c8, #8f94fb);
}

.input-area {
  transition: transform 0.2s;
}
.input-area:focus-within {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.todo-item {
  transition: all 0.2s ease;
  background: white;
  margin-bottom: 8px;
}
.todo-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

.custom-checkbox {
  width: 1.2em;
  height: 1.2em;
  cursor: pointer;
}

.done-text {
  opacity: 0.5;
  text-decoration: line-through;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}
.todo-item:hover .delete-btn {
  opacity: 1;
}

.bg-success-subtle { background-color: #d1e7dd; }
.bg-primary-subtle { background-color: #cfe2ff; }
</style>