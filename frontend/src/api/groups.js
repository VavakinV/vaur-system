import { apiClient } from "@/api/client";

export default {
    async getGroups() {
        const response = await apiClient.get('/groups/');
        return response.data;
    },
};
