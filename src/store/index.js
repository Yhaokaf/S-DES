import { createStore } from 'vuex';

export default createStore({
    state: {
        user: null
    },
    mutations: {
        SET_USER(state, user) {
            state.user = user
            localStorage.setItem('user', JSON.stringify(user))
        },
        CLEAR_USER(state) {
            state.user = null
            localStorage.removeItem('user')
        }
    },
    actions: {
        login({ commit }, user) {
            commit('SET_USER', user)
        },
        logout({ commit }) {
            commit('CLEAR_USER')
        }
    },
    getters: {
        isAuthenticated: state => !!state.user
    }
});
