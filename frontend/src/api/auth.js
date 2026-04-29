import axios from "axios"
import { getApiBaseUrl } from "./baseUrl"

const API_URL = getApiBaseUrl()

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json"
    }
})

function getApiErrorMessage(error, fallback) {
    if (error.response) {
        if (error.response.data?.detail) {
            return error.response.data.detail
        }

        if (typeof error.response.data === "string") {
            return error.response.data
        }

        return fallback
    }

    if (error.request) {
        return "Нет соединения с сервером"
    }

    return `Ошибка: ${error.message}`
}

export default {
    async getUserData(accessToken) {
        const response = await apiClient.get("/auth/me/", {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        })

        return response.data
    },

    async login({ email, password }) {
        try {
            const response = await apiClient.post("/auth/login/", {
                email,
                password
            })

            return response.data
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error("Неверный email или пароль")
            }

            throw new Error(
                getApiErrorMessage(error, "Произошла ошибка при авторизации")
            )
        }
    },

    async register(payload) {
        try {
            const response = await apiClient.post("/auth/register/", payload)
            return response.data
        } catch (error) {
            if (error.response?.status === 400) {
                throw new Error(
                    getApiErrorMessage(error, "Некорректные данные для регистрации")
                )
            }

            throw new Error(
                getApiErrorMessage(error, "Произошла ошибка при регистрации")
            )
        }
    },

    async logout() {
        const refreshToken = localStorage.getItem("refresh_token")
        const accessToken = localStorage.getItem("access_token")

        if (refreshToken && accessToken) {
            try {
                await apiClient.post(
                    "/auth/logout/",
                    { refresh: refreshToken },
                    {
                        headers: {
                            Authorization: `Bearer ${accessToken}`
                        }
                    }
                )
            } catch (error) {
                if (error.response) {
                    if (error.response.status === 400) {
                        console.warn("Refresh токен недействителен или уже просрочен (400).")
                    } else if (error.response.status === 401) {
                        console.warn("Требуется авторизация или access токен просрочен (401).")
                    } else {
                        console.error("Неизвестная ошибка сервера при выходе:", error.response.data)
                    }
                } else {
                    console.error("Сетевая ошибка при запросе на выход:", error.message)
                }
            }
        }

        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
    }
}
