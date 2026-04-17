import authApi from "@/api/auth"

export const authModule = {
    namespaced: true,
    state: () => ({
        user: JSON.parse(localStorage.getItem('user')) || null,
        token: localStorage.getItem('token') || null,
    }),

    getters: {
        isAuthenticated: (state) => Boolean(state.user && state.token),
        user: (state) => state.user,
        role: (state) => state.user?.role || null
    },

    mutations: {
        SET_AUTH(state, {user, token}){
            state.user = user
            state.token = token

            localStorage.setItem("user", JSON.stringify(user))
            localStorage.setItem("token", token)
        },

        CLEAR_AUTH(state) {
            state.user = null
            state.token = null

            localStorage.removeItem("user")
            localStorage.removeItem("token")
        }
    },

    actions: {
        async login({commit}, credentials){
            const {user, token} = await authApi.login(credentials)
            commit("SET_AUTH", {user, token})
            return user
        },

        logout({commit}) {
            commit("CLEAR_AUTH")
        }
    }
}