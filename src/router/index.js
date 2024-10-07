import { createRouter, createWebHistory } from 'vue-router';
import AppLogin from '../views/AppLogin.vue';


const routes = [
    {
        path: '/',
        name: 'Login',
        component: AppLogin
    },

];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('user');
    if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
        next('/');
    } else {
        next();
    }
});

// 如果需要在路由中进行验证或其他逻辑，请在此处添加

export default router;
