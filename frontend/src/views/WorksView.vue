<template>
  <div class="works-view">
    <h1 class="page-title">{{ role === 'teacher' ? 'Работы под моим руководством' : 'Мои работы' }}</h1>

    <div v-if="loading" class="empty-hint">Загрузка...</div>

    <div v-else-if="works.length === 0" class="empty-hint">Работ пока нет.</div>

    <div v-else class="table-container">
      <table class="works-table">
        <thead>
          <tr>
            <th>Тема</th>
            <th>Тип работы</th>
            <th v-if="role === 'teacher'">Студент</th>
            <th v-if="role === 'teacher'">Группа</th>
            <th v-if="role === 'student'">Руководитель</th>
            <th>Статус</th>
            <th>Файл</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="work in works" :key="work.id">
            <td data-label="Тема" class="topic-cell">
              <router-link :to="{ name: 'workDetail', params: { id: work.id } }">{{ work.topic }}</router-link>
            </td>
            <td data-label="Тип работы">{{ work.work_type_name }}</td>
            <td v-if="role === 'teacher'" data-label="Студент">{{ work.student_full_name }}</td>
            <td v-if="role === 'teacher'" data-label="Группа">{{ work.student_group }}</td>
            <td v-if="role === 'student'" data-label="Руководитель">{{ work.supervisor_full_name }}</td>
            <td data-label="Статус">
              <span :class="['status-badge', work.status]">{{ translateStatus(work.status) }}</span>
            </td>
            <td data-label="Файл">
              <custom-button
                v-if="work.has_document"
                size="small"
                @click="download(work)"
              >Скачать</custom-button>
              <span v-else class="no-file">Нет файла</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
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

export default {
  data() {
    return {
      works: [],
      loading: true,
    };
  },

  computed: {
    role() {
      return this.$store.getters['auth/role'];
    },
  },

  async created() {
    try {
      this.works = await workApi.getWorks();
    } catch (e) {
      console.error(e);
    } finally {
      this.loading = false;
    }
  },

  methods: {
    translateStatus(s) {
      return STATUS_LABELS[s] || s;
    },
    async download(work) {
      try {
        await workApi.downloadDocument(work.id, work.topic + '.docx');
      } catch (e) {
        alert('Ошибка при скачивании файла');
      }
    },
  },
};
</script>

<style scoped>
.works-view {
  min-height: calc(100vh - 80px);
  padding: 40px 32px;
  background: #f3f6f4;
}

.page-title {
  color: #011f4b;
  font-size: 24px;
  margin: 0 0 24px;
}

.empty-hint {
  color: #888;
  font-size: 16px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.works-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.works-table th,
.works-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #eee;
}

.works-table th {
  background: #fafafa;
  font-weight: 600;
  color: #666;
  font-size: 14px;
}

.topic-cell a {
  color: #4caf50;
  text-decoration: none;
  font-weight: 500;
}

.topic-cell a:hover {
  text-decoration: underline;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  white-space: nowrap;
}

.status-badge.done               { background: #e8f5e9; color: #2e7d32; }
.status-badge.not_sent           { background: #f5f5f5; color: #757575; }
.status-badge.in_progress        { background: #fff3e0; color: #ef6c00; }
.status-badge.student_edit       { background: #fff3e0; color: #ef6c00; }
.status-badge.supervisor_edit    { background: #fff3e0; color: #ef6c00; }
.status-badge.normcontroller_edit { background: #fce4ec; color: #c62828; }

.no-file {
  color: #999;
  font-size: 14px;
  font-style: italic;
}

@media (max-width: 768px) {
  .works-view { padding: 20px 16px; }

  .works-table thead { display: none; }

  .works-table,
  .works-table tbody,
  .works-table tr,
  .works-table td {
    display: block;
    width: 100%;
  }

  .works-table tr {
    margin-bottom: 12px;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 10px;
    background: #fff;
  }

  .works-table td {
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-bottom: 1px solid #f5f5f5;
  }

  .works-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 15px;
    width: 45%;
    white-space: nowrap;
    text-align: left;
    font-weight: 600;
    color: #666;
  }

  .topic-cell { text-align: right !important; }
}
</style>
