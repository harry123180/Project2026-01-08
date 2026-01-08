import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import { setupCalendar, Calendar, DatePicker } from 'v-calendar';
import 'v-calendar/style.css';

const app = createApp(App)

// 初始化 Calendar 設定
app.use(setupCalendar, {})

// 明確註冊組件，這樣在 CalendarView.vue 裡寫 <VCalendar> 才能被認得
app.component('VCalendar', Calendar)
app.component('VDatePicker', DatePicker)

app.mount('#app')
