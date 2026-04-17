export default {
    // ЗАГЛУШКА, ЗАМЕНИТЬ НА AXIOS
    async login({email, password}) {
        if (email === "admin@test.com" && password === "123456"){
            return {
                token: "admin-token",
                user: {
                    id: 1,
                    name: "Admin",
                    role: "admin"
                }
            }
        }

        if (email === "user@test.com" && password === "123456"){
            return {
                token: "user-token",
                user: {
                    id: 2,
                    name: "User",
                    role: "student"
                }
            }
        }

        throw new Error("Неверный email/пароль")
    }
}