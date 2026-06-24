<template>
  <div class="work-container">
    <div v-if="loading" class="status-msg">Загрузка данных...</div>

    <div v-else-if="work" class="work-card">
      <h1 class="work-topic">{{ work.topic }}</h1>

      <div class="info-list">
        <div class="info-item">
          <label>ТИП РАБОТЫ</label>
          <span>{{ work.work_type_name }}</span>
        </div>

        <div class="info-item">
          <label>АВТОР</label>
          <router-link
            :to="{ name: 'profile', params: { id: work.student_user_id } }"
            class="profile-link"
          >
            {{ work.student_full_name }}, группа {{ work.student_group }}
          </router-link>
        </div>

        <div class="info-item">
          <label>НАУЧНЫЙ РУКОВОДИТЕЛЬ</label>
          <router-link
            :to="{ name: 'profile', params: { id: work.supervisor_user_id } }"
            class="profile-link"
          >
            {{ work.supervisor_full_name }}, {{ work.department_name }}
          </router-link>
        </div>

        <div class="info-item">
          <label>СТАТУС РАБОТЫ</label>
          <div class="status-row">
            <span :class="['status-work', work.status]">{{ translateStatus(work.status) }}</span>
            <button
              v-if="isSupervisor && !editingStatus"
              class="btn-edit-status"
              @click="startEditStatus"
            >
              Изменить
            </button>
          </div>
          <div v-if="isSupervisor && editingStatus" class="status-edit-form">
            <select v-model="newStatus" class="status-select">
              <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
            <div class="status-edit-actions">
              <custom-button size="small" @click="saveStatus" :disabled="savingStatus">
                {{ savingStatus ? 'Сохранение...' : 'Сохранить' }}
              </custom-button>
              <button class="btn-cancel-edit" @click="cancelEditStatus">Отмена</button>
            </div>
            <p v-if="statusError" class="correction-error">{{ statusError }}</p>
          </div>
        </div>

        <div class="info-item">
          <label>СТАТУС НОРМОКОНТРОЛЯ</label>
          <span :class="['status-norm', work.norm_control_status]">{{ translateNormStatus(work.norm_control_status) }}</span>
        </div>
      </div>

      <hr class="section-divider" />

      <div class="file-section">
        <div class="info-item">
          <label>ФАЙЛ РАБОТЫ</label>
          <div v-if="work.has_document" class="file-row">
            <a class="file-link" href="#" @click.prevent="download">
              {{ work.document_original_name || 'document.docx' }}
            </a>
            <span v-if="work.document_updated_at" class="file-date">
              обновлён {{ formatDate(work.document_updated_at) }}
            </span>
          </div>
          <span v-else class="file-none">Файл не загружен</span>
        </div>

        <input
          type="file"
          ref="fileInput"
          accept=".docx"
          style="display: none"
          @change="handleFileChange"
        />

        <custom-button @click="$refs.fileInput.click()">Обновить файл</custom-button>
      </div>

      <hr class="section-divider" />

      <div class="corrections-section">
        <h2 class="section-label">ПРАВКИ</h2>

        <div v-if="correctionsLoading" class="corrections-msg">Загрузка...</div>

        <template v-else>
          <div v-if="corrections.length === 0" class="corrections-msg">Правок пока нет.</div>

          <div class="corrections-list">
            <div v-for="c in corrections" :key="c.id" class="correction-card">
              <div class="correction-meta">
                <span class="correction-author">{{ c.author_name }}</span>
                <span class="correction-date">{{ formatDate(c.created_at) }}</span>
              </div>

              <!-- Display mode -->
              <template v-if="editingCorrectionId !== c.id">
                <div class="correction-items">
                  <p v-for="(item, i) in c.items" :key="i" class="correction-item">{{ item }}</p>
                </div>
                <button
                  v-if="canEditCorrection(c)"
                  class="btn-edit-correction"
                  @click="startEdit(c)"
                >
                  Редактировать
                </button>
              </template>

              <!-- Edit mode -->
              <template v-else>
                <textarea
                  v-model="editText"
                  class="correction-textarea"
                  placeholder="Текст правки..."
                  rows="4"
                ></textarea>
                <p v-if="editError" class="correction-error">{{ editError }}</p>
                <div class="correction-edit-actions">
                  <custom-button size="small" @click="saveEdit(c)" :disabled="editSaving">
                    Сохранить
                  </custom-button>
                  <button class="btn-cancel-edit" @click="cancelEdit">Отмена</button>
                </div>
              </template>
            </div>
          </div>

          <div v-if="isSupervisor" class="add-correction-form">
            <h3 class="add-correction-title">Добавить правку</h3>
            <textarea
              v-model="newCorrectionText"
              class="correction-textarea"
              placeholder="Введите текст правки (каждая строка — отдельный пункт)..."
              rows="4"
            ></textarea>
            <p v-if="addError" class="correction-error">{{ addError }}</p>
            <custom-button
              @click="addCorrection"
              :disabled="addingCorrection || !newCorrectionText.trim()"
            >
              {{ addingCorrection ? 'Добавление...' : 'Добавить правку' }}
            </custom-button>
          </div>
        </template>
      </div>
    </div>

    <div v-else class="status-msg">Работа не найдена</div>
  </div>
</template>

<script>
import workApi from "@/api/work";

const STATUS_LABELS = {
  done: 'Сдана',
  not_sent: 'Не отправлена',
  in_progress: 'В работе',
  student_edit: 'Правки от студента',
  supervisor_edit: 'Правки от руководителя',
  normcontroller_edit: 'Правки от нормоконтролера',
};

const NORM_STATUS_LABELS = {
  passed: 'Пройден',
  needs_changes: 'Есть исправления',
  pending: 'В ожидании',
  not_sent: 'Не отправлена',
};

export default {
  props: ['id'],

  data() {
    return {
      work: null,
      loading: true,
      corrections: [],
      correctionsLoading: false,
      newCorrectionText: '',
      addingCorrection: false,
      addError: '',
      editingCorrectionId: null,
      editText: '',
      editError: '',
      editSaving: false,
      editingStatus: false,
      newStatus: null,
      savingStatus: false,
      statusError: '',
    };
  },

  computed: {
    currentUserId() {
      return this.$store.getters['auth/id'];
    },
    role() {
      return this.$store.getters['auth/role'];
    },
    isSupervisor() {
      return (
        this.role === 'teacher' &&
        this.work !== null &&
        this.currentUserId === this.work.supervisor_user_id
      );
    },
    statusOptions() {
      return Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }));
    },
  },

  methods: {
    async fetchWorkData() {
      this.loading = true;
      try {
        this.work = await workApi.getWorkById(this.id);
        await this.fetchCorrections();
      } catch (e) {
        console.error('Ошибка загрузки работы', e);
      } finally {
        this.loading = false;
      }
    },

    async fetchCorrections() {
      this.correctionsLoading = true;
      try {
        this.corrections = await workApi.getCorrections(this.id);
      } catch (e) {
        console.error('Ошибка загрузки правок', e);
      } finally {
        this.correctionsLoading = false;
      }
    },

    async handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) return;
      try {
        await workApi.uploadDocument(this.id, file);
        await this.fetchWorkData();
      } catch (e) {
        alert('Ошибка при загрузке файла');
      }
    },

    async download() {
      try {
        await workApi.downloadDocument(this.id, this.work.document_original_name);
      } catch (e) {
        alert('Ошибка при скачивании файла');
      }
    },

    async addCorrection() {
      const text = this.newCorrectionText.trim();
      if (!text) return;
      const items = text.split('\n').map(s => s.trim()).filter(Boolean);
      if (!items.length) return;
      this.addingCorrection = true;
      this.addError = '';
      try {
        const correction = await workApi.createCorrection(this.id, items);
        this.corrections.push(correction);
        this.newCorrectionText = '';
      } catch (e) {
        this.addError = e.response?.data?.detail || 'Ошибка при добавлении правки';
      } finally {
        this.addingCorrection = false;
      }
    },

    startEdit(correction) {
      this.editingCorrectionId = correction.id;
      this.editText = correction.items.join('\n');
      this.editError = '';
    },

    cancelEdit() {
      this.editingCorrectionId = null;
      this.editText = '';
      this.editError = '';
    },

    async saveEdit(correction) {
      const text = this.editText.trim();
      if (!text) return;
      const items = text.split('\n').map(s => s.trim()).filter(Boolean);
      if (!items.length) return;
      this.editSaving = true;
      this.editError = '';
      try {
        const updated = await workApi.updateCorrection(correction.id, items);
        const idx = this.corrections.findIndex(c => c.id === correction.id);
        if (idx !== -1) this.corrections.splice(idx, 1, updated);
        this.cancelEdit();
      } catch (e) {
        this.editError = e.response?.data?.detail || 'Ошибка при сохранении';
      } finally {
        this.editSaving = false;
      }
    },

    canEditCorrection(correction) {
      return this.currentUserId === correction.author_user_id;
    },

    formatDate(dt) {
      return new Date(dt).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    },

    startEditStatus() {
      this.newStatus = this.work.status;
      this.editingStatus = true;
      this.statusError = '';
    },

    cancelEditStatus() {
      this.editingStatus = false;
      this.newStatus = null;
      this.statusError = '';
    },

    async saveStatus() {
      if (this.savingStatus || !this.newStatus) return;
      this.savingStatus = true;
      this.statusError = '';
      try {
        const result = await workApi.updateStatus(this.id, this.newStatus);
        this.work = { ...this.work, status: result.status };
        this.cancelEditStatus();
      } catch (e) {
        this.statusError = e.response?.data?.detail || 'Ошибка при обновлении статуса';
      } finally {
        this.savingStatus = false;
      }
    },

    translateStatus(s) {
      return STATUS_LABELS[s] || s;
    },

    translateNormStatus(s) {
      return NORM_STATUS_LABELS[s] || s;
    },
  },

  watch: {
    id: { immediate: true, handler: 'fetchWorkData' },
  },
};
</script>

<style scoped>
.work-container {
  min-height: calc(100vh - 80px);
  background-color: #f3f6f4;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.work-card {
  background: white;
  width: 100%;
  max-width: 800px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.work-topic {
  font-size: 26px;
  font-weight: bold;
  color: #011f4b;
  margin: 0 0 30px;
  line-height: 1.3;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #999;
}

.info-item span,
.info-item p {
  font-size: 16px;
  color: #222;
  margin: 0;
}

.profile-link {
  font-size: 16px;
  color: #005b96;
  text-decoration: underline;
  width: fit-content;
}

.profile-link:hover {
  color: #011f4b;
}

.status-work,
.status-norm {
  font-size: 16px;
  font-weight: 600;
}

.status-work.done               { color: #2e7d32; }
.status-work.not_sent           { color: #757575; }
.status-work.in_progress        { color: #ef6c00; }
.status-work.student_edit       { color: #ef6c00; }
.status-work.supervisor_edit    { color: #ef6c00; }
.status-work.normcontroller_edit { color: #c62828; }

.status-norm.passed        { color: #2e7d32; }
.status-norm.needs_changes { color: #c62828; }
.status-norm.pending       { color: #ef6c00; }
.status-norm.not_sent      { color: #757575; }

.section-divider {
  border: 0;
  border-top: 1px solid #eee;
  margin: 28px 0;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-edit-status {
  background: none;
  border: 1px solid #6497b1;
  border-radius: 4px;
  color: #6497b1;
  font-size: 12px;
  padding: 2px 10px;
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
}

.btn-edit-status:hover {
  background: #e8f0f5;
}

.status-edit-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 6px;
}

.status-select {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #333;
  outline: none;
  max-width: 280px;
  cursor: pointer;
}

.status-select:focus {
  border-color: #6497b1;
}

.status-edit-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.file-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.file-link {
  font-size: 16px;
  color: #005b96;
  text-decoration: underline;
  cursor: pointer;
}

.file-link:hover {
  color: #011f4b;
}

.file-date {
  font-size: 12px;
  color: #aaa;
  white-space: nowrap;
}

.file-none {
  color: #999;
  font-style: italic;
}


.corrections-section {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.section-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #999;
  margin: 0 0 16px;
}

.corrections-msg {
  font-size: 14px;
  color: #999;
  font-style: italic;
  margin-bottom: 16px;
}

.corrections-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 8px;
}

.correction-card {
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
}

.correction-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.correction-author {
  font-weight: 600;
  font-size: 14px;
  color: #011f4b;
}

.correction-date {
  font-size: 12px;
  color: #aaa;
}

.correction-items {
  margin-bottom: 10px;
}

.correction-item {
  font-size: 15px;
  color: #333;
  margin: 0 0 4px;
  padding-left: 14px;
  position: relative;
  line-height: 1.5;
}

.correction-item::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #6497b1;
}

.btn-edit-correction {
  background: none;
  border: 1px solid #6497b1;
  border-radius: 4px;
  color: #6497b1;
  font-size: 13px;
  padding: 4px 12px;
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
}

.btn-edit-correction:hover {
  background: #e8f0f5;
}

.correction-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
  margin-bottom: 10px;
  line-height: 1.5;
}

.correction-textarea:focus {
  border-color: #6497b1;
}

.correction-edit-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-cancel-edit {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  font-size: 13px;
  padding: 4px 14px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s;
}

.btn-cancel-edit:hover {
  background: #f5f5f5;
}

.correction-error {
  color: #c62828;
  font-size: 13px;
  margin: 0 0 8px;
}

.add-correction-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.add-correction-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.status-msg {
  padding: 40px;
  color: #666;
  font-size: 16px;
}
</style>
