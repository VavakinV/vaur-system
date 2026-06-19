import { apiClient } from "@/api/client";

export default {
    async getRequests() {
        const response = await apiClient.get('/works/requests/');
        return response.data;
    },

    async getRequest(id) {
        const response = await apiClient.get(`/works/requests/${id}/`);
        return response.data;
    },

    async createRequest(data) {
        const response = await apiClient.post('/works/requests/', data);
        return response.data;
    },

    async updateRequestStatus(id, status) {
        const response = await apiClient.patch(`/works/requests/${id}/`, { status });
        return response.data;
    },

    async updateRequest(id, data) {
        const response = await apiClient.patch(`/works/requests/${id}/`, data);
        return response.data;
    },

    async getDepartments() {
        const response = await apiClient.get('/departments/');
        if (!Array.isArray(response.data)) {
            console.error('Unexpected /departments/ response:', response.data);
            return [];
        }
        return response.data;
    },

    async getTeachersByDepartment(departmentId) {
        const response = await apiClient.get(`/departments/${departmentId}/teachers/`);
        return response.data;
    },

    async getWorkTypes() {
        const response = await apiClient.get('/works/types/');
        return response.data;
    },
};
