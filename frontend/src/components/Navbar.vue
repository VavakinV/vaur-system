<template>
  <nav class="navbar">
    <h1 class="logo" @click="$router.push('/')">Система ВАУР</h1>

    <div class="navbar__btns">
      <custom-button @click="$router.push('/works')">
        Мои работы
      </custom-button>
      
      <custom-button @click="$router.push('/')">
        Мои заявки
      </custom-button>

      <custom-button class="btn-logout" @click="handleLogout">
        Выйти
      </custom-button>
    </div>
  </nav>
</template>

<script>
import authApi from '@/api/auth';

export default {
  methods: {
    async handleLogout() {
      try {
        await authApi.logout();
        
        await this.$store.dispatch('auth/logout');

        this.$router.push('/login');
      } catch (e) {
        console.error("Ошибка при выходе из системы:", e);
      }
    }
  }
}
</script>

<style scoped>
.navbar {
  height: 80px; 
  background-color: #6497b1;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  font-size: 28px;
  font-weight: 800;
  cursor: pointer;
  color: #011f4b;
  margin: 0;
  transition: opacity 0.2s ease;
  user-select: none;
}

.logo:hover {
  opacity: 0.8;
}

.navbar__btns {
  display: flex;
  align-items: center;
  gap: 15px;
}

.btn-logout {
  background-color: #b16464 !important;
  border: 1px solid rgba(1, 31, 75, 0.2) !important;
}

.btn-logout:hover {
  background-color: #a05a5a !important;
}

@media (max-width: 600px) {
  .navbar {
    padding: 0 15px;
    height: auto;
    flex-direction: column;
    padding-bottom: 15px;
  }
  .logo {
    margin: 15px 0;
  }
  .navbar__btns {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>