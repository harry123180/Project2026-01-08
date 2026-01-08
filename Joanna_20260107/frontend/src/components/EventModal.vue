<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { PropType } from 'vue'

// Define the structure of an event object for clarity
interface EventData {
  id: string | null
  title: string
  description: string
  start_time: string
  end_time: string
  is_all_day: boolean
  status: string // Add status field
}

// --- Props and Emits ---

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  event: {
    type: Object as PropType<EventData | null>,
    default: null,
  },
})

const emit = defineEmits(['save', 'delete', 'close'])

// --- Component State ---

// Use a local ref to hold the form data, initialized with a default structure
const localEvent = ref<EventData>({
  id: null,
  title: '',
  description: '',
  start_time: '',
  end_time: '',
  is_all_day: false,
  status: 'Unknown', // Default status for new events in the modal
})

const availableStatuses = ['To Do', 'In Progress', 'Done', 'Unknown']

// --- Watchers ---

// When the event prop changes, update the local copy for the form
watch(
  () => props.event,
  (newEvent) => {
    if (newEvent) {
      localEvent.value = { ...newEvent }
    } else {
      // Reset to default if no event is passed (for new event creation)
      localEvent.value = {
        id: null,
        title: '',
        description: '',
        start_time: '',
        end_time: '',
        is_all_day: false,
      }
    }
  },
  { immediate: true, deep: true }
)

// --- Computed Properties ---

// Computed property to determine if this is a new event or an existing one
const isNewEvent = computed(() => !localEvent.value.id)

// Helper to format dates for datetime-local input, which needs YYYY-MM-DDTHH:mm
const formatDateTimeForInput = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  // Adjust for timezone offset to display local time correctly in the input
  const timezoneOffset = date.getTimezoneOffset() * 60000;
  const localDate = new Date(date.getTime() - timezoneOffset);
  return localDate.toISOString().slice(0, 16);
}

const startTimeForInput = computed({
  get: () => formatDateTimeForInput(localEvent.value.start_time),
  set: (val) => { localEvent.value.start_time = new Date(val).toISOString() }
})

const endTimeForInput = computed({
  get: () => formatDateTimeForInput(localEvent.value.end_time),
  set: (val) => { localEvent.value.end_time = new Date(val).toISOString() }
})


// --- Event Handlers ---

function handleSave() {
  if (!localEvent.value.title) {
    alert('Title is required.')
    return
  }
  emit('save', localEvent.value)
}

function handleDelete() {
  if (localEvent.value.id) {
    emit('delete', localEvent.value.id)
  }
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <h2 class="modal-title">{{ isNewEvent ? 'Create Event' : 'Edit Event' }}</h2>
      
      <form @submit.prevent="handleSave">
        <div class="form-group">
          <label for="title">Title</label>
          <input id="title" v-model="localEvent.title" type="text" required />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea id="description" v-model="localEvent.description"></textarea>
        </div>

        <div class="form-group">
          <label for="start_time">Start Time</label>
          <input id="start_time" v-model="startTimeForInput" type="datetime-local" required />
        </div>

        <div class="form-group">
          <label for="end_time">End Time</label>
          <input id="end_time" v-model="endTimeForInput" type="datetime-local" />
        </div>

        <div class="form-group checkbox-group">
          <input id="is_all_day" v-model="localEvent.is_all_day" type="checkbox" />
          <label for="is_all_day">All-day event</label>
        </div>

        <div class="form-group">
          <label for="status">Status</label>
          <select id="status" v-model="localEvent.status">
            <option v-for="statusOption in availableStatuses" :key="statusOption" :value="statusOption">
              {{ statusOption }}
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="submit" class="btn btn-primary">Save</button>
          <button v-if="!isNewEvent" type="button" @click="handleDelete" class="btn btn-danger">Delete</button>
          <button type="button" @click="handleClose" class="btn btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.modal-title {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group input[type="datetime-local"],
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* Important for padding and width */
  font-size: 1rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-group input {
  margin-right: 0.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  font-weight: bold;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
</style>
