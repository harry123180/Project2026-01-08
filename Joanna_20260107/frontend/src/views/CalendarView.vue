<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { CalendarOptions, EventApi, DateSelectArg, EventClickArg, Calendar } from '@fullcalendar/core'
import axios from 'axios'
import EventModal from '../components/EventModal.vue'

// --- Refs and State ---

const API_URL = 'http://localhost:5000/api'
const calendarRef = ref<{ getApi: () => Calendar } | null>(null)
const isModalVisible = ref(false)
const selectedEvent = ref<any>(null)
const router = useRouter()

// --- Calendar Configuration ---

const calendarOptions = ref<CalendarOptions>({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,kanban' // Added kanban button
  },
  customButtons: {
    kanban: {
      text: 'Board',
      click: () => {
        router.push('/kanban')
      }
    }
  },
  editable: true,
  selectable: true,
  weekends: true,
  events: fetchEvents,
  select: handleDateSelect,
  eventClick: handleEventClick,
  eventDrop: handleEventDrop,
  displayEventTime: false, // Prevents event times from displaying in event blocks
});

// --- API and Event Handlers ---

async function fetchEvents(fetchInfo: { start: Date; end: Date }, successCallback: (events: any[]) => void, failureCallback: (error: any) => void) {
  try {
    const { start, end } = fetchInfo
    const response = await axios.get(`${API_URL}/events`, {
      params: { start: start.toISOString(), end: end.toISOString() }
    });
    successCallback(response.data);
  } catch (error) {
    console.error('Error fetching events:', error);
    failureCallback(error);
  }
}

function handleDateSelect(selectInfo: DateSelectArg) {
  selectedEvent.value = {
    id: null,
    title: '',
    description: '',
    start_time: selectInfo.startStr,
    end_time: selectInfo.endStr,
    is_all_day: selectInfo.allDay,
    status: 'Unknown', // Default status for new events
  }
  isModalVisible.value = true
  const calendarApi = selectInfo.view.calendar;
  calendarApi.unselect();
}

function handleEventClick(clickInfo: EventClickArg) {
  selectedEvent.value = {
    id: clickInfo.event.id,
    title: clickInfo.event.title,
    description: clickInfo.event.extendedProps.description,
    start_time: clickInfo.event.startStr,
    end_time: clickInfo.event.endStr,
    is_all_day: clickInfo.event.allDay,
    status: clickInfo.event.extendedProps.status, // Add status here
  }
  isModalVisible.value = true
}

function handleEventDrop(dropInfo: { event: EventApi }) {
  const event = dropInfo.event
  const updatedEvent = {
    start_time: event.start?.toISOString(),
    end_time: event.end?.toISOString(),
    is_all_day: event.allDay,
    title: event.title,
    description: event.extendedProps.description,
  };

  axios.put(`${API_URL}/events/${event.id}`, updatedEvent)
    .catch(error => {
      console.error('Error updating event:', error);
      dropInfo.revert();
    });
}

// --- Modal Actions ---

function handleCloseModal() {
  isModalVisible.value = false
  selectedEvent.value = null
}

async function handleSaveEvent(eventData: any) {
  try {
    if (eventData.id) {
      // Update existing event
      await axios.put(`${API_URL}/events/${eventData.id}`, eventData)
    } else {
      // Create new event
      await axios.post(`${API_URL}/events`, eventData)
    }
    // Refetch events and close modal
    calendarRef.value?.getApi().refetchEvents()
    handleCloseModal()
  } catch (error) {
    console.error('Error saving event:', error)
    alert('Failed to save event. See console for details.')
  }
}

async function handleDeleteEvent(eventId: string) {
  if (confirm('Are you sure you want to delete this event?')) {
    try {
      await axios.delete(`${API_URL}/events/${eventId}`)
      calendarRef.value?.getApi().refetchEvents()
      handleCloseModal()
    } catch (error) {
      console.error('Error deleting event:', error)
      alert('Failed to delete event. See console for details.')
    }
  }
}

</script>

<template>
  <div class="calendar-container">
    <FullCalendar ref="calendarRef" :options="calendarOptions" />
    <EventModal
      :visible="isModalVisible"
      :event="selectedEvent"
      @close="handleCloseModal"
      @save="handleSaveEvent"
      @delete="handleDeleteEvent"
    />
  </div>
</template>

<style>
.calendar-container {
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
}
</style>
