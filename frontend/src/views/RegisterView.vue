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

            const payload = {
                username: this.buildUsername(formData.email),
                email: formData.email,
                password: formData.password,
                last_name: formData.last_name,
                first_name: formData.first_name,
                middle_name: formData.middle_name,
                contacts: "",
                group_number: 0
            }

            try {
                await this.$store.dispatch("auth/register", payload)

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