<template>
    <div class="register-page">
        <RegistrationForm
            :error="error"
            @submit="onSubmit"
        />
    </div>
</template>

<script>
import RegistrationForm from "@/components/RegistrationForm.vue"

export default {
    name: "RegisterView",

    components: {
        RegistrationForm
    },

    data() {
        return {
            error: ""
        }
    },

    methods: {
        buildUsername(email) {
            return email.trim().toLowerCase()
        },

        async onSubmit(formData) {
            this.error = ""

            formData.contacts = ""

            try {
                await this.$store.dispatch("auth/register", formData)

                const redirect = this.$route.query.redirect || "/works"
                this.$router.replace(redirect)
            } catch (err) {
                this.error = err.message || "Ошибка регистрации"
            }
        }
    }
}
</script>

<style scoped>
.register-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: #f3f6f4;
}
</style>