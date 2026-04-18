<template>
    <div class="login-page">
        <AuthorizationForm
            :error="error"
            @submit="onSubmit"
        />
    </div>
</template>

<script>
import AuthorizationForm from "@/components/AuthorizationForm.vue"

export default {
    name: "LoginView",

    components: {
        AuthorizationForm
    },

    data() {
        return {
            error: ""
        }
    },

    methods: {
        async onSubmit(credentials) {
            this.error = ""

            try {
                await this.$store.dispatch("auth/login", credentials)

                const redirect = this.$route.query.redirect || "/works"
                this.$router.replace(redirect)
            } catch (err) {
                this.error = err.message || "Ошибка авторизации"
            }
        }
    }
}
</script>

<style scoped>
.login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: #f3f6f4;
}
</style>