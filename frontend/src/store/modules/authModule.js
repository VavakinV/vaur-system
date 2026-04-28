import authApi from "@/api/auth"

export const authModule = {
    namespaced: true,
    state: () => ({
        accessToken: localStorage.getItem('access_token') || null,
        refreshToken: localStorage.getItem('refresh_token') || null,
        user: JSON.parse(localStorage.getItem('user')) || null,
    }),

    getters: {
        isAuthenticated: (state) => Boolean(state.accessToken),
        user: (state) => state.user,
        role: (state) => state.user?.role || null
    },

    mutations: {
        SET_AUTH(state, { access, refresh, user }) {
            state.accessToken = access;
            state.refreshToken = refresh;
            state.user = user;

            localStorage.setItem("access_token", access);
            localStorage.setItem("refresh_token", refresh);
            localStorage.setItem("user", JSON.stringify(user));
        },

        CLEAR_AUTH(state) {
            state.accessToken = null;
            state.refreshToken = null;
            state.user = null;

            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user");
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