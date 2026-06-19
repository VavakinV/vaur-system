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
          <span :class="['status-work', work.status]">{{ translateStatus(work.status) }}</span>
        </div>

        <div class="info-item">
          <label>СТАТУС НОРМОКОНТРОЛЯ</label>
          <span :class="['status-norm', work.norm_control_status]">{{ translateNormStatus(work.norm_control_status) }}</span>
        </div>
      </div>

      <hr class="file-divider" />

      <div class="file-section">
        <div class="info-item">
          <label>ФАЙЛ РАБОТЫ</label>
          <a
            v-if="work.has_document"
            class="file-link"
            href="#"
            @click.prevent="download"
          >{{ work.document_original_name || 'document.docx' }}</a>
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
    };
  },
  methods: {
    async fetchWorkData() {
      this.loading = true;
      try {
        this.work = await workApi.getWorkById(this.id);
      } catch (e) {
        console.error('Ошибка загрузки работы', e);
      } finally {
        this.loading = false;
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

.file-divider {
  border: 0;
  border-top: 1px solid #eee;
  margin: 28px 0;
}

.file-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-link {
  font-size: 16px;
  color: #005b96;
  text-decoration: underline;
  cursor: pointer;
  width: fit-content;
}

.file-link:hover {
  color: #011f4b;
}

.file-none {
  color: #999;
  font-style: italic;
}

.status-msg {
  padding: 40px;
  color: #666;
  font-size: 16px;
}
</style>
