import {createRouter, createWebHistory} from 'vue-router'
import store from '@/store'

import Login from '@/views/LoginView'
import Register from '@/views/RegisterView'
import Works from '@/views/WorksView'
import Forbidden from '@/views/ForbiddenView'
import Profile from '@/views/ProfileView.vue'
import Work from '@/views/WorkIdView.vue'
import Applications from '@/views/ApplicationsView.vue'
import ApplicationDetail from '@/views/ApplicationDetailView.vue'

const routes = [
    {
        path: "/",
        redirect: "/works",
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
        meta: {
            showNavbar: false
        }
    },
    {
        path: '/register',
        name: 'register',
        component: Register,
        meta: {
            showNavbar: false
        }
    },
    {
        path: '/works',
        name: 'works',
        component: Works,
        meta: {
            requiresAuth: true,
            roles: ["admin", "student", "teacher"]
        }
    },
    {
        path: '/profile/:id',
        name: 'profile',
        component: Profile,
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["admin", "student", "teacher"]
        },
        meta: {
            requiresAuth: true,
            roles: ["admin", "student", "teacher"]
        }
    },
    {
        path: '/work/:id',
        name: 'workDetail',
        component: Work,
        props: true
    },
    {
        path: '/applications',
        name: 'applications',
        component: Applications,
        meta: {
            requiresAuth: true,
            roles: ["student", "teacher"]
        }
    },
    {
        path: '/applications/:id',
        name: 'applicationDetail',
        component: ApplicationDetail,
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["student", "teacher"]
        }
    },
    {
        path: '/forbidden',
        name: 'forbidden',
        component: Forbidden,
    }
]

const router = createRouter({
    routes,
    history: createWebHistory()
})

router.beforeEach((to, from, next) => {
    // to and from are both route objects. must call `next`.
    const isAuthenticated = store.getters["auth/isAuthenticated"]
    const role = store.getters["auth/role"]

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
    const isPublic = to.matched.some((record) => record.meta.public)

    if (requiresAuth && !isAuthenticated) {
        next({
            name: "login",
            query: {
                redirect: to.fullPath
            }
        })
        return
    }

    if (to.name === "login" && isAuthenticated) {
        next(to.query.redirect || "/works")
        return
    }

    const allowedRoles = to.meta.roles
    if (allowedRoles && allowedRoles.length && !allowedRoles.includes(role)) {
        next({name: "forbidden"})
        return
    }

    next()
})

export default router