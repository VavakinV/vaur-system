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

    async getCorrections(workId) {
        const response = await apiClient.get(`/works/${workId}/corrections/`);
        return response.data;
    },

    async createCorrection(workId, items) {
        const response = await apiClient.post(`/works/${workId}/corrections/`, { items });
        return response.data;
    },

    async updateCorrection(correctionId, items) {
        const response = await apiClient.patch(`/works/corrections/${correctionId}/`, { items });
        return response.data;
    },

    async updateStatus(workId, status) {
        const response = await apiClient.patch(`/works/${workId}/status/`, { status });
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
