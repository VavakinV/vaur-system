<template>
    <form class="auth-form" @submit.prevent="onSubmit">
        <h2 class="auth-form__title">Вход в систему</h2>
        <p class="auth-form__subtitle">Введите email и пароль для авторизации</p>

        <div class="auth-form__field">
            <label class="auth-form__label" for="email">Email</label>
            <input
                id="email"
                v-model="localEmail"
                class="auth-form__input"
                type="email"
                placeholder="name@example.com"
            />
        </div>

        <div class="auth-form__field">
            <label class="auth-form__label" for="password">Пароль</label>
            <input
                id="password"
                v-model="localPassword"
                class="auth-form__input"
                type="password"
                placeholder="Введите пароль"
            />
        </div>

        <p v-if="error" class="auth-form__error">{{ error }}</p>

        <button class="auth-form__button" type="submit">
            Войти
        </button>
        <p class="auth-form__footer">Нет аккаунта?</p>
        <p class="auth-form__link-to-register" @click="$router.push('/register')">Зарегистрироваться</p>
    </form>
</template>

<script>
export default {
    name: "AuthorizationForm",

    props: {
        error: {
            type: String,
            default: ""
        }
    },

    emits: ["submit"],

    data() {
        return {
            localEmail: "",
            localPassword: ""
        }
    },

    methods: {
        onSubmit() {
            this.$emit("submit", {
                email: this.localEmail,
                password: this.localPassword
            })
        }
    }
}
</script>

<style scoped>
.auth-form {
    width: 100%;
    max-width: 640px;
    padding: 32px;
    border-radius: 20px;
    background: #6497b1;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
}

.auth-form__title {
    margin: 0 0 8px;
    font-size: 48px;
    line-height: 1.2;
    color: #011f4b;
    text-align: center;
}

.auth-form__subtitle {
    margin: 0 0 24px;
    font-size: 24px;
    color: #03396c;
    text-align: center;
}

.auth-form__field {
    margin-bottom: 24px;
}

.auth-form__label {
    display: block;
    margin-bottom: 8px;
    margin-left: 4px;
    font-size: 24px;
    font-weight: 600;
    color:#011f4b;
}

.auth-form__input {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid#005b96;
    border-radius: 12px;
    background: #f3f6f4;
    font-size: 18px;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-sizing: border-box;
}

.auth-form__input:focus {
    border-color: #011f4b;
    box-shadow: 0 0 0 4px rgba(1, 31, 75, 0.15);
}

.auth-form__error {
    margin: 4px 0 16px;
    color: red;
    font-size: 18px;
}

.auth-form__button {
    width: 100%;
    padding: 12px 16px;
    border: none;
    border-radius: 12px;
    background: #005b96;
    color: #f3f6f4;
    font-size: 20px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.15s ease, opacity 0.2s ease;
}

.auth-form__button:hover {
    opacity: 0.9;
}

.auth-form__button:active {
    transform: scale(0.99);
}

.auth-form__footer {
    margin-top: 24px;
    font-size: 24px;
    color: #03396c;
    text-align: center;
}

.auth-form__link-to-register{
    font-size: 24px;
    color: #005b96;
    text-align: center;
    text-decoration: underline;
    cursor: pointer;
}
</style>