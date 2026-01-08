<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const API_URL = 'http://localhost:5000/api'

interface Event {
  id: string
  title: string
  description: string
  start: string
  end: string | null
  allDay: boolean
  status: string
}

const events = ref<Event[]>([])
const router = useRouter()

// Fetch all events from the backend
const fetchEvents = async () => {
  try {
    const response = await axios.get(`${API_URL}/events`)
    events.value = response.data
  } catch (error) {
    console.error('Error fetching events for board:', error)
  }
}

// Go back to the calendar view
const goToCalendar = () => {
  router.push('/')
}

onMounted(() => {
  fetchEvents()
})
</script>

<template>
  <div class="board-container">
    <div class="board-header">
      <h1>Event Board</h1>
      <button @click="goToCalendar" class="btn-back">Back to Calendar</button>
    </div>
    <div class="event-list">
      <div v-for="event in events" :key="event.id" class="event-card">
        <h4 class="card-title">{{ event.title }}</h4>
        <p class="card-description">{{ event.description }}</p>
        <p class="card-status">Status: {{ event.status || 'Unknown' }}</p>
        <p class="card-date">{{ new Date(event.start).toLocaleDateString() }}</p>
      </div>
      <p v-if="events.length === 0">No events to display on the board.</p>
    </div>
  </div>
</template>

<style scoped>
.board-container {
  padding: 2rem;
  font-family: sans-serif;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.btn-back {
  padding: 0.5rem 1rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.event-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  flex-grow: 1;
}

.event-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-title {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.2rem;
  color: #333;
}

.card-description {
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 1rem;
}

.card-status {
  font-size: 0.9rem;
  color: #888;
  font-style: italic;
}

.card-date {
  font-size: 0.85rem;
  color: #666;
  text-align: right;
  margin-top: auto; /* Pushes date to the bottom */
}
</style>
