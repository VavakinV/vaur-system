<!-- TODO: Доделать получение групп в выпадающий список и отправку ID группы в запросе -->

<template>
    <form class="auth-form" @submit.prevent="onSubmit">
        <h2 class="auth-form__title">Регистрация студента</h2>
        <p class="auth-form__subtitle">Заполните данные для создания аккаунта</p>

        <div class="auth-form__field">
            <label class="auth-form__label" for="last_name">Фамилия</label>
            <input
                id="last_name"
                v-model="localLastName"
                class="auth-form__input"
                type="text"
                placeholder="Иванов"
            />
        </div>

        <div class="auth-form__field">
            <label class="auth-form__label" for="first_name">Имя</label>
            <input
                id="first_name"
                v-model="localFirstName"
                class="auth-form__input"
                type="text"
                placeholder="Иван"
            />
        </div>

        <div class="auth-form__field">
            <label class="auth-form__label" for="middle_name">Отчество</label>
            <input
                id="middle_name"
                v-model="localMiddleName"
                class="auth-form__input"
                type="text"
                placeholder="Иванович"
            />
        </div>

        <div class="auth-form__field">
            <label class="auth-form__label" for="group_number">Группа</label>
            <input
                id="group_number"
                v-model="localGroupNumber"
                class="auth-form__input"
                type="text"
                placeholder="Ваша группа"
            />
        </div>

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

        <div class="auth-form__field">
            <label class="auth-form__label" for="password_confirm">Подтверждение пароля</label>
            <input
                id="password_confirm"
                v-model="localPasswordConfirm"
                class="auth-form__input"
                type="password"
                placeholder="Повторите пароль"
            />
        </div>

        <p v-if="localError || error" class="auth-form__error">
            {{ localError || error }}
        </p>

        <button class="auth-form__button" type="submit">
            Зарегистрироваться
        </button>

        <p class="auth-form__footer">Уже есть аккаунт?</p>
        <p class="auth-form__link-to-register" @click="$router.push('/')">
            Войти
        </p>
    </form>
</template>

<script>
export default {
    name: "RegistrationForm",

    props: {
        error: {
            type: String,
            default: ""
        }
    },

    emits: ["submit"],

    data() {
        return {
            localLastName: "",
            localFirstName: "",
            localMiddleName: "",
            localGroupNumber: "",
            localEmail: "",
            localPassword: "",
            localPasswordConfirm: "",
            localError: ""
        }
    },

    methods: {
        onSubmit() {
            this.localError = ""

            if (this.localPassword !== this.localPasswordConfirm) {
                this.localError = "Пароли не совпадают"
                return
            }

            this.$emit("submit", {
                last_name: this.localLastName,
                first_name: this.localFirstName,
                middle_name: this.localMiddleName,
                group_number: this.localGroupNumber,
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
    color: #011f4b;
}

.auth-form__input {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid #005b96;
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

.auth-form__link-to-register {
    font-size: 24px;
    color: #005b96;
    text-align: center;
    text-decoration: underline;
    cursor: pointer;
}
</style>