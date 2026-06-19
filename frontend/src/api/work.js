import { apiClient } from "@/api/client";

export default {
    async getWorks() {
        const response = await apiClient.get('/works/');
        return response.data;
    },

    async getWorkById(id) {
        const response = await apiClient.get(`/works/${id}/detail/`);
        return response.data;
    },

    async uploadDocument(id, file) {
        const formData = new FormData();
        formData.append('document', file);
        const response = await apiClient.post(`/works/${id}/document/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    async downloadDocument(id, filename) {
        const response = await apiClient.get(`/works/${id}/document/`, {
            responseType: 'blob',
        });
        const url = URL.createObjectURL(response.data);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'document.docx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },
};
