import { createRouter, createWebHistory } from 'vue-router'
import CalendarView from '../views/CalendarView.vue'
import KanbanView from '../views/KanbanView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'calendar',
      component: CalendarView
    },
    {
      path: '/kanban',
      name: 'board',
      component: KanbanView
    }
  ]
})

export default router
