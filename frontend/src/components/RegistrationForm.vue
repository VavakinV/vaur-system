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
                required
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
                required
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

        <div class="auth-form__field autocomplete-wrapper">
            <label class="auth-form__label" for="group_number">Группа</label>
            <input
                id="group_number"
                v-model="searchGroupText"
                class="auth-form__input"
                type="text"
                placeholder="Начните вводить или выберите из списка"
                autocomplete="off"
                required
                @focus="isDropdownOpen = true"
                @blur="closeDropdown"
                @input="onGroupInput"
            />
            
            <ul v-if="isDropdownOpen && filteredGroups.length" class="autocomplete-list">
                <li
                    v-for="group in filteredGroups"
                    :key="group.id"
                    class="autocomplete-item"
                    @mousedown.prevent="selectGroup(group)"
                >
                    {{ group.number }}
                </li>
            </ul>
        </div>

        <div class="auth-form__field">
            <label class="auth-form__label" for="email">Email</label>
            <input
                id="email"
                v-model="localEmail"
                class="auth-form__input"
                type="email"
                placeholder="name@example.com"
                required
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
                required
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
                required
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
import { apiClient } from "@/api/auth"

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
            localEmail: "",
            localPassword: "",
            localPasswordConfirm: "",
            localError: "",

            groups: [],
            searchGroupText: "",
            selectedGroupId: null,
            isDropdownOpen: false,
        }
    },

    computed: {
        filteredGroups() {
            if (!this.searchGroupText) {
                return this.groups
            }
            const lowerSearch = this.searchGroupText.toLowerCase()
            return this.groups.filter(group => 
                group.number.toLowerCase().includes(lowerSearch)
            )
        }
    },

    async mounted() {
        await this.fetchGroups()
    },

    methods: {
        async fetchGroups() {
            try {
                const response = await apiClient.get("/groups/")
                this.groups = response.data
            } catch (error) {
                console.error("Не удалось загрузить список групп:", error)
            }
        },

        onGroupInput() {
            this.selectedGroupId = null
            this.isDropdownOpen = true
        },

        selectGroup(group) {
            this.searchGroupText = group.number
            this.selectedGroupId = group.id
            this.isDropdownOpen = false
        },

        closeDropdown() {
            this.isDropdownOpen = false
        },

        onSubmit() {
            this.localError = ""

            if (this.localPassword !== this.localPasswordConfirm) {
                this.localError = "Пароли не совпадают"
                return
            }

            if (!this.selectedGroupId) {
                const exactMatch = this.groups.find(
                    g => g.number.toLowerCase() === this.searchGroupText.trim().toLowerCase()
                )
                if (exactMatch) {
                    this.selectedGroupId = exactMatch.id
                } else {
                    this.localError = "Пожалуйста, выберите существующую группу из списка"
                    return
                }
            }

            this.$emit("submit", {
                username: this.localEmail,
                email: this.localEmail,
                password: this.localPassword,
                last_name: this.localLastName,
                first_name: this.localFirstName,
                middle_name: this.localMiddleName,
                contacts: "",
                group_number: this.selectedGroupId
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

.autocomplete-wrapper {
    position: relative;
}

.autocomplete-list {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: 200px;
    overflow-y: auto;
    margin: 4px 0 0;
    padding: 0;
    background: #f3f6f4;
    border: 1px solid #005b96;
    border-radius: 12px;
    list-style: none;
    z-index: 10;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.autocomplete-item {
    padding: 12px 14px;
    font-size: 18px;
    color: #011f4b;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.autocomplete-item:hover {
    background-color: #d1e0e8;
}

/* Кастомизация скроллбара для выпадающего списка */
.autocomplete-list::-webkit-scrollbar {
    width: 8px;
}

.autocomplete-list::-webkit-scrollbar-track {
    background: #f3f6f4;
    border-radius: 12px;
}

.autocomplete-list::-webkit-scrollbar-thumb {
    background-color: #005b96;
    border-radius: 12px;
}
</style>