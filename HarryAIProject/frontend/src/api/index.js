import axios from 'axios';

const api = axios.create({
    baseURL: '/api', // 透過 Vite proxy 轉發到 http://127.0.0.1:5000/api
    headers: {
        'Content-Type': 'application/json'
    }
});

export default {
    getTasks() {
        return api.get('/tasks');
    },
    createTask(task) {
        return api.post('/tasks', task);
    },
    updateTask(id, updates) {
        return api.put(`/tasks/${id}`, updates);
    },
    deleteTask(id) {
        return api.delete(`/tasks/${id}`);
    }
};
