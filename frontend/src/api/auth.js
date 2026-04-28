//  export default {
//     // ЗАГЛУШКА, ЗАМЕНИТЬ НА AXIOS
//     async login({email, password}) {

//         if (email === "admin@test.com" && password === "123456"){
//             return {
//                 token: "admin-token",
//                 user: {
//                     id: 1,
//                     name: "Admin",
//                     role: "admin"
//                 }
//             }
//         }

//         if (email === "user@test.com" && password === "123456"){
//             return {
//                 token: "user-token",
//                 user: {
//                     id: 2,
//                     name: "User",
//                     role: "student"
//                 }
//             }
//         }

//         throw new Error("Неверный email/пароль")
//     }
// }




import axios from 'axios';

const API_URL = process.env.VUE_APP_API_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

export default {
    async login({ email, password }) {
        try {
            const response = await apiClient.post('/auth/login/', {
                email: email,
                password: password
            });

            const { access, refresh } = response.data;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);

            return {
                access,
                refresh
            };

        } catch (error) {
            if (error.response) {
                if (error.response.status === 401) {
                    throw new Error("Неверный email или пароль");
                }
                throw new Error(error.response.data.detail || "Произошла ошибка при авторизации");
            } else if (error.request) {
                throw new Error("Нет соединения с сервером");
            } else {
                throw new Error("Ошибка: " + error.message);
            }
        }
    },

    async logout() {
        const refreshToken = localStorage.getItem('refresh_token');
        const accessToken = localStorage.getItem('access_token');

        if (refreshToken && accessToken) {
            try {
                await apiClient.post(
                    '/auth/logout/',
                    { refresh: refreshToken },
                    {
                        headers: {
                            Authorization: `Bearer ${accessToken}`
                        }
                    }
                );
            } catch (error) {
                if (error.response) {
                    if (error.response.status === 400) {
                        console.warn("Refresh токен недействителен или уже просрочен (400).");
                    } else if (error.response.status === 401) {
                        console.warn("Требуется авторизация или access токен просрочен (401).");
                    } else {
                        console.error("Неизвестная ошибка сервера при выходе:", error.response.data);
                    }
                } else {
                    console.error("Сетевая ошибка при запросе на выход:", error.message);
                }
            }
        }

        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    async getUserData(accessToken) {
        const response = await apiClient.get('/auth/me/', {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });
        return response.data;
    }
}