import axios from "axios"

const API_URL = process.env.VUE_APP_API_URL || "http://127.0.0.1:8000"

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json"
    }
})

export default {

    // РАБОЧАЯ ВЕРСИЯ
    // async getUserById(id) {
    //     const response = await apiClient.get(`/users/${id}/`);
    //     return response.data;
    // },

    // МОКОВАЯ ВЕРСИЯ:
    async getUserById(id) {
        console.warn(`Запрос данных для пользователя с ID: ${id} (MOCK)`);
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    id: id,
                    username: "mock_user_" + id,
                    email: "student_" + id + "@example.com",
                    last_name: "Иванов",
                    first_name: "Иван",
                    middle_name: "Иванович",
                    contacts: "Телеграм: @ivan_student",
                    role: "student",
                    is_staff: false,
                    is_superuser: false
                });
            }, 500);
        });
    },

    // РАБОЧАЯ ВЕРСИЯ
    // async updateContacts(contacts) {
    //     const response = await apiClient.patch('/auth/me/', { contacts });
    //     return response.data;
    // },

    // МОКОВАЯ ВЕРСИЯ:
    async updateContacts(contacts) {
        console.warn("Обновление контактов (MOCK)...");
        return new Promise((resolve) => {
            setTimeout(() => {
                const currentUser = JSON.parse(localStorage.getItem('user')) || {};
                const updatedUser = { ...currentUser, contacts: contacts };
                resolve(updatedUser);
            }, 800);
        });
    }
};