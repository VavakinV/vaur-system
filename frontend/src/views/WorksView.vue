<template>
  <div class="works-view">
    <div class="table-container">
      <table class="works-table">
        <thead>
          <tr>
            <th>Тема</th>
            <th v-if="role === 'student'">Руководитель</th>
            <th v-else>Студент</th>
            <th>Статус</th>
            <th>Файл</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="work in works" :key="work.id">
            <td data-label="Тема" class="theme-cell">
              <router-link :to="`/work/${work.id}`">{{ work.title }}</router-link>
            </td>
            
            <td :data-label="role === 'student' ? 'Руководитель' : 'Студент'">
              {{ role === 'student' ? work.advisor : work.student_name }}
            </td>
            
            <td data-label="Статус">
              <span :class="['status-badge', work.status_slug]">
                {{ work.status }}
              </span>
            </td>
            
            <td data-label="Файл">
              <custom-button 
                size="small" 
                @click="downloadFile(work.file_url)"
                v-if="work.file_url"
              >
                Скачать
              </custom-button>
              <span v-else class="no-file">Нет файла</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // ЗАМЕНИТЬ НА ОБРАЩЕНИЕ К API
      works: [
        {
          id: 1,
          title: "Разработка информационной системы для ВУЗа",
          advisor: "Иванов И.И.",
          student_name: "Петров П.П.",
          status: "В работе",
          status_slug: "in-progress",
          file_url: "#"
        },
        {
          id: 2,
          title: "Анализ алгоритмов шифрования в веб-приложениях",
          advisor: "Сидоров С.С.",
          student_name: "Васильев В.В.",
          status: "Завершено",
          status_slug: "completed",
          file_url: "#"
        }
      ]
    };
  },
  
  computed: {
    role() {
      return this.$store.getters["auth/role"];
    }
  },

  methods: {
    async logout() {
      await this.$store.dispatch("auth/logout");
      this.$router.push("/login");
    },
    downloadFile(url) {
      // Логика скачивания файла
      window.open(url, '_blank');
    }
  }
}
</script>

<style scoped>
.works-view {
  min-height: 100vh;
  padding: 32px;
  background: #f3f6f4;
  font-family: sans-serif;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
}

.works-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.works-table th, .works-table td {
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.works-table th {
  background: #fafafa;
  font-weight: 600;
  color: #666;
}

.theme-cell a {
  color: #4caf50;
  text-decoration: none;
  font-weight: 500;
}

.theme-cell a:hover {
  text-decoration: underline;
}

/* Стили для статусов */
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
}

.status-badge.in-progress {
  background: #fff3e0;
  color: #ef6c00;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.no-file {
  color: #999;
  font-size: 0.9rem;
  font-style: italic;
}

.logout-btn {
  background-color: #ff5252 !important;
}

@media screen and (max-width: 768px) {
  .works-table thead {
    display: none;
  }

  .works-table, .works-table tbody, .works-table tr, .works-table td {
    display: block;
    width: 100%;
  }

  .works-table tr {
    margin-bottom: 15px;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 10px;
    background: #fff;
  }

  .works-table td {
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-bottom: 1px solid #f9f9f9;
  }

  .works-table td:last-child {
    border-bottom: 0;
  }

  /* Вставляем название колонки перед данными */
  .works-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 15px;
    width: 45%;
    white-space: nowrap;
    text-align: left;
    font-weight: bold;
    color: #666;
  }

  .theme-cell {
    text-align: right !important;
  }
}
</style>