import { apiClient } from "@/api/auth";

export default {
    async getUserById(id) {
        const response = await apiClient.get(`/users/${id}/detail/`);
        return response.data;
    },

    async updateContacts(contacts) {
        const response = await apiClient.patch('/users/me/', { contacts });
        return response.data;
    },
};
