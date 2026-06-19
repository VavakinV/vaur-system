<template>
  <div class="applications-view">

    <!-- Student: empty state -->
    <template v-if="role === 'student' && !loading && requests.length === 0">
      <h1 class="page-title">Мои заявки</h1>
      <p class="empty-hint">У вас пока нет активных заявок. Подайте новую, чтобы приступить к вашей курсовой работе или ВКР!</p>
      <custom-button class="btn-submit" @click="openModal">Подать заявку</custom-button>
    </template>

    <!-- Student: list -->
    <template v-else-if="role === 'student' && !loading">
      <div class="page-header">
        <h1 class="page-title">Мои заявки</h1>
        <custom-button v-if="!hasPendingRequest" class="btn-submit" @click="openModal">Подать заявку</custom-button>
      </div>

      <div class="filters-bar">
        <select class="filter-select" v-model="filters.type_name">
          <option value="">Все типы работ</option>
          <option v-for="t in uniqueTypes" :key="t" :value="t">{{ t }}</option>
        </select>
        <select class="filter-select" v-model="filters.person">
          <option value="">Все руководители</option>
          <option v-for="p in uniquePersons" :key="p" :value="p">{{ p }}</option>
        </select>
        <select class="filter-select" v-model="filters.status">
          <option value="">Все статусы</option>
          <option v-for="s in uniqueStatuses" :key="s" :value="s">{{ statusLabel(s) }}</option>
        </select>
        <button v-if="hasActiveFilters" class="btn-reset" @click="resetFilters">✕ Сбросить</button>
      </div>
      <p v-if="hasActiveFilters" class="filter-count">Показано {{ displayedRequests.length }} из {{ requests.length }}</p>

      <div class="table-container">
        <div v-if="displayedRequests.length === 0" class="empty-filtered">Нет заявок, соответствующих фильтрам.</div>
        <table v-else class="requests-table">
          <thead>
            <tr>
              <th>Тема</th>
              <th class="sortable" @click="toggleSort('type_name')">
                <span class="th-inner">Тип работы <span :class="['sort-icon', { active: sort.key === 'type_name' }]">{{ sortIcon('type_name') }}</span></span>
              </th>
              <th class="sortable" @click="toggleSort('teacher_name')">
                <span class="th-inner">Руководитель <span :class="['sort-icon', { active: sort.key === 'teacher_name' }]">{{ sortIcon('teacher_name') }}</span></span>
              </th>
              <th class="sortable" @click="toggleSort('status')">
                <span class="th-inner">Статус <span :class="['sort-icon', { active: sort.key === 'status' }]">{{ sortIcon('status') }}</span></span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in displayedRequests" :key="req.id">
              <td data-label="Тема" class="topic-cell">
                <router-link :to="{ name: 'applicationDetail', params: { id: req.id } }">{{ req.topic }}</router-link>
              </td>
              <td data-label="Тип работы">{{ req.type_name }}</td>
              <td data-label="Руководитель">
                <router-link :to="{ name: 'profile', params: { id: req.teacher_user_id } }">{{ req.teacher_name }}</router-link>
              </td>
              <td data-label="Статус">
                <div class="status-cell">
                  <span :class="['status-badge', req.status]">{{ statusLabel(req.status) }}</span>
                  <button
                    v-if="req.status === 'pending'"
                    class="icon-btn"
                    title="Изменить заявку"
                    @click="openEditModal(req)"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Teacher: list -->
    <template v-else-if="role === 'teacher' && !loading">
      <h1 class="page-title">Отправленные мне заявки</h1>
      <div v-if="requests.length === 0" class="empty-hint">Входящих заявок пока нет.</div>
      <template v-else>
        <div class="filters-bar">
          <select class="filter-select" v-model="filters.type_name">
            <option value="">Все типы работ</option>
            <option v-for="t in uniqueTypes" :key="t" :value="t">{{ t }}</option>
          </select>
          <select class="filter-select" v-model="filters.person">
            <option value="">Все студенты</option>
            <option v-for="p in uniquePersons" :key="p" :value="p">{{ p }}</option>
          </select>
          <select class="filter-select" v-model="filters.student_group">
            <option value="">Все группы</option>
            <option v-for="g in uniqueGroups" :key="g" :value="g">{{ g }}</option>
          </select>
          <select class="filter-select" v-model="filters.status">
            <option value="">Все статусы</option>
            <option v-for="s in uniqueStatuses" :key="s" :value="s">{{ statusLabel(s) }}</option>
          </select>
          <button v-if="hasActiveFilters" class="btn-reset" @click="resetFilters">✕ Сбросить</button>
        </div>
        <p v-if="hasActiveFilters" class="filter-count">Показано {{ displayedRequests.length }} из {{ requests.length }}</p>

        <div class="table-container">
          <div v-if="displayedRequests.length === 0" class="empty-filtered">Нет заявок, соответствующих фильтрам.</div>
          <table v-else class="requests-table">
            <thead>
              <tr>
                <th>Тема</th>
                <th class="sortable" @click="toggleSort('type_name')">
                  <span class="th-inner">Тип работы <span :class="['sort-icon', { active: sort.key === 'type_name' }]">{{ sortIcon('type_name') }}</span></span>
                </th>
                <th class="sortable" @click="toggleSort('student_name')">
                  <span class="th-inner">Студент <span :class="['sort-icon', { active: sort.key === 'student_name' }]">{{ sortIcon('student_name') }}</span></span>
                </th>
                <th class="sortable" @click="toggleSort('student_group')">
                  <span class="th-inner">Группа <span :class="['sort-icon', { active: sort.key === 'student_group' }]">{{ sortIcon('student_group') }}</span></span>
                </th>
                <th class="sortable" @click="toggleSort('status')">
                  <span class="th-inner">Статус <span :class="['sort-icon', { active: sort.key === 'status' }]">{{ sortIcon('status') }}</span></span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in displayedRequests" :key="req.id">
                <td data-label="Тема" class="topic-cell">
                  <router-link :to="{ name: 'applicationDetail', params: { id: req.id } }">{{ req.topic }}</router-link>
                </td>
                <td data-label="Тип работы">{{ req.type_name }}</td>
                <td data-label="Студент">
                  <router-link :to="{ name: 'profile', params: { id: req.student_user_id } }">{{ req.student_name }}</router-link>
                </td>
                <td data-label="Группа">{{ req.student_group }}</td>
                <td data-label="Статус">
                  <div class="status-cell">
                    <span :class="['status-badge', req.status]">{{ statusLabel(req.status) }}</span>
                    <button
                      v-if="req.status === 'pending'"
                      class="icon-btn"
                      title="Изменить статус"
                      @click="openStatusModal(req)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>

    <div v-else-if="loading" class="loading">Загрузка...</div>

    <!-- Modal: submit new request (student) -->
    <div v-if="showSubmitModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <h2 class="modal-title">{{ editingRequest ? 'Изменить заявку' : 'Подать заявку' }}</h2>

        <label class="form-label">Кафедра</label>
        <select class="form-select" v-model="form.department_id" @change="onDepartmentChange">
          <option value="" disabled>Выберите кафедру</option>
          <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
        </select>

        <label class="form-label">Преподаватель</label>
        <select class="form-select" v-model="form.teacher" :disabled="!form.department_id || teachersLoading">
          <option value="" disabled>{{ teachersLoading ? 'Загрузка...' : 'Выберите преподавателя' }}</option>
          <option v-for="teacher in availableTeachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.full_name }}
          </option>
        </select>
        <p v-if="form.department_id && !teachersLoading && availableTeachers.length === 0" class="hint-text">
          На этой кафедре нет доступных преподавателей.
        </p>

        <label class="form-label">Тип работы</label>
        <select class="form-select" v-model="form.type">
          <option value="" disabled>Выберите тип работы</option>
          <option v-for="wt in workTypes" :key="wt.id" :value="wt.id">{{ wt.name }}</option>
        </select>

        <label class="form-label">Тема работы</label>
        <input
          class="form-input"
          type="text"
          v-model="form.topic"
          placeholder="Введите тему работы"
          maxlength="150"
        />

        <p v-if="submitError" class="error-text">{{ submitError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeModal">Отмена</button>
          <custom-button
            @click="submitRequest"
            :disabled="submitting || !formValid"
          >
            {{ submitting ? 'Отправка...' : (editingRequest ? 'Сохранить' : 'Отправить') }}
          </custom-button>
        </div>
      </div>
    </div>

    <!-- Modal: change status (teacher) -->
    <div v-if="showStatusModal" class="modal-backdrop" @click.self="closeStatusModal">
      <div class="modal modal--narrow">
        <h2 class="modal-title">Изменить статус заявки</h2>
        <p class="modal-desc">Тема: <strong>{{ selectedRequest?.topic }}</strong></p>
        <p v-if="statusError" class="error-text">{{ statusError }}</p>
        <div class="modal-actions modal-actions--status">
          <custom-button class="btn-reject btn-status-action" @click="changeStatus('rejected')" :disabled="statusUpdating">
            Отклонить
          </custom-button>
          <custom-button class="btn-status-action" @click="changeStatus('accepted')" :disabled="statusUpdating">
            Одобрить
          </custom-button>
          <button class="btn-cancel btn-status-cancel" @click="closeStatusModal">Отмена</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import applicationsApi from '@/api/applications';

export default {
  data() {
    return {
      requests: [],
      loading: true,

      sort: { key: null, dir: 'asc' },
      filters: { type_name: '', person: '', student_group: '', status: '' },

      departments: [],
      availableTeachers: [],
      teachersLoading: false,
      workTypes: [],

      showSubmitModal: false,
      editingRequest: null,
      form: { department_id: '', teacher: '', type: '', topic: '' },
      submitting: false,
      submitError: '',

      showStatusModal: false,
      selectedRequest: null,
      statusUpdating: false,
      statusError: '',
    };
  },

  computed: {
    role() {
      return this.$store.getters['auth/role'];
    },
    formValid() {
      return this.form.teacher && this.form.type && this.form.topic.trim();
    },
    hasPendingRequest() {
      return this.requests.some(r => r.status === 'pending');
    },

    uniqueTypes() {
      return [...new Set(this.requests.map(r => r.type_name).filter(Boolean))].sort();
    },
    uniquePersons() {
      const key = this.role === 'teacher' ? 'student_name' : 'teacher_name';
      return [...new Set(this.requests.map(r => r[key]).filter(Boolean))].sort();
    },
    uniqueGroups() {
      return [...new Set(this.requests.map(r => r.student_group).filter(Boolean))].sort();
    },
    uniqueStatuses() {
      return [...new Set(this.requests.map(r => r.status).filter(Boolean))];
    },
    hasActiveFilters() {
      return Object.values(this.filters).some(v => v !== '');
    },

    displayedRequests() {
      const STATUS_ORDER = { pending: 0, accepted: 1, rejected: 2 };
      const personKey = this.role === 'teacher' ? 'student_name' : 'teacher_name';

      let result = this.requests.filter(r => {
        if (this.filters.type_name && r.type_name !== this.filters.type_name) return false;
        if (this.filters.person && r[personKey] !== this.filters.person) return false;
        if (this.filters.student_group && r.student_group !== this.filters.student_group) return false;
        if (this.filters.status && r.status !== this.filters.status) return false;
        return true;
      });

      if (this.sort.key) {
        const key = this.sort.key;
        const dir = this.sort.dir === 'asc' ? 1 : -1;
        result = [...result].sort((a, b) => {
          if (key === 'status') {
            return dir * ((STATUS_ORDER[a.status] ?? 99) - (STATUS_ORDER[b.status] ?? 99));
          }
          return dir * String(a[key] || '').localeCompare(String(b[key] || ''), 'ru');
        });
      } else {
        result = [...result].sort((a, b) => (STATUS_ORDER[a.status] ?? 99) - (STATUS_ORDER[b.status] ?? 99));
      }

      return result;
    },
  },

  async created() {
    await this.loadRequests();
  },

  methods: {
    async loadRequests() {
      this.loading = true;
      try {
        this.requests = await applicationsApi.getRequests();
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },

    statusLabel(status) {
      const map = { pending: 'Ожидание', accepted: 'Одобрена', rejected: 'Отклонена' };
      return map[status] || status;
    },
    toggleSort(key) {
      if (this.sort.key === key) {
        this.sort.dir = this.sort.dir === 'asc' ? 'desc' : 'asc';
      } else {
        this.sort = { key, dir: 'asc' };
      }
    },
    sortIcon(key) {
      if (this.sort.key !== key) return '⇅';
      return this.sort.dir === 'asc' ? '▲' : '▼';
    },
    resetFilters() {
      this.filters = { type_name: '', person: '', student_group: '', status: '' };
    },

    async openModal() {
      this.form = { department_id: '', teacher: '', type: '', topic: '' };
      this.availableTeachers = [];
      this.submitError = '';
      try {
        [this.departments, this.workTypes] = await Promise.all([
          applicationsApi.getDepartments(),
          applicationsApi.getWorkTypes(),
        ]);
      } catch (e) {
        console.error(e);
      }
      this.showSubmitModal = true;
    },

    closeModal() {
      this.showSubmitModal = false;
      this.editingRequest = null;
    },

    async loadTeachersForDepartment(departmentId) {
      this.availableTeachers = [];
      if (!departmentId) return;
      this.teachersLoading = true;
      try {
        this.availableTeachers = await applicationsApi.getTeachersByDepartment(departmentId);
      } catch (e) {
        console.error(e);
      } finally {
        this.teachersLoading = false;
      }
    },

    async onDepartmentChange() {
      this.form.teacher = '';
      await this.loadTeachersForDepartment(this.form.department_id);
    },

    async openEditModal(req) {
      this.editingRequest = req;
      this.form = {
        department_id: req.teacher_department_id,
        teacher: '',
        type: req.type_id,
        topic: req.topic,
      };
      this.submitError = '';
      try {
        [this.departments, this.workTypes] = await Promise.all([
          applicationsApi.getDepartments(),
          applicationsApi.getWorkTypes(),
        ]);
        await this.loadTeachersForDepartment(req.teacher_department_id);
        // Ensure current teacher is selectable even if now at capacity
        if (!this.availableTeachers.some(t => t.id === req.teacher_id)) {
          this.availableTeachers.unshift({ id: req.teacher_id, full_name: req.teacher_name });
        }
        this.form.teacher = req.teacher_id;
      } catch (e) {
        console.error(e);
      }
      this.showSubmitModal = true;
    },

    async submitRequest() {
      if (!this.formValid || this.submitting) return;
      this.submitting = true;
      this.submitError = '';
      try {
        const payload = {
          teacher: this.form.teacher,
          type: this.form.type,
          topic: this.form.topic.trim(),
        };
        if (this.editingRequest) {
          const updated = await applicationsApi.updateRequest(this.editingRequest.id, payload);
          const idx = this.requests.findIndex(r => r.id === updated.id);
          if (idx !== -1) this.requests.splice(idx, 1, updated);
        } else {
          const created = await applicationsApi.createRequest(payload);
          this.requests.unshift(created);
        }
        this.closeModal();
      } catch (e) {
        this.submitError = e.response?.data?.detail || 'Ошибка при отправке заявки.';
      } finally {
        this.submitting = false;
      }
    },

    openStatusModal(req) {
      this.selectedRequest = req;
      this.statusError = '';
      this.showStatusModal = true;
    },

    closeStatusModal() {
      this.showStatusModal = false;
      this.selectedRequest = null;
    },

    async changeStatus(newStatus) {
      if (this.statusUpdating) return;
      this.statusUpdating = true;
      this.statusError = '';
      try {
        const updated = await applicationsApi.updateRequestStatus(this.selectedRequest.id, newStatus);
        const idx = this.requests.findIndex(r => r.id === updated.id);
        if (idx !== -1) this.requests.splice(idx, 1, updated);
        this.closeStatusModal();
      } catch (e) {
        this.statusError = e.response?.data?.detail || 'Ошибка при обновлении статуса.';
      } finally {
        this.statusUpdating = false;
      }
    },
  },
};
</script>

<style scoped>
.applications-view {
  min-height: 100vh;
  padding: 32px;
  background: #f3f6f4;
  font-family: sans-serif;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #011f4b;
  margin: 0 0 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header .page-title {
  margin: 0;
}

.empty-hint {
  color: #555;
  margin-bottom: 20px;
}

.btn-submit {
  min-width: 180px;
}

/* Filter bar */
.filters-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}

.filter-select {
  flex: 1 1 150px;
  max-width: 210px;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #333;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.filter-select:focus {
  border-color: #6497b1;
}

.btn-reset {
  padding: 8px 14px;
  border: 1px solid #e0b87a;
  border-radius: 6px;
  background: #fff8e8;
  color: #a05a00;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.btn-reset:hover {
  background: #ffeecf;
}

.filter-count {
  font-size: 13px;
  color: #888;
  margin: 0 0 10px;
}

.empty-filtered {
  padding: 24px 16px;
  color: #888;
  font-size: 15px;
}

/* Sortable headers */
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background: #f0f4f7;
}

.th-inner {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.sort-icon {
  font-size: 11px;
  color: #ccc;
  transition: color 0.15s;
}

.sort-icon.active {
  color: #6497b1;
}

/* Table */
.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
}

.requests-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.requests-table th,
.requests-table td {
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.requests-table th {
  background: #fafafa;
  font-weight: 600;
  color: #666;
}

.topic-cell {
  max-width: 360px;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Status badges */
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.status-badge.pending {
  background: #fff3e0;
  color: #ef6c00;
}

.status-badge.accepted {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.rejected {
  background: #fce4e4;
  color: #c62828;
}

/* Icon button */
.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6497b1;
  padding: 2px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.icon-btn:hover {
  color: #005b96;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.modal--narrow {
  max-width: 380px;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #011f4b;
  margin: 0 0 6px;
}

.modal-desc {
  font-size: 0.95rem;
  color: #444;
  margin: 0;
}

.form-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #555;
  margin-bottom: -4px;
}

.form-select,
.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #222;
  background: #fafafa;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}

.form-select:focus,
.form-input:focus {
  border-color: #6497b1;
  background: #fff;
}

.form-select:disabled {
  color: #aaa;
  cursor: not-allowed;
}

.hint-text {
  font-size: 0.82rem;
  color: #888;
  margin: -4px 0 0;
}

.error-text {
  font-size: 0.88rem;
  color: #c62828;
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
  margin-top: 6px;
}

.modal-actions .btn-cancel {
  margin-right: auto;
}

.modal-actions--status {
  flex-wrap: wrap;
}

.btn-status-action {
  flex: 1;
}

.btn-status-cancel {
  flex-basis: 100%;
  margin-right: 0;
  margin-left: auto;
  width: fit-content;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #c5c5c5;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 16px;
  font-weight: 400;
  color: #555;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.btn-cancel:hover {
  background: #f5f5f5;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-reject {
  background-color: #b16464 !important;
}

.btn-reject:hover {
  background-color: #a05a5a !important;
}

.loading {
  color: #888;
  font-size: 1rem;
  padding: 32px 0;
}

/* Responsive */
@media screen and (max-width: 768px) {
  .requests-table thead {
    display: none;
  }

  .requests-table,
  .requests-table tbody,
  .requests-table tr,
  .requests-table td {
    display: block;
    width: 100%;
  }

  .requests-table tr {
    margin-bottom: 15px;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 10px;
    background: #fff;
  }

  .requests-table td {
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-bottom: 1px solid #f9f9f9;
  }

  .requests-table td:last-child {
    border-bottom: 0;
  }

  .requests-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 15px;
    width: 45%;
    white-space: nowrap;
    text-align: left;
    font-weight: bold;
    color: #666;
  }

  .status-cell {
    justify-content: flex-end;
  }

  .modal {
    margin: 16px;
    padding: 24px 20px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .filter-select {
    flex: 1 1 calc(50% - 5px);
    max-width: none;
  }
}
</style>
