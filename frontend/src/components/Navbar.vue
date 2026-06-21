<template>
    <nav class="navbar">
        <div class="navbar__inner">
        <div class="navbar__left">
              <h1 class="logo" @click="$router.push('/')">Система ВАУР</h1>
        </div>

        <div class="navbar__center">
            <span class="nav-link" @click="$router.push('/works')">Мои работы</span>
            <span class="nav-link" @click="$router.push('/applications')">Мои заявки</span>
        </div>

        <div class="navbar__right">
            <span 
                v-if="userId" 
                class="user-link nav-link" 
                @click="$router.push(`/profile/${userId}`)"
            >
               {{ userName }}
            </span>

            <custom-button class="btn-logout" @click="handleLogout">
                Выйти
            </custom-button>
        </div>
        </div><!-- /navbar__inner -->
    </nav>
</template>

<script>
import authApi from '@/api/auth';

export default {
  computed: {
    userId() {
      return this.$store.getters['auth/id'];
    },
    userName() {
      return this.$store.getters['auth/userName'];
    }
  },

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
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar__left, .navbar__right {
  flex: 1;
  display: flex;
  align-items: center;
}

.navbar__right {
  justify-content: flex-end;
  gap: 20px;
}

.navbar__center {
  display: flex;
  gap: 30px;
  justify-content: center;
}

.nav-link {
  color: #f3f6f4;
  font-size: 20px;
  font-weight: 500;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
  position: relative;
}

.nav-link:hover {
  opacity: 0.8;
}

.nav-link:after, 
.user-link:after{
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  display: block;
  margin-top: 2px;
  right: 0;
  transition: width 0.3s ease;
}

.nav-link:after {
  background: #f3f6f4;
}

.user-link:after {
  background: #011f4b !important;
}

.nav-link:hover:after,
.user-link:hover:after {
  width: 100%;
  left: 0;
  background: #f3f6f4;
}

.logo {
  font-size: 28px;
  font-weight: 800;
  cursor: pointer;
  color: #011f4b;
  margin: 0;
  transition: opacity 0.2s ease;
  user-select: none;
  white-space: nowrap;
}

.logo:hover {
  opacity: 0.8;
}

.user-link {
  font-size: 20px;
  color: #011f4b;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  user-select: none;
}

.btn-logout {
  background-color: #b16464 !important;
  border: 1px solid rgba(1, 31, 75, 0.2) !important;
}

.btn-logout:hover {
  background-color: #a05a5a !important;
}

@media (max-width: 900px) {
  .navbar__center {
    gap: 15px;
  }
}

@media (max-width: 768px) {
  .navbar {
    height: auto;
  }
  .navbar__inner {
    flex-direction: column;
    padding: 15px;
    gap: 15px;
    height: auto;
  }
  .navbar__left, .navbar__center, .navbar__right {
    flex: none;
    width: 100%;
    justify-content: center;
  }
}
</style>