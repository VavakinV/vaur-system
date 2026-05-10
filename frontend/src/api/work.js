import { apiClient } from "@/api/auth";

export default {
    async getWorkById(id) {
        const response = await apiClient.get(`/works/${id}/`);
        return response.data;
    },
    async uploadDocument(id, file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await apiClient.post(`/works/${id}/document/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }
};