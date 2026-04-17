<template>
    <div class="works-view">
        <h1>Works</h1>

        <p>Пользователь авторизован.</p>
        <p>Роль: {{ role }}</p>

        <custom-button @click="logout">Выйти</custom-button>
    </div>
</template>

<script>
export default {
    computed: {
        role() {
            return this.$store.getters["auth/role"]
        }
    },

    methods: {
        async logout() {
            await this.$store.dispatch("auth/logout")
            this.$router.push("/login")
        }
    }
}
</script>

<style scoped>
.works-view {
    min-height: 100vh;
    padding: 24px;
    background: #f3f6f4;
}
</style>