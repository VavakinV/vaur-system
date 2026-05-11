<template>
  <div class="profile-container">
    <div v-if="loading">Загрузка...</div>
    
    <div v-else-if="profileUser" class="profile-card">
      <div class="role-badge">{{ translateRole(profileUser.role) }}</div>

      <h1 class="profile-title">
        {{ isOwnProfile ? 'Мой профиль' : 'Профиль пользователя' }}
      </h1>

      <div class="profile-content">
        <div class="info-group">
          <label>ФИО</label>
          <p>{{ fullDisplayName }}</p>
        </div>

        <div class="info-group">
          <label>Email</label>
          <p>{{ profileUser.email }}</p>
        </div>

        <hr class="divider" />

        <div class="info-group">
          <label v-if="isTeacher">Информация о преподавателе</label>
          <label v-else>Контакты</label>
          
          <div v-if="!isEditing" class="contacts-display">
            <p>{{ profileUser.contacts || 'Нет информации' }}</p>
            
            <custom-button 
              v-if="isOwnProfile" 
              class="edit-btn" 
              @click="isEditing = true"
            >
              Редактировать контакты
            </custom-button>
          </div>


          <div v-else-if="isOwnProfile" class="contacts-edit">
            <textarea v-model="editedContacts" rows="4"></textarea>
            <div class="edit-actions">
              <custom-button @click="saveContacts">Сохранить</custom-button>
              <button class="cancel-link" @click="isEditing = false">Отмена</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else>Пользователь не найден</div>
  </div>
</template>

<script>
import userApi from "@/api/user";

export default {
  props: ['id'],
  data() {
    return {
        profileUser: null,
        isEditing: false,
        editedContacts: "",
        loading: true,
        isTeacher: false,
    };
  },
  computed: {
    currentUser() {
        return this.$store.getters["auth/user"];
    },
    isOwnProfile() {
        const authUser = this.$store.getters["auth/user"];
        if (!authUser || !this.id) return false;
        return String(authUser.id) === String(this.id);
    },
    fullDisplayName() {
        const u = this.profileUser;
        return `${u.full_name}`.trim();
    }
  },
  methods: {
    async fetchProfileData() {
        this.loading = true;
        try {
            this.profileUser = await userApi.getUserById(this.id);
        
            this.editedContacts = this.profileUser.contacts || "";
            this.isTeacher = this.profileUser.role === "teacher";
        } catch (e) {
            console.error("Ошибка загрузки профиля", e);
        } finally {
            this.loading = false;
        }
    },
    async saveContacts() {
        try {
            const updatedUser = await userApi.updateContacts(this.editedContacts);
            this.$store.commit("auth/SET_USER", updatedUser);
            this.profileUser = updatedUser;
            this.isEditing = false;
        } catch (e) {
            alert("Ошибка при сохранении");
        }
    },
    translateRole(role) {
        const roles = { student: "Студент", teacher: "Преподаватель" };
        return roles[role] || role;
    }
  },
  watch: {
    id: {
        immediate: true,
        handler: 'fetchProfileData'
    }
  }
};
</script>

<style scoped>
.profile-container {
    min-height: calc(100vh - 80px);
    background-color: #f3f6f4;
    padding: 40px 20px;
    display: flex;
    justify-content: center;
}

.profile-card {
    background: white;
    width: 100%;
    max-width: 600px;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}

.profile-title {
    color: #011f4b;
    margin-bottom: 30px;
    font-size: 24px;
}

.role-badge {
    position: absolute;
    top: 32px;
    right: -65px; 
    
    width: 240px; 
    
    background: #6497b1;
    color: white;
    padding: 8px 0;
    transform: rotate(45deg);
    text-align: center;
    
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    z-index: 1;
}

.role-badge.student { background: #64b182; }
.role-badge.teacher { background: #6497b1; }

.info-group {
    margin-bottom: 20px;
}

.info-group label {
    display: block;
    font-size: 13px;
    color: #888;
    margin-bottom: 4px;
    text-transform: uppercase;
    font-weight: 600;
}

.info-group p {
    font-size: 18px;
    color: #333;
    margin: 0;
}

.divider {
    border: 0;
    border-top: 1px solid #eee;
    margin: 30px 0;
}

.contacts-display {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.edit-btn {
    align-self: flex-start;
    font-size: 14px;
    background-color: #e0e0e0 !important;
    color: #333 !important;
}

textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: inherit;
    font-size: 16px;
    resize: vertical;
    outline: none;
    overflow-wrap: break-word;
}

textarea:focus {
    border-color: #6497b1;
}

.edit-actions {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 10px;
}

.cancel-link {
    background: none;
    border: none;
    color: #888;
    cursor: pointer;
    text-decoration: underline;
}

.cancel-link:hover {
    color: #333;
}
</style>