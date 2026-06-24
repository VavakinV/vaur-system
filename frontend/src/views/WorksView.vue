<template>
  <div class="works-view">
    <div class="page-inner">
    <h1 class="page-title">{{ role === 'teacher' ? 'Работы под моим руководством' : 'Мои работы' }}</h1>

    <div v-if="loading" class="empty-hint">Загрузка...</div>
    <div v-else-if="works.length === 0" class="empty-hint">Работ пока нет.</div>

    <template v-else>
      <div class="filters-bar">
        <select class="filter-select" v-model="filters.work_type_name" title="Тип работы">
          <option value="">Все типы работ</option>
          <option v-for="t in uniqueTypes" :key="t" :value="t">{{ t }}</option>
        </select>

        <select class="filter-select" v-model="filters.person" :title="role === 'teacher' ? 'Студент' : 'Руководитель'">
          <option value="">{{ role === 'teacher' ? 'Все студенты' : 'Все руководители' }}</option>
          <option v-for="p in uniquePersons" :key="p" :value="p">{{ p }}</option>
        </select>

        <select v-if="role === 'teacher'" class="filter-select" v-model="filters.student_group" title="Группа">
          <option value="">Все группы</option>
          <option v-for="g in uniqueGroups" :key="g" :value="g">{{ g }}</option>
        </select>

        <select class="filter-select" v-model="filters.status" title="Статус">
          <option value="">Все статусы</option>
          <option v-for="s in uniqueStatuses" :key="s" :value="s">{{ translateStatus(s) }}</option>
        </select>

        <button v-if="hasActiveFilters" class="btn-reset" @click="resetFilters">✕ Сбросить</button>
      </div>

      <p v-if="hasActiveFilters" class="filter-count">
        Показано {{ displayedWorks.length }} из {{ works.length }}
      </p>

      <div class="table-container">
        <div v-if="displayedWorks.length === 0" class="empty-filtered">
          Нет работ, соответствующих фильтрам.
        </div>
        <table v-else class="works-table">
          <thead>
            <tr>
              <th class="sortable" @click="toggleSort('topic')">
                <span class="th-inner">Тема <span :class="['sort-icon', { active: sort.key === 'topic' }]">{{ sortIcon('topic') }}</span></span>
              </th>
              <th class="sortable" @click="toggleSort('work_type_name')">
                <span class="th-inner">Тип работы <span :class="['sort-icon', { active: sort.key === 'work_type_name' }]">{{ sortIcon('work_type_name') }}</span></span>
              </th>
              <th v-if="role === 'teacher'" class="sortable" @click="toggleSort('student_full_name')">
                <span class="th-inner">Студент <span :class="['sort-icon', { active: sort.key === 'student_full_name' }]">{{ sortIcon('student_full_name') }}</span></span>
              </th>
              <th v-if="role === 'teacher'" class="sortable" @click="toggleSort('student_group')">
                <span class="th-inner">Группа <span :class="['sort-icon', { active: sort.key === 'student_group' }]">{{ sortIcon('student_group') }}</span></span>
              </th>
              <th v-if="role === 'student'" class="sortable" @click="toggleSort('supervisor_full_name')">
                <span class="th-inner">Руководитель <span :class="['sort-icon', { active: sort.key === 'supervisor_full_name' }]">{{ sortIcon('supervisor_full_name') }}</span></span>
              </th>
              <th class="sortable" @click="toggleSort('status')">
                <span class="th-inner">Статус <span :class="['sort-icon', { active: sort.key === 'status' }]">{{ sortIcon('status') }}</span></span>
              </th>
              <th>Файл</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="work in displayedWorks" :key="work.id">
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
                <custom-button v-if="work.has_document" size="small" @click="download(work)">
                  Скачать
                </custom-button>
                <span v-else class="no-file">Нет файла</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
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

const STATUS_ORDER = {
  not_sent: 0, in_progress: 1, student_edit: 2,
  supervisor_edit: 3, normcontroller_edit: 4, done: 5,
};

export default {
  data() {
    return {
      works: [],
      loading: true,
      sort: { key: null, dir: 'asc' },
      filters: { work_type_name: '', person: '', student_group: '', status: '' },
    };
  },

  computed: {
    role() {
      return this.$store.getters['auth/role'];
    },

    uniqueTypes() {
      return [...new Set(this.works.map(w => w.work_type_name).filter(Boolean))].sort();
    },
    uniquePersons() {
      const key = this.role === 'teacher' ? 'student_full_name' : 'supervisor_full_name';
      return [...new Set(this.works.map(w => w[key]).filter(Boolean))].sort();
    },
    uniqueGroups() {
      return [...new Set(this.works.map(w => w.student_group).filter(Boolean))].sort();
    },
    uniqueStatuses() {
      return [...new Set(this.works.map(w => w.status).filter(Boolean))];
    },

    hasActiveFilters() {
      return Object.values(this.filters).some(v => v !== '');
    },

    displayedWorks() {
      const personKey = this.role === 'teacher' ? 'student_full_name' : 'supervisor_full_name';

      let result = this.works.filter(w => {
        if (this.filters.work_type_name && w.work_type_name !== this.filters.work_type_name) return false;
        if (this.filters.person && w[personKey] !== this.filters.person) return false;
        if (this.filters.student_group && w.student_group !== this.filters.student_group) return false;
        if (this.filters.status && w.status !== this.filters.status) return false;
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
      }

      return result;
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
      this.filters = { work_type_name: '', person: '', student_group: '', status: '' };
    },
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
  background: #f3f6f4;
}

.page-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-title {
  color: #011f4b;
  font-size: 24px;
  margin: 0 0 20px;
}

.filters-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}

.filter-select {
  flex: 1 1 160px;
  max-width: 220px;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #333;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
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
  color: #555;
  font-size: 14px;
}

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

.status-badge.done                { background: #e8f5e9; color: #2e7d32; }
.status-badge.not_sent            { background: #f5f5f5; color: #757575; }
.status-badge.in_progress         { background: #fff3e0; color: #ef6c00; }
.status-badge.student_edit        { background: #fff3e0; color: #ef6c00; }
.status-badge.supervisor_edit     { background: #fff3e0; color: #ef6c00; }
.status-badge.normcontroller_edit { background: #fce4ec; color: #c62828; }

.no-file {
  color: #999;
  font-size: 14px;
  font-style: italic;
}

.empty-hint,
.empty-filtered {
  color: #888;
  font-size: 16px;
  padding: 20px 0;
}

.empty-filtered {
  padding: 24px;
}

@media (max-width: 768px) {
  .page-inner { padding: 20px 16px; }

  .filter-select {
    flex: 1 1 calc(50% - 5px);
    max-width: none;
  }

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
