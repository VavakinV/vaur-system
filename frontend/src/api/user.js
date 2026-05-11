import { apiClient } from "@/api/auth";

export default {

    // РАБОЧАЯ ВЕРСИЯ
    // async getUserById(id) {
    //     const response = await apiClient.get(`/users/${id}/`);
    //     return response.data;
    // },

    // МОКОВАЯ ВЕРСИЯ
    async getUserById(id) {
        return {
            id: id,
            last_name: "Тестовый",
            first_name: "Студент",
            middle_name: "Иванович",
            email: "test@example.com",
            role: "student",
            contacts: "Бэкенд скоро починят, и здесь будут реальные контакты",
            group: { number: "ФИ41" }
        };
    },

    // РАБОЧАЯ ВЕРСИЯ
    // async updateContacts(contacts) {
    //     const response = await apiClient.patch('/users/me/', { contacts });
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
