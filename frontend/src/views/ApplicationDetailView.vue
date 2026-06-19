<template>
  <div class="app-detail-container">
    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="request" class="detail-card">
      <h1 class="card-title">Заявка на руководство работы</h1>

      <div class="field">
        <div class="field-label">Тип работы</div>
        <div class="field-value">{{ request.type_name }}</div>
      </div>

      <div class="field">
        <div class="field-label">Тема работы</div>
        <div class="field-value">{{ request.topic }}</div>
      </div>

      <div class="field">
        <div class="field-label">Студент</div>
        <div class="field-value">
          <router-link :to="{ name: 'profile', params: { id: request.student_user_id } }">
            {{ request.student_name }}, группа {{ request.student_group }}
          </router-link>
        </div>
      </div>

      <div class="field">
        <div class="field-label">Научный руководитель</div>
        <div class="field-value">
          <router-link :to="{ name: 'profile', params: { id: request.teacher_user_id } }">
            {{ request.teacher_name }}, каф. {{ request.teacher_department_name }}
          </router-link>
        </div>
      </div>

      <div class="field">
        <div class="field-label">Статус заявки</div>
        <div class="field-value">
          <span :class="['status-text', request.status]">{{ statusLabel(request.status) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import applicationsApi from "@/api/applications";

export default {
  props: ['id'],
  data() {
    return {
      request: null,
      loading: true,
      error: null,
    };
  },
  methods: {
    async fetchRequest() {
      this.loading = true;
      this.error = null;
      try {
        this.request = await applicationsApi.getRequest(this.id);
      } catch (e) {
        this.error = 'Заявка не найдена или у вас нет доступа к ней.';
      } finally {
        this.loading = false;
      }
    },
    statusLabel(s) {
      return { pending: 'Ожидание', accepted: 'Принята', rejected: 'Отклонена' }[s] || s;
    },
  },
  watch: {
    id: { immediate: true, handler: 'fetchRequest' },
  },
};
</script>

<style scoped>
.app-detail-container {
  min-height: calc(100vh - 80px);
  background-color: #f3f6f4;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.detail-card {
  background: white;
  width: 100%;
  max-width: 560px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.card-title {
  color: #011f4b;
  font-size: 22px;
  margin: 0 0 30px;
}

.field {
  margin-bottom: 20px;
}

.field-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #999;
  margin-bottom: 4px;
}

.field-value {
  font-size: 16px;
  color: #222;
}

.field-value a {
  color: #6497b1;
  text-decoration: none;
}

.field-value a:hover {
  text-decoration: underline;
}

.status-text {
  font-weight: 600;
}

.status-text.pending  { color: #e09a2e; }
.status-text.accepted { color: #3a9c5f; }
.status-text.rejected { color: #c0392b; }

.loading,
.error {
  margin-top: 60px;
  font-size: 16px;
  color: #666;
}
</style>
