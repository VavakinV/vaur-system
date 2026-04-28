import authApi from "@/api/auth"

const safelyParseJSON = (data) => {
    try {
        return (data && data !== "undefined") ? JSON.parse(data) : null;
    } catch (e) {
        return null;
    }
};

export const authModule = {
    namespaced: true,
    state: () => {
        let savedUser = null;
        try {
            const userStr = localStorage.getItem('user');
            savedUser = userStr ? JSON.parse(userStr) : null;
        } catch (e) {
            localStorage.removeItem('user');
        }

        return {
            accessToken: localStorage.getItem('access_token') || null,
            refreshToken: localStorage.getItem('refresh_token') || null,
            user: savedUser,
        }
    },

    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        role: (state) => state.user?.role || null,
        userName: (state) => state.user ? `${state.user.first_name} ${state.user.last_name}` : 'Гость'
    },

    mutations: {
        SET_AUTH(state, { access, refresh }) {
            state.accessToken = access;
            state.refreshToken = refresh;
            localStorage.setItem("access_token", access);
            localStorage.setItem("refresh_token", refresh);
        },
        SET_USER(state, user) {
            state.user = user;
            localStorage.setItem("user", JSON.stringify(user));
        },
        CLEAR_AUTH(state) {
            state.accessToken = null;
            state.refreshToken = null;
            state.user = null;
            localStorage.clear();
        }
    },

    actions: {
        async login({ commit }, credentials) {
            const data = await authApi.login(credentials);

            commit("SET_AUTH", data);

            try {
                const user = await authApi.getUserData(data.access);
                commit("SET_USER", user);
                return user;
            } catch (error) {
                commit("CLEAR_AUTH");
                throw new Error("Ошибка получения профиля");
            }
        },

        async logout({ commit }) {
            try {
                await authApi.logout();
            } finally {
                commit("CLEAR_AUTH");
            }
        }
    }
}