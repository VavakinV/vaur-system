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
          <label>АВТОР РАБОТЫ</label>
          <router-link 
            v-if="work.student_id" 
            :to="`/profile/${work.student_id}`" 
            class="profile-link"
          >
            {{ work.student_full_name }}
          </router-link>
          <span v-else>{{ work.student_full_name }}</span>
        </div>

        <div class="info-item">
          <label>НАУЧНЫЙ РУКОВОДИТЕЛЬ</label>
          <router-link 
            v-if="work.supervisor_id" 
            :to="`/profile/${work.supervisor_id}`" 
            class="profile-link"
          >
            {{ work.supervisor_full_name }}
          </router-link>
          <span v-else>{{ work.supervisor_full_name }}</span>
        </div>

        <div class="info-item">
          <label>СТАТУС РАБОТЫ</label>
          <span class="status-mock">В процессе (уточняется)</span>
        </div>

        <div class="info-item">
          <label>СТАТУС НОРМОКОНТРОЛЯ</label>
          <span :class="['status-tag', work.norm_control_status]">
            {{ translateNormStatus(work.norm_control_status) }}
          </span>
        </div>
      </div>

      <hr class="file-divider" />

      <div class="file-section">
        <div class="info-item">
          <label>ФАЙЛ РАБОТЫ</label>
          <p v-if="work.has_document" class="file-link">
            Документ загружен
          </p>
          <p v-else class="file-none">Файл не загружен</p>
        </div>

        <input 
          type="file" 
          ref="fileInput" 
          style="display: none" 
          @change="handleFileChange"
        />
        
        <custom-button @click="$refs.fileInput.click()">
          Обновить файл
        </custom-button>
      </div>
    </div>

    <div v-else class="status-msg">Работа не найдена</div>
  </div>
</template>

<script>
import workApi from "@/api/work";

export default {
  props: ['id'],
  data() {
    return {
      work: null,
      loading: true
    };
  },
  methods: {
    async fetchWorkData() {
      this.loading = true;
      try {
        this.work = await workApi.getWorkById(this.id);

        // МОКОВЫЕ ДАННЫЕ, ДОБАВИТЬ НА БЭКЕ
        this.work.student_id = 2; 
        this.work.supervisor_id = 1;
      } catch (e) {
        console.error("Ошибка загрузки работы", e);
      } finally {
        this.loading = false;
      }
    },
    async handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) return;

      try {
        await workApi.uploadDocument(this.id, file);
        alert("Файл успешно обновлен");
        this.fetchWorkData();
      } catch (e) {
        alert("Ошибка при загрузке файла");
      }
    },
    translateNormStatus(status) {
      const statuses = {
        passed: "Пройден",
        failed: "Не пройден",
        pending: "На проверке"
      };
      return statuses[status] || "Неизвестно";
    }
  },
  watch: {
    id: {
      immediate: true,
      handler: 'fetchWorkData'
    }
  }
};
</script>

<style scoped>
.work-container {
  min-height: calc(100vh - 80px);
  background-color: #f3f6f4;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
}

.work-card {
  background: white;
  width: 100%;
  max-width: 800px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  text-align: left;
}

.work-topic {
  font-size: 28px;
  font-weight: bold;
  color: #011f4b;
  margin-bottom: 30px;
  line-height: 1.2;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 14px;
  color: #666666;
  font-weight: 500;
}

.info-item span, .info-item p {
  font-size: 18px;
  color: #000000;
  margin: 0;
}

.profile-link {
  font-size: 18px;
  color: #005B96 !important;
  text-decoration: underline;
  cursor: pointer;
  width: fit-content;
}

.profile-link:hover {
  color: #011f4b !important;
}

.file-divider {
  border: 0;
  border-top: 1px solid #EEEEEE;
  margin: 24px 0;
}

.file-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-tag.passed { color: #2e7d32; font-weight: 600; }
.status-tag.failed { color: #d32f2f; font-weight: 600; }

.status-msg {
  padding: 40px;
  color: #666;
}
</style>